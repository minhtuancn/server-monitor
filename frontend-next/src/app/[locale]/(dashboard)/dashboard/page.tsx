"use client";

import { downloadFile } from "@/lib/api-client";
import { MONITORING_WS_URL } from "@/lib/config";
import { createReconnectingWebSocket } from "@/lib/websocket";
import { StatsOverview, Server } from "@/types";
import { ServerFormDialog } from "@/components/server/ServerFormDialog";
import { useGroups } from "@/hooks/use-groups";
import { apiFetch } from "@/lib/api-client";
import AddIcon from "@mui/icons-material/Add";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import RefreshIcon from "@mui/icons-material/Refresh";
import TerminalIcon from "@mui/icons-material/Terminal";
import FilterListIcon from "@mui/icons-material/FilterList";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function DashboardWithGroups() {
  const [liveServers, setLiveServers] = useState<Server[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<string>("");

  const {
    data: stats,
    isLoading: statsLoading,
    refetch: refetchStats,
  } = useQuery<StatsOverview>({
    queryKey: ["stats"],
    queryFn: () => apiFetch<StatsOverview>("/api/stats/overview"),
  });

  const {
    data: servers,
    isLoading: serversLoading,
    refetch: refetchServers,
  } = useQuery<Server[]>({
    queryKey: ["servers"],
    queryFn: () => apiFetch<Server[]>("/api/servers"),
  });

  const { data: groups = [] } = useGroups("servers");

  const { data: recentActivity } = useQuery({
    queryKey: ["recent-activity"],
    queryFn: () =>
      apiFetch<{
        activities: Array<{
          id: string;
          user_id: number;
          username?: string;
          action: string;
          target_type: string;
          target_id: string;
          server_name?: string;
          created_at: string;
        }>;
        count: number;
      }>("/api/activity/recent?limit=10"),
    refetchInterval: 30000,
  });

  // Filter servers by selected group
  const displayServers = liveServers.length ? liveServers : servers || [];
  const filteredServers = selectedGroup
    ? displayServers.filter((s) => s.group_id?.toString() === selectedGroup)
    : displayServers;

  const isLoading = statsLoading || serversLoading;

  // Copy live server data from existing servers
  useEffect(() => {
    if (!servers) return;
    setLiveServers((prev) => {
      if (!prev.length) return servers;
      const map = new Map<number, Server>();
      servers.forEach((s) => map.set(s.id, s));
      prev.forEach((live) => {
        const existing = map.get(live.id);
        if (existing) {
          map.set(live.id, { ...existing, ...live });
        }
      });
      return Array.from(map.values());
    });
  }, [servers]);

  useEffect(() => {
    const url =
      MONITORING_WS_URL || `${window.location.origin.replace("http", "ws")}/ws`;
    const socket = createReconnectingWebSocket(
      url,
      {
        onMessage: (payload: unknown) => {
          if (
            payload &&
            typeof payload === "object" &&
            (payload as { type?: string }).type === "stats_update" &&
            Array.isArray((payload as { data?: unknown }).data)
          ) {
            const items = (payload as { data: unknown[] }).data;
            setLiveServers((prev) => {
              const map = new Map<number, Server>();
              prev.forEach((s) => map.set(s.id, s));
              items.forEach((raw) => {
                if (!raw || typeof raw !== "object") return;
                const item = raw as {
                  server_id: number;
                  server_name?: string;
                  status?: string;
                  cpu?: number;
                  memory?: number;
                  disk?: number;
                };
                const existing = map.get(item.server_id) || ({} as Server);
                map.set(item.server_id, {
                  ...existing,
                  id: item.server_id,
                  name: item.server_name || existing.name,
                  status: item.status || existing.status,
                  cpu: item.cpu,
                  memory: item.memory,
                  disk: item.disk,
                  host: existing.host || "",
                });
              });
              return Array.from(map.values());
            });
          }
        },
      },
      { maxRetries: 10, retryDelayMs: 1500 }
    );

    return () => socket.close();
  }, []);

  // Helper functions for activity feed
  const getActionIcon = (action: string) => {
    const iconMap: Record<string, string> = {
      create: "➕",
      update: "✏️",
      delete: "🗑️",
      login: "🔐",
      logout: "👋",
      execute: "▶️",
      view: "👁️",
    };
    return iconMap[action] || "📝";
  };

  const getActionText = (action: string) => {
    const textMap: Record<string, string> = {
      create: "created",
      update: "updated",
      delete: "deleted",
      login: "logged in",
      logout: "logged out",
      execute: "executed task",
      view: "viewed",
    };
    return textMap[action] || action;
  };

  const timeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <Stack spacing={3}>
      <Box
        display="flex"
        alignItems={{ xs: "flex-start", sm: "center" }}
        justifyContent="space-between"
        gap={2}
        flexWrap="wrap"
      >
        <Box>
          <Typography variant="h5" fontWeight={700}>
            Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time overview of all monitored servers
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap" justifyContent="flex-end">
          <Button
            size="small"
            variant="outlined"
            startIcon={<CloudDownloadIcon />}
            onClick={() => downloadFile("/api/export/servers/csv", "servers.csv")}
          >
            Export CSV
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={<CloudDownloadIcon />}
            onClick={() => downloadFile("/api/export/servers/json", "servers.json")}
          >
            Export JSON
          </Button>
          <IconButton
            onClick={() => Promise.all([refetchServers(), refetchStats()])}
            sx={{ width: 44, height: 44 }}
            aria-label="Refresh servers and stats"
          >
            <RefreshIcon />
          </IconButton>
        </Stack>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Servers
              </Typography>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <Typography variant="h4">{stats?.total_servers ?? 0}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Online
              </Typography>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <Typography variant="h4" color="success.main">
                  {stats?.online_servers ?? 0}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Offline
              </Typography>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <Typography variant="h4" color="error.main">
                  {stats?.offline_servers ?? 0}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          {recentActivity?.activities && recentActivity.activities.length > 0 ? (
            <Stack spacing={0} divider={<Box sx={{ borderBottom: 1, borderColor: "divider" }} />}>
              {recentActivity.activities.map((activity) => {
                return (
                  <Box
                    key={activity.id}
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      p: 1.5,
                      borderRadius: 1,
                      "&:hover": { bgcolor: "action.hover" },
                    }}
                  >
                    <Typography fontSize="1.5rem">{getActionIcon(activity.action)}</Typography>
                    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                      <Typography variant="body2" noWrap>
                        <strong>{activity.username || `User ${activity.user_id}`}</strong>{" "}
                        {getActionText(activity.action)}
                        {activity.server_name && (
                          <> on <strong>{activity.server_name}</strong></>
                        )}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {timeAgo(activity.created_at)}
                      </Typography>
                    </Box>
                  </Box>
                );
              })}
            </Stack>
          ) : (
            <Typography color="text.secondary" mt={2}>
              No recent activity
            </Typography>
          )}
        </CardContent>
      </Card>

      <Card id="servers">
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2} flexWrap="wrap" gap={2}>
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="h6">Servers</Typography>
              {isLoading && <CircularProgress size={18} />}
            </Box>
            <Stack direction="row" spacing={2} alignItems="center">
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel id="group-filter-label">
                  <FilterListIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: "middle" }} />
                  Filter by Group
                </InputLabel>
                <Select
                  labelId="group-filter-label"
                  value={selectedGroup}
                  label="Filter by Group"
                  onChange={(e) => setSelectedGroup(e.target.value)}
                >
                  <MenuItem value="">
                    <em>All Servers</em>
                  </MenuItem>
                  {groups.map((group) => (
                    <MenuItem key={group.id} value={group.id.toString()}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: "50%",
                            bgcolor: group.color,
                          }}
                        />
                        <span>{group.name}</span>
                      </Stack>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setDialogOpen(true)}
              >
                Add Server
              </Button>
            </Stack>
          </Box>
          <Grid container spacing={2}>
            {filteredServers.map((server) => {
              const serverGroup = groups.find((g) => g.id === server.group_id);
              return (
                <Grid item xs={12} md={6} lg={4} key={server.id}>
                  <Card variant="outlined" sx={{ height: "100%" }}>
                    <CardContent>
                      <Stack spacing={1.5}>
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                          <Typography variant="subtitle1" fontWeight={700}>
                            {server.name}
                          </Typography>
                          <Chip
                            size="small"
                            color={
                              server.status === "online"
                                ? "success"
                                : server.status === "offline"
                                  ? "error"
                                  : "default"
                            }
                            label={server.status || "unknown"}
                          />
                        </Box>
                        {serverGroup && (
                          <Chip
                            label={serverGroup.name}
                            size="small"
                            sx={{
                              bgcolor: serverGroup.color + "20",
                              color: serverGroup.color,
                              borderLeft: `3px solid ${serverGroup.color}`,
                              maxWidth: "fit-content",
                            }}
                          />
                        )}
                        <Typography variant="body2" color="text.secondary">
                          {server.host}
                        </Typography>
                        <Stack direction="row" spacing={1} flexWrap="wrap">
                          <Chip label={`CPU ${server.cpu ?? "-"}%`} size="small" />
                          <Chip label={`RAM ${server.memory ?? "-"}%`} size="small" />
                          <Chip label={`Disk ${server.disk ?? "-"}%`} size="small" />
                        </Stack>
                        <Stack direction="row" spacing={1}>
                          <Button
                            component={Link}
                            href={`./servers/${server.id}`}
                            size="small"
                            variant="outlined"
                          >
                            Details
                          </Button>
                          <Button
                            component={Link}
                            href={`./terminal?server=${server.id}`}
                            size="small"
                            variant="text"
                            startIcon={<TerminalIcon />}
                          >
                            Terminal
                          </Button>
                        </Stack>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </CardContent>
      </Card>

      <ServerFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSuccess={() => {
          refetchServers();
          refetchStats();
        }}
      />
    </Stack>
  );
}
