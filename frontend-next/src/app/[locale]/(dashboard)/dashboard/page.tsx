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
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography variant="h5" fontWeight={700}>
            Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time overview of all monitored servers
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<CloudDownloadIcon />}
            onClick={() => downloadFile("/api/export/servers/csv", "servers.csv")}
          >
            Export CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<CloudDownloadIcon />}
            onClick={() => downloadFile("/api/export/servers/json", "servers.json")}
          >
            Export JSON
          </Button>
          <IconButton onClick={() => Promise.all([refetchServers(), refetchStats()])}>
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
            <IconButton onClick={() => reset()}>
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
            <Grid item xs={12} md={6} display="flex" justifyContent="flex-end" alignItems="center">
              <Button
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
