"use client";

import { apiFetch, downloadFile } from "@/lib/api-client";
import { MONITORING_WS_URL } from "@/lib/config";
import { createReconnectingWebSocket } from "@/lib/websocket";
import { StatsOverview, Server } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import AddIcon from "@mui/icons-material/Add";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import RefreshIcon from "@mui/icons-material/Refresh";
import TerminalIcon from "@mui/icons-material/Terminal";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  IconButton,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const serverSchema = z.object({
  name: z.string().min(1, "Name is required"),
  host: z.string().min(1, "Host is required"),
  port: z.coerce.number().min(1).max(65535).optional(),
  username: z.string().min(1, "Username is required"),
  description: z.string().optional(),
  tags: z.string().optional(),
});

type ServerForm = z.infer<typeof serverSchema>;

export default function DashboardPage() {
  const [formError, setFormError] = useState<string | null>(null);
  const [liveServers, setLiveServers] = useState<Server[]>([]);

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

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ServerForm>({ resolver: zodResolver(serverSchema) });

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
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const onCreateServer = async (values: ServerForm) => {
    setFormError(null);
    try {
      await apiFetch("/api/servers", {
        method: "POST",
        body: JSON.stringify(values),
      });
      reset();
      refetchServers();
      refetchStats();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to create server";
      setFormError(message);
    }
  };

  const isLoading = statsLoading || serversLoading;

  useEffect(() => {
    if (servers) {
      setLiveServers(servers);
    }
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
      { maxRetries: 10, retryDelayMs: 1500 },
    );

    return () => socket.close();
  }, []);

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

      {/* Recent Activity Widget */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          {recentActivity?.activities && recentActivity.activities.length > 0 ? (
            <Stack spacing={1} mt={2}>
              {recentActivity.activities.map((activity) => {
                const getActionIcon = (action: string) => {
                  if (action.includes("terminal")) return "💻";
                  if (action.includes("ssh_key")) return "🔑";
                  if (action.includes("inventory")) return "📊";
                  if (action.includes("user")) return "👤";
                  if (action.includes("server")) return "🖥️";
                  return "📝";
                };

                const getActionText = (action: string) => {
                  const parts = action.split(".");
                  if (parts.length >= 2) {
                    return `${parts[0]} ${parts[1]}`;
                  }
                  return action;
                };

                const timeAgo = (dateStr: string) => {
                  const date = new Date(dateStr);
                  const now = new Date();
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
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">Servers</Typography>
            {isLoading && <CircularProgress size={18} />}
          </Box>
          <Grid container spacing={2}>
            {(liveServers.length ? liveServers : servers || []).map((server) => (
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
                      <Typography variant="body2" color="text.secondary">
                        {server.host}
                      </Typography>
                      <Stack direction="row" spacing={1}>
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
            ))}
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">Add Server</Typography>
            <IconButton onClick={() => reset()} sx={{ width: 44, height: 44 }}>
              <AddIcon />
            </IconButton>
          </Box>
          {formError && <Alert severity="error">{formError}</Alert>}
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Name"
                fullWidth
                {...register("name")}
                error={!!errors.name}
                helperText={errors.name?.message}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Host"
                fullWidth
                {...register("host")}
                error={!!errors.host}
                helperText={errors.host?.message}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Port"
                type="number"
                fullWidth
                {...register("port")}
                error={!!errors.port}
                helperText={errors.port?.message}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Username"
                fullWidth
                {...register("username")}
                error={!!errors.username}
                helperText={errors.username?.message}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <TextField
                label="Description"
                fullWidth
                {...register("description")}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Tags" fullWidth {...register("tags")} />
            </Grid>
            <Grid
              item
              xs={12}
              md={6}
              display="flex"
              justifyContent={{ xs: "flex-start", md: "flex-end" }}
              alignItems="center"
            >
              <Button
                size="small"
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleSubmit(onCreateServer)}
                disabled={isSubmitting}
              >
                {isSubmitting ? "Saving..." : "Add Server"}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Stack>
  );
}
