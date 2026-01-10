#!/usr/bin/env python3

"""
Plugin System - Extensible plugin framework for Server Monitor
Provides hooks for plugins to respond to system events
"""

import os
import sys
import importlib.util
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import traceback
from abc import ABC, abstractmethod

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from event_model import Event
from observability import StructuredLogger


logger = StructuredLogger("plugin_system")


class PluginInterface(ABC):
    """
    Base interface for all plugins

    Plugins must implement this interface to be loaded by the system.
    All hook methods are optional - implement only what you need.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with optional configuration

        Args:
            config: Plugin-specific configuration dict
        """
        self.config = config or {}
        self.enabled = True
        self.name = self.__class__.__name__

    def on_startup(self, ctx: Dict[str, Any]) -> None:
        """
        Called when the server starts up

        Args:
            ctx: Startup context with server info
        """
        pass

    def on_shutdown(self) -> None:
        """Called when the server shuts down"""
        pass

    def on_event(self, event: Event) -> None:
        """
        Called for every event in the system

        Args:
            event: Event object with event details
        """
        pass

    def on_audit_log(self, event: Event) -> None:
        """
        Called when an audit log is created

        Args:
            event: Event object representing the audit log
        """
        pass

    def on_task_created(self, event: Event) -> None:
        """
        Called when a task is created

        Args:
            event: Event with task details in meta
        """
        pass

    def on_task_finished(self, event: Event) -> None:
        """
        Called when a task finishes (success or failure)

        Args:
            event: Event with task result in meta
        """
        pass

    def on_inventory_collected(self, event: Event) -> None:
        """
        Called when inventory is collected for a server

        Args:
            event: Event with inventory snapshot in meta
        """
        pass

    def on_alert(self, event: Event) -> None:
        """
        Called when an alert is triggered

        Args:
            event: Event with alert details in meta
        """
        pass

    def on_server_status_changed(self, event: Event) -> None:
        """
        Called when a server status changes

        Args:
            event: Event with old/new status in meta
        """
        pass


