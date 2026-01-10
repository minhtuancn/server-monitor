"use client";

import { useSession } from "@/hooks/useSession";
import { useThemeSync } from "@/hooks/use-theme-sync";
import { Role } from "@/types";
import MenuIcon from "@mui/icons-material/Menu";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import LogoutIcon from "@mui/icons-material/Logout";
import DashboardIcon from "@mui/icons-material/Dashboard";
import StorageIcon from "@mui/icons-material/Storage";
import TerminalIcon from "@mui/icons-material/Terminal";
import SettingsIcon from "@mui/icons-material/Settings";
import LanguageIcon from "@mui/icons-material/Language";
import EmailIcon from "@mui/icons-material/Email";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import NotificationsIcon from "@mui/icons-material/Notifications";
import PeopleIcon from "@mui/icons-material/People";
import HealthAndSafetyIcon from "@mui/icons-material/HealthAndSafety";
import PolicyIcon from "@mui/icons-material/Policy";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import AssignmentIcon from "@mui/icons-material/Assignment";
import HistoryIcon from "@mui/icons-material/History";
import WebhookIcon from "@mui/icons-material/Webhook";
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
} from "@mui/material";
import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useTheme as useMuiTheme } from "@mui/material/styles";
import { useTheme } from "next-themes";
import { useState, useEffect } from "react";

type NavItem = {
  label: string;
  href: string;
  icon: React.ReactNode;
  roles?: Role[];
};

type NavSection = {
  title: string;
  items: NavItem[];
};

const NAV_SECTIONS: NavSection[] = [
  {
    title: "Overview",
    items: [
      {
        label: "Dashboard",
        href: "/dashboard",
        icon: <DashboardIcon />,
      },
      {
        label: "Servers",
        href: "/dashboard#servers",
        icon: <StorageIcon />,
      },
      {
        label: "Terminal",
        href: "/terminal",
        icon: <TerminalIcon />,
      },
      {
        label: "Terminal Sessions",
        href: "/terminal/sessions",
        icon: <AssignmentIcon />,
        roles: ["admin", "operator"],
      },
    ],
  },
  {
    title: "Configuration",
    items: [
      { label: "Settings", href: "/settings", icon: <SettingsIcon /> },
      {
        label: "Database",
        href: "/settings/database",
        icon: <StorageIcon />,
        roles: ["admin"],
      },
      {
        label: "Domain & SSL",
        href: "/settings/domain",
        icon: <LanguageIcon />,
        roles: ["admin"],
      },
      {
        label: "Email",
        href: "/settings/email",
        icon: <EmailIcon />,
        roles: ["admin"],
      },
      {
        label: "SSH Keys",
        href: "/settings/ssh-keys",
        icon: <VpnKeyIcon />,
      },
      {
        label: "Webhooks",
        href: "/settings/integrations/webhooks",
        icon: <WebhookIcon />,
        roles: ["admin"],
      },
    ],
  },
  {
    title: "Operations",
    items: [
      {
        label: "Notifications",
        href: "/notifications",
        icon: <NotificationsIcon />,
      },
      { label: "Users", href: "/users", icon: <PeopleIcon />, roles: ["admin"] },
      {
        label: "Audit Logs",
        href: "/audit-logs",
        icon: <HistoryIcon />,
        roles: ["admin"],
      },
      {
        label: "System Check",
        href: "/system-check",
        icon: <HealthAndSafetyIcon />,
      },
      {
        label: "CORS Test",
        href: "/test-cors",
        icon: <PolicyIcon />,
      },
      {
        label: "Exports",
        href: "/exports",
        icon: <CloudDownloadIcon />,
      },
    ],
  },
];

