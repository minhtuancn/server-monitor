"use client";

import { apiFetch } from "@/lib/api-client";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import RefreshIcon from "@mui/icons-material/Refresh";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import WarningIcon from "@mui/icons-material/Warning";
import ApiIcon from "@mui/icons-material/Api";
import StorageIcon from "@mui/icons-material/Storage";
import TerminalIcon from "@mui/icons-material/Terminal";
import WebSocketIcon from "@mui/icons-material/Hub";
import MemoryIcon from "@mui/icons-material/Memory";
import DiskIcon from "@mui/icons-material/SdStorage";
import CpuIcon from "@mui/icons-material/DeveloperBoard";
import ScheduleIcon from "@mui/icons-material/Schedule";

type ServiceStatus = {
  status: "healthy" | "unhealthy" | "degraded" | "error";
  port?: number;
  message: string;
  size_mb?: number;
  server_count?: number;
};

type SystemMetrics = {
  memory?: {
    total_mb: number;
    used_mb: number;
    available_mb: number;
    percent_used: number;
  };
  disk?: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    percent_used: number;
  };
  cpu?: {
    percent_used: number;
    cores: number;
  };
  uptime?: {
    seconds: number;
    human: string;
  };
  error?: string;
};

type HealthResponse = {
  status: "healthy" | "degraded";
  timestamp: string;
  services: {
    api: ServiceStatus;
    websocket: ServiceStatus;
    terminal: ServiceStatus;
    database: ServiceStatus;
  };
  system: SystemMetrics;
};

export default function HealthDashboardPage() {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [countdown, setCountdown] = useState(10);

  // Fetch health data
  const { data, isLoading, error, refetch } = useQuery<HealthResponse>({
    queryKey: ["admin-health"],
    queryFn: () => apiFetch("/api/admin/health"),
    refetchInterval: autoRefresh ? 10000 : false,
  });

  // Countdown timer for next refresh
  useEffect(() => {
    if (!autoRefresh) {
      setCountdown(10);
      return;
    }

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) return 10;
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircleIcon color="success" />;
      case "unhealthy":
        return <ErrorIcon color="error" />;
      case "degraded":
        return <WarningIcon color="warning" />;
      case "error":
        return <ErrorIcon color="error" />;
      default:
        return <WarningIcon />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "success";
      case "unhealthy":
        return "error";
      case "degraded":
        return "warning";
      case "error":
        return "error";
      default:
        return "default";
    }
  };

  const getServiceIcon = (service: string) => {
    switch (service) {
      case "api":
        return <ApiIcon />;
      case "websocket":
        return <WebSocketIcon />;
      case "terminal":
        return <TerminalIcon />;
      case "database":
        return <StorageIcon />;
      default:
        return <ApiIcon />;
    }
  };

  if (isLoading && !data) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load health data: {(error as Error).message}
      </Alert>
    );
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            System Health Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monitor services status and system metrics
          </Typography>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
          <Typography variant="body2" color="text.secondary">
            {autoRefresh ? `Auto-refresh in ${countdown}s` : "Auto-refresh disabled"}
          </Typography>
          <Tooltip title={autoRefresh ? "Disable auto-refresh" : "Enable auto-refresh"}>
            <Chip
              label={autoRefresh ? "Auto" : "Manual"}
              color={autoRefresh ? "primary" : "default"}
              onClick={() => setAutoRefresh(!autoRefresh)}
              size="small"
              aria-label={autoRefresh ? "Disable automatic health data refresh" : "Enable automatic health data refresh"}
            />
          </Tooltip>
          <Tooltip title="Refresh now">
            <IconButton 
              onClick={() => refetch()} 
              size="small"
              aria-label="Refresh health data immediately"
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>

      {/* Overall Status Banner */}
      <Alert
        severity={data?.status === "healthy" ? "success" : "warning"}
        icon={getStatusIcon(data?.status || "degraded")}
        sx={{ mb: 3 }}
      >
        <Typography variant="subtitle1">
          Overall Status: <strong>{data?.status?.toUpperCase()}</strong>
        </Typography>
        <Typography variant="caption">
          Last checked: {data?.timestamp ? new Date(data.timestamp).toLocaleString() : "N/A"}
        </Typography>
      </Alert>

      {/* Services Status Grid */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2 }}>
        Services Status
      </Typography>
      <Grid container spacing={3} mb={4}>
        {data?.services &&
          Object.entries(data.services).map(([name, service]) => (
            <Grid item xs={12} sm={6} md={3} key={name}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center" gap={1}>
                        {getServiceIcon(name)}
                        <Typography variant="h6" sx={{ textTransform: "capitalize" }}>
                          {name}
                        </Typography>
                      </Box>
                      {getStatusIcon(service.status)}
                    </Box>
                    <Chip
                      label={service.status}
                      color={getStatusColor(service.status) as any}
                      size="small"
                      sx={{ alignSelf: "flex-start" }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {service.message}
                    </Typography>
                    {service.port && (
                      <Typography variant="caption" color="text.secondary">
                        Port: {service.port}
                      </Typography>
                    )}
                    {service.size_mb !== undefined && (
                      <Typography variant="caption" color="text.secondary">
                        Size: {service.size_mb} MB
                      </Typography>
                    )}
                    {service.server_count !== undefined && (
                      <Typography variant="caption" color="text.secondary">
                        Servers: {service.server_count}
                      </Typography>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
      </Grid>

      {/* System Metrics */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2 }}>
        System Metrics
      </Typography>

      {data?.system?.error ? (
        <Alert severity="error">{data.system.error}</Alert>
      ) : (
        <Grid container spacing={3}>
          {/* Memory Usage */}
          {data?.system?.memory && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <MemoryIcon color="primary" />
                      <Typography variant="h6">Memory Usage</Typography>
                    </Box>
                    <Box>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">
                          {data.system.memory.used_mb.toFixed(0)} MB / {data.system.memory.total_mb.toFixed(0)} MB
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {data.system.memory.percent_used.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.system.memory.percent_used}
                        color={data.system.memory.percent_used > 90 ? "error" : data.system.memory.percent_used > 75 ? "warning" : "primary"}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Available: {data.system.memory.available_mb.toFixed(0)} MB
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Disk Usage */}
          {data?.system?.disk && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <DiskIcon color="primary" />
                      <Typography variant="h6">Disk Usage</Typography>
                    </Box>
                    <Box>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">
                          {data.system.disk.used_gb.toFixed(1)} GB / {data.system.disk.total_gb.toFixed(1)} GB
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {data.system.disk.percent_used.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.system.disk.percent_used}
                        color={data.system.disk.percent_used > 90 ? "error" : data.system.disk.percent_used > 75 ? "warning" : "primary"}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Available: {data.system.disk.available_gb.toFixed(1)} GB
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* CPU Usage */}
          {data?.system?.cpu && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <CpuIcon color="primary" />
                      <Typography variant="h6">CPU Usage</Typography>
                    </Box>
                    <Box>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">
                          {data.system.cpu.cores} cores
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {data.system.cpu.percent_used.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.system.cpu.percent_used}
                        color={data.system.cpu.percent_used > 90 ? "error" : data.system.cpu.percent_used > 75 ? "warning" : "primary"}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* System Uptime */}
          {data?.system?.uptime && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <ScheduleIcon color="primary" />
                      <Typography variant="h6">System Uptime</Typography>
                    </Box>
                    <Typography variant="h4">{data.system.uptime.human}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {data.system.uptime.seconds.toLocaleString()} seconds
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );
}