class PluginManager:
    """
    Manages plugin lifecycle and event dispatching

    Features:
    - Allowlist-based plugin loading (security by default)
    - Fail-safe execution (plugin errors don't crash core)
    - Event routing to registered plugins
    - Plugin enable/disable support
    """

    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.enabled = os.environ.get("PLUGINS_ENABLED", "false").lower() == "true"
        self.allowlist = self._parse_allowlist()
        self.plugins_dir = Path(__file__).parent / "plugins"

        logger.info(
            "Plugin system initialized",
            enabled=self.enabled,
            allowlist=self.allowlist,
            plugins_dir=str(self.plugins_dir),
        )

    def _parse_allowlist(self) -> List[str]:
        """Parse PLUGINS_ALLOWLIST environment variable"""
        allowlist_str = os.environ.get("PLUGINS_ALLOWLIST", "")
        if not allowlist_str:
            return []
        return [p.strip() for p in allowlist_str.split(",") if p.strip()]

    def load_plugins(self) -> None:
        """
        Load plugins from plugins directory

        Only loads plugins in the allowlist for security.
        Each plugin must be explicitly enabled.
        """
        if not self.enabled:
            logger.info("Plugin system disabled")
            return

        if not self.allowlist:
            logger.warning("Plugin system enabled but allowlist is empty")
            return

        if not self.plugins_dir.exists():
            logger.warning("Plugins directory does not exist", path=str(self.plugins_dir))
            return

        for plugin_name in self.allowlist:
            try:
                self._load_plugin(plugin_name)
            except Exception as e:
                logger.error(f"Failed to load plugin: {plugin_name}", error=str(e), traceback=traceback.format_exc())

    def _load_plugin(self, plugin_name: str) -> None:
        """
        Load a single plugin by name

        Args:
            plugin_name: Name of the plugin (without .py extension)
        """
        plugin_path = self.plugins_dir / f"{plugin_name}.py"

        if not plugin_path.exists():
            logger.error(f"Plugin file not found: {plugin_name}", path=str(plugin_path))
            return

        # Load module dynamically
        spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", plugin_path)
        if not spec or not spec.loader:
            logger.error(f"Failed to load plugin spec: {plugin_name}")
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"plugins.{plugin_name}"] = module
        spec.loader.exec_module(module)

        # Find plugin class (must inherit from PluginInterface)
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                plugin_class = attr
                break

        if not plugin_class:
            logger.error(f"No PluginInterface subclass found in: {plugin_name}")
            return

        # Get plugin config from environment
        config_key = f"PLUGIN_{plugin_name.upper()}_CONFIG"
        config_str = os.environ.get(config_key, "{}")
        config = {}
        if config_str:
            try:
                import json

                config = json.loads(config_str)
            except:
                logger.warning(f"Failed to parse plugin config: {plugin_name}", config_key=config_key)

        # Instantiate plugin
        plugin = plugin_class(config=config)
        self.plugins[plugin_name] = plugin

        logger.info(f"Plugin loaded: {plugin_name}", plugin_class=plugin_class.__name__, enabled=plugin.enabled)

    def dispatch_event(self, event: Event) -> None:
        """
        Dispatch event to all registered plugins

        Args:
            event: Event to dispatch

        Note: Plugin errors are caught and logged, but don't affect system operation
        """
        if not self.enabled or not self.plugins:
            return

        for plugin_name, plugin in self.plugins.items():
            if not plugin.enabled:
                continue

            try:
                # Call generic event handler
                plugin.on_event(event)

                # Call specific event handlers based on event type
                self._dispatch_specific_event(plugin, event)

            except Exception as e:
                logger.error(
                    f"Plugin error: {plugin_name}",
                    event_type=event.event_type,
                    error=str(e),
                    traceback=traceback.format_exc(),
                    service=f"plugin:{plugin_name}",
                )

    def _dispatch_specific_event(self, plugin: PluginInterface, event: Event) -> None:
        """
        Route event to specific handler methods based on event type

        Args:
            plugin: Plugin instance
            event: Event to dispatch
        """
        event_type = event.event_type

        # Map event types to handler methods
        if event_type.startswith("task.created"):
            plugin.on_task_created(event)
        elif event_type.startswith("task.finished") or event_type.startswith("task.failed"):
            plugin.on_task_finished(event)
        elif event_type.startswith("inventory."):
            plugin.on_inventory_collected(event)
        elif event_type.startswith("alert."):
            plugin.on_alert(event)
        elif event_type.startswith("server.status"):
            plugin.on_server_status_changed(event)

        # Always call audit log handler for audit events
        if event.action:  # Has audit action
            plugin.on_audit_log(event)

    def startup(self, ctx: Optional[Dict[str, Any]] = None) -> None:
        """
        Notify plugins of system startup

        Args:
            ctx: Optional startup context
        """
        if not self.enabled:
            return

        ctx = ctx or {}
        for plugin_name, plugin in self.plugins.items():
            if not plugin.enabled:
                continue

            try:
                plugin.on_startup(ctx)
                logger.info(f"Plugin startup: {plugin_name}", service=f"plugin:{plugin_name}")
            except Exception as e:
                logger.error(f"Plugin startup error: {plugin_name}", error=str(e), service=f"plugin:{plugin_name}")

    def shutdown(self) -> None:
        """Notify plugins of system shutdown"""
        if not self.enabled:
            return

        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.on_shutdown()
                logger.info(f"Plugin shutdown: {plugin_name}", service=f"plugin:{plugin_name}")
            except Exception as e:
                logger.error(f"Plugin shutdown error: {plugin_name}", error=str(e), service=f"plugin:{plugin_name}")


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.load_plugins()
    return _plugin_manager


def dispatch_event(event: Event) -> None:
    """
    Dispatch event to plugin system

    Convenience function for dispatching events from anywhere in the codebase.

    Args:
        event: Event to dispatch
    """
    manager = get_plugin_manager()
    manager.dispatch_event(event)
