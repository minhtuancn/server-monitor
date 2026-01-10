#!/usr/bin/env python3

"""
Task Recovery Module
Recovers tasks that were interrupted during system shutdown or crashes
"""

import os
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from observability import StructuredLogger

# Initialize logger
logger = StructuredLogger("task_recovery")

# Task is considered stale if running for more than this duration (minutes)
TASK_STALE_THRESHOLD_MINUTES = int(os.environ.get("TASK_STALE_THRESHOLD_MINUTES", "60"))


def recover_stale_tasks():
    """
    Recover tasks that were left in 'running' state
    This happens when:
    - System crashes
    - Services are killed
    - Network interruptions

    A task is considered stale if:
    - Status is 'running'
    - started_at is more than TASK_STALE_THRESHOLD_MINUTES ago
    - No recent heartbeat (not implemented yet, but placeholder for future)

    Returns:
        Dict with recovery statistics
    """
    logger.info("Starting task recovery check", stale_threshold_minutes=TASK_STALE_THRESHOLD_MINUTES)

    try:
        # Calculate cutoff time for stale tasks
        cutoff_time = (datetime.utcnow() - timedelta(minutes=TASK_STALE_THRESHOLD_MINUTES)).isoformat() + "Z"

        # Get all running tasks
        running_tasks = db.get_tasks(status="running")

        if not running_tasks:
            logger.info("No running tasks found during recovery check")
            return {"recovered": 0, "message": "No running tasks to recover"}

        # Check each task
        stale_tasks = []
        for task in running_tasks:
            started_at = task.get("started_at")

            # If no started_at or started long ago, mark as stale
            if not started_at or started_at < cutoff_time:
                stale_tasks.append(task)

        # Mark stale tasks as interrupted
        recovered_count = 0
        for task in stale_tasks:
            try:
                db.update_task_status(
                    task_id=task["id"],
                    status="interrupted",
                    finished_at=datetime.utcnow().isoformat() + "Z",
                    stderr="Task interrupted due to system restart or timeout",
                )

                logger.info(
                    "Recovered stale task",
                    task_id=task["id"],
                    server_id=task["server_id"],
                    started_at=task.get("started_at"),
                    command_preview=task.get("command", "")[:100],
                )

                recovered_count += 1

            except Exception as e:
                logger.error("Failed to recover task", task_id=task["id"], error=str(e))

        # Add audit log for recovery (if we recovered any tasks)
        if recovered_count > 0:
            try:
                # Get first admin user as system user
                admin_users = db.get_all_users()
                system_user_id = admin_users[0]["id"] if admin_users else 1

                db.add_audit_log(
                    user_id=system_user_id,
                    action="task.recover",
                    target_type="tasks",
                    target_id="system",
                    meta={
                        "recovered_count": recovered_count,
                        "total_running": len(running_tasks),
                        "cutoff_time": cutoff_time,
                        "stale_threshold_minutes": TASK_STALE_THRESHOLD_MINUTES,
                    },
                )
            except Exception as e:
                logger.warning("Failed to create audit log for task recovery", error=str(e))

        logger.info(
            "Task recovery complete",
            recovered=recovered_count,
            total_running=len(running_tasks),
            cutoff_time=cutoff_time,
        )

        return {
            "recovered": recovered_count,
            "total_running": len(running_tasks),
            "message": f"Recovered {recovered_count} stale tasks out of {len(running_tasks)} running tasks",
        }

    except Exception as e:
        logger.error("Task recovery failed", error=str(e))
        return {"recovered": 0, "error": str(e), "message": f"Task recovery failed: {str(e)}"}


def recover_terminal_sessions():
    """
    Recover terminal sessions that were left in 'active' state
    Mark them as interrupted on startup

    Returns:
        Dict with recovery statistics
    """
    logger.info("Starting terminal session recovery check")

    try:
        # Get all active terminal sessions
        active_sessions = db.get_terminal_sessions(status="active")

        if not active_sessions:
            logger.info("No active terminal sessions found during recovery check")
            return {"recovered": 0, "message": "No active terminal sessions to recover"}

        # Mark all as interrupted (they can't still be active after restart)
        recovered_count = 0
        for session in active_sessions:
            try:
                db.end_terminal_session(session["id"], status="interrupted")

                logger.info(
                    "Recovered terminal session",
                    session_id=session["id"],
                    server_id=session["server_id"],
                    user_id=session["user_id"],
                    started_at=session.get("started_at"),
                )

                recovered_count += 1

            except Exception as e:
                logger.error("Failed to recover terminal session", session_id=session["id"], error=str(e))

        logger.info("Terminal session recovery complete", recovered=recovered_count, total_active=len(active_sessions))

        return {
            "recovered": recovered_count,
            "total_active": len(active_sessions),
            "message": f"Recovered {recovered_count} terminal sessions",
        }

    except Exception as e:
        logger.error("Terminal session recovery failed", error=str(e))
        return {"recovered": 0, "error": str(e), "message": f"Terminal session recovery failed: {str(e)}"}


def run_startup_recovery():
    """
    Run all recovery checks on startup
    - Recover stale tasks
    - Recover terminal sessions

    Returns:
        Dict with combined recovery statistics
    """
    logger.info("Running startup recovery checks")

    task_result = recover_stale_tasks()
    session_result = recover_terminal_sessions()

    total_recovered = task_result.get("recovered", 0) + session_result.get("recovered", 0)

    logger.info(
        "Startup recovery complete",
        tasks_recovered=task_result.get("recovered", 0),
        sessions_recovered=session_result.get("recovered", 0),
        total_recovered=total_recovered,
    )

    return {"tasks": task_result, "terminal_sessions": session_result, "total_recovered": total_recovered}


if __name__ == "__main__":
    # Test the recovery
    print("Testing task recovery...")
    result = run_startup_recovery()
    print(f"\nRecovery results:")
    print(f"  Tasks recovered: {result['tasks']['recovered']}")
    print(f"  Sessions recovered: {result['terminal_sessions']['recovered']}")
    print(f"  Total recovered: {result['total_recovered']}")