const DESKTOP_DRAWER_WIDTH = 270;
const MOBILE_DRAWER_WIDTH = 240;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const params = useParams();
  const locale = (params?.locale as string) || "en";
  const router = useRouter();
  const muiTheme = useMuiTheme();
  const { theme, setTheme } = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down("md"));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const { data: session } = useSession();
  
  // Sync theme changes to backend
  useThemeSync();

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleDrawer = () => setMobileOpen((open) => !open);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.replace(`/${locale}/login`);
  };

  const currentRole = session?.authenticated ? session.user?.role : "public";

  const renderNavItems = () =>
    NAV_SECTIONS.map((section) => (
      <Box key={section.title} sx={{ mb: 2 }}>
        <Typography variant="caption" sx={{ px: 2.5, color: "text.secondary" }}>
          {section.title}
        </Typography>
        <List>
          {section.items
            .filter((item) => {
              if (!item.roles || item.roles.length === 0) return true;
              return currentRole && item.roles.includes(currentRole);
            })
            .map((item) => {
              const href = `/${locale}${item.href}`;
              const active = pathname === href || pathname.startsWith(`${href}/`);
              return (
                /* eslint-disable @typescript-eslint/no-explicit-any */
                <ListItemButton
                  key={item.label}
                  component={Link as any}
                  href={href as any}
                  selected={!!active}
                  onClick={() => isMobile && setMobileOpen(false)}
                  sx={{
                    borderRadius: 2,
                    mx: 1,
                    my: 0.5,
                  }}
                >
                  {/* eslint-enable @typescript-eslint/no-explicit-any */}
                  <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              );
            })}
        </List>
      </Box>
    ));

  const drawerContent = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Box sx={{ px: 2, py: 2 }}>
        <Typography variant="h6">Server Monitor</Typography>
        <Typography variant="body2" color="text.secondary">
          Multi-server dashboard
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ flex: 1, overflowY: "auto", py: 1 }}>{renderNavItems()}</Box>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Logged in as
        </Typography>
        <Typography variant="body2" fontWeight={600}>
          {session?.authenticated ? session.user?.username : "Guest"}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {session?.authenticated ? session.user?.role : "public"}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar position="fixed" color="inherit" elevation={1} sx={{ zIndex: 1300 }}>
        <Toolbar sx={{ display: "flex", gap: 1 }}>
          {isMobile && (
            <IconButton 
              edge="start" 
              onClick={toggleDrawer} 
              sx={{ width: 44, height: 44 }}
              aria-label="Open navigation menu"
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Server Monitor
          </Typography>
          <Tooltip title="Toggle theme">
            <IconButton
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              color="inherit"
              sx={{ width: 44, height: 44 }}
              aria-label="Toggle theme"
            >
              {mounted && muiTheme.palette.mode === "dark" ? (
                <Brightness7Icon />
              ) : (
                <Brightness4Icon />
              )}
            </IconButton>
          </Tooltip>
          <Tooltip title="Logout">
            <IconButton 
              onClick={handleLogout} 
              color="inherit" 
              sx={{ width: 44, height: 44 }}
              aria-label="Logout"
            >
              <LogoutIcon />
            </IconButton>
          </Tooltip>
          <Avatar sx={{ width: 36, height: 36, ml: 1 }}>
            {(session?.authenticated && session.user?.username?.[0]?.toUpperCase()) ||
              "A"}
          </Avatar>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { xs: MOBILE_DRAWER_WIDTH, md: DESKTOP_DRAWER_WIDTH },
          flexShrink: { md: 0 },
        }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={toggleDrawer}
            ModalProps={{ keepMounted: true }}
            sx={{
              "& .MuiDrawer-paper": {
                boxSizing: "border-box",
                width: MOBILE_DRAWER_WIDTH,
              },
            }}
          >
            {drawerContent}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            sx={{
              "& .MuiDrawer-paper": {
                boxSizing: "border-box",
                width: DESKTOP_DRAWER_WIDTH,
              },
            }}
            open
          >
            {drawerContent}
          </Drawer>
        )}
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          px: { xs: 2, md: 3 },
          py: { xs: 2, md: 3 },
          width: { md: `calc(100% - ${DESKTOP_DRAWER_WIDTH}px)` },
          mt: 8,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
