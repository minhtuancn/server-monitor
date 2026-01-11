"use client";

import { usePathname, useParams } from "next/navigation";
import { Breadcrumbs as MuiBreadcrumbs, Link, Typography, Box } from "@mui/material";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import HomeIcon from "@mui/icons-material/Home";

type BreadcrumbSegment = {
  label: string;
  href?: string;
};

export function Breadcrumbs() {
  const pathname = usePathname();
  const params = useParams();
  const locale = (params?.locale as string) || "en";

  // Route label mappings
  const routeLabels: Record<string, string> = {
    dashboard: "Dashboard",
    servers: "Servers",
    terminal: "Terminal",
    notifications: "Notifications",
    users: "Users",
    settings: "Settings",
    "audit-logs": "Audit Logs",
    "system-check": "System Check",
    "test-cors": "CORS Test",
    exports: "Exports",
    "access-denied": "Access Denied",
    "server-notes": "Server Notes",
    database: "Database",
    health: "System Health",
    domain: "Domain & SSL",
    email: "Email",
    "ssh-keys": "SSH Keys",
    integrations: "Integrations",
    webhooks: "Webhooks",
    groups: "Server Groups",
    sessions: "Terminal Sessions",
  };

  const generateBreadcrumbs = (): BreadcrumbSegment[] => {
    // Remove locale from pathname
    const pathWithoutLocale = pathname?.replace(`/${locale}`, "") || "";

    // Split path into segments
    const segments = pathWithoutLocale.split("/").filter(Boolean);

    // Always start with Dashboard as home
    const breadcrumbs: BreadcrumbSegment[] = [
      {
        label: "Dashboard",
        href: `/${locale}/dashboard`,
      },
    ];

    // Build breadcrumbs from segments
    let currentPath = `/${locale}`;

    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;

      // Check if segment is a number (likely an ID)
      const isId = /^\d+$/.test(segment);

      if (isId) {
        // For IDs, use generic label with the ID
        const prevSegment = segments[index - 1];
        if (prevSegment === "servers") {
          breadcrumbs.push({
            label: `Server #${segment}`,
            href: currentPath,
          });
        } else {
          breadcrumbs.push({
            label: `#${segment}`,
            href: currentPath,
          });
        }
      } else {
        // Use mapped label or capitalize segment
        const label = routeLabels[segment] || segment
          .split("-")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");

        breadcrumbs.push({
          label,
          href: currentPath,
        });
      }
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  // Don't show breadcrumbs on login or setup pages
  if (pathname?.includes("/login") || pathname?.includes("/setup")) {
    return null;
  }

  // Only show if we have more than just the home breadcrumb
  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <Box
      sx={{
        px: { xs: 2, md: 3 },
        py: 1.5,
        borderBottom: 1,
        borderColor: "divider",
        bgcolor: "background.paper",
      }}
      role="navigation"
      aria-label="breadcrumb"
    >
      <MuiBreadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb navigation"
        sx={{
          "& .MuiBreadcrumbs-ol": {
            flexWrap: "nowrap",
          },
          "& .MuiBreadcrumbs-li": {
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          },
        }}
      >
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === breadcrumbs.length - 1;
          const isFirst = index === 0;

          if (isLast) {
            // Last breadcrumb - current page (not clickable)
            return (
              <Typography
                key={crumb.href || crumb.label}
                color="text.primary"
                sx={{
                  display: "flex",
                  alignItems: "center",
                  fontWeight: 500,
                  maxWidth: { xs: "150px", sm: "200px", md: "300px" },
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
                aria-current="page"
              >
                {crumb.label}
              </Typography>
            );
          }

          // Clickable breadcrumb
          return (
            <Link
              key={crumb.href || crumb.label}
              color="inherit"
              href={crumb.href}
              underline="hover"
              sx={{
                display: "flex",
                alignItems: "center",
                maxWidth: { xs: "100px", sm: "150px", md: "200px" },
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {isFirst && (
                <HomeIcon
                  sx={{ mr: 0.5, fontSize: "1.1rem" }}
                  fontSize="inherit"
                />
              )}
              {crumb.label}
            </Link>
          );
        })}
      </MuiBreadcrumbs>
    </Box>
  );
}
