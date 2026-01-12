"use client";

import { apiFetch } from "@/lib/api-client";
import { Server, ServerNote, ServerInventory, Task } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import ConfirmDialog from "@/components/ConfirmDialog";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import RefreshIcon from "@mui/icons-material/Refresh";
import SaveIcon from "@mui/icons-material/Save";
import TerminalIcon from "@mui/icons-material/Terminal";
import StorageIcon from "@mui/icons-material/Storage";
import MemoryIcon from "@mui/icons-material/Memory";
import DnsIcon from "@mui/icons-material/Dns";
import ComputerIcon from "@mui/icons-material/Computer";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  Grid,
  Stack,
  Switch,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Typography,
  LinearProgress,
} from "@mui/material";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { z } from "zod";
import { ServerMetricsChart, MetricGauge } from "@/components/dashboard/server-metrics-chart";
import DockerManagementTab from "@/components/servers/management/DockerManagementTab";
import ServiceManagementTab from "@/components/servers/management/ServiceManagementTab";
import NetworkManagementTab from "@/components/servers/management/NetworkManagementTab";
import PowerManagementControls from "@/components/servers/management/PowerManagementControls";

const noteSchema = z.object({
  content: z.string().min(3, "Note is too short"),
});

type NoteForm = z.infer<typeof noteSchema>;

const taskSchema = z.object({
  command: z.string().min(1, "Command is required").max(10000, "Command too long"),
  timeout_seconds: z.number().min(1).max(600),
  store_output: z.boolean(),
});

type TaskForm = z.infer<typeof taskSchema>;

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`server-tabpanel-${index}`}
      aria-labelledby={`server-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function formatBytes(bytes: number, decimals = 1): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

function formatUptime(seconds?: number): string {
  if (!seconds) return "Unknown";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}

export default function ServerWorkspacePage() {
  const params = useParams();
  const serverId = params?.id as string;
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [noteDialogOpen, setNoteDialogOpen] = useState(false);
  const [editingNote, setEditingNote] = useState<ServerNote | null>(null);
  const [noteFormData, setNoteFormData] = useState({ title: "", description: "", content: "" });
  const [noteTab, setNoteTab] = useState(0); // 0 = Edit, 1 = Preview
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadFormData, setUploadFormData] = useState({ title: "", description: "" });
  const [expandedNotes, setExpandedNotes] = useState<Set<number>>(new Set());
  const [viewNoteDialog, setViewNoteDialog] = useState(false);
  const [viewingNote, setViewingNote] = useState<ServerNote | null>(null);
  const [gaugeSize, setGaugeSize] = useState(160);
  const [deleteNoteDialogOpen, setDeleteNoteDialogOpen] = useState(false);
  const [noteToDelete, setNoteToDelete] = useState<number | null>(null);
  const [cancelTaskDialogOpen, setCancelTaskDialogOpen] = useState(false);
  const [taskToCancel, setTaskToCancel] = useState<string | null>(null);

  const [metricsTimeframe, setMetricsTimeframe] = useState<"1h" | "6h" | "24h" | "7d" | "30d">("24h");

  // Handle gauge size based on window width
  useEffect(() => {
    const handleResize = () => {
      setGaugeSize(window.innerWidth < 600 ? 120 : 160);
    };
    
    // Set initial size
    handleResize();
    
    // Listen for resize
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const { data: server, isLoading: serverLoading } = useQuery<Server>({
    queryKey: ["server", serverId],
    queryFn: () => apiFetch<Server>(`/api/servers/${serverId}`),
    enabled: !!serverId,
  });

  const { data: notes, isLoading: notesLoading } = useQuery<ServerNote[]>({
    queryKey: ["server-notes", serverId],
    queryFn: () => apiFetch<ServerNote[]>(`/api/servers/${serverId}/notes`),
    enabled: !!serverId,
  });

  const { data: metricsHistory, isLoading: metricsLoading } = useQuery({
    queryKey: ["server-metrics-history", serverId, metricsTimeframe],
    queryFn: () =>
      apiFetch<any[]>(
        `/api/servers/${serverId}/metrics/history?timeframe=${metricsTimeframe}&interval=5m`
      ),
    enabled: !!serverId && tabValue === 0,
    refetchInterval: 60000, // Refetch every minute
  });

  const {
    data: inventory,
    isLoading: inventoryLoading,
    error: inventoryError,
  } = useQuery<ServerInventory>({
    queryKey: ["server-inventory", serverId],
    queryFn: () =>
      apiFetch<ServerInventory>(`/api/servers/${serverId}/inventory/latest`),
    enabled: !!serverId && tabValue === 1,
    retry: false,
  });

  const refreshInventoryMutation = useMutation({
    mutationFn: async () => {
      return apiFetch(`/api/servers/${serverId}/inventory/refresh`, {
        method: "POST",
        body: JSON.stringify({}),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["server-inventory", serverId],
      });
    },
  });

  const {
    data: tasks,
    isLoading: tasksLoading,
  } = useQuery<{ tasks: Task[] }>({
    queryKey: ["server-tasks", serverId],
    queryFn: () =>
      apiFetch<{ tasks: Task[] }>(`/api/tasks?server_id=${serverId}`),
    enabled: !!serverId && tabValue === 5,
    refetchInterval: (query) => {
      // Poll if any tasks are running or queued
      const hasActiveTasks = query.state.data?.tasks?.some(
        (t: Task) => t.status === "running" || t.status === "queued"
      );
      return hasActiveTasks ? 3000 : false; // Poll every 3s if active
    },
  });

  const createTaskMutation = useMutation({
    mutationFn: async (taskData: TaskForm) => {
      return apiFetch(`/api/servers/${serverId}/tasks`, {
        method: "POST",
        body: JSON.stringify(taskData),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["server-tasks", serverId] });
      taskFormReset();
      setTaskDialogOpen(false);
    },
  });

  const cancelTaskMutation = useMutation({
    mutationFn: async (taskId: string) => {
      return apiFetch(`/api/tasks/${taskId}/cancel`, {
        method: "POST",
        body: JSON.stringify({}),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["server-tasks", serverId] });
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<NoteForm>({ resolver: zodResolver(noteSchema) });

  const {
    register: taskRegister,
    handleSubmit: handleTaskSubmit,
    reset: taskFormReset,
    formState: { errors: taskErrors, isSubmitting: taskIsSubmitting },
  } = useForm<TaskForm>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      timeout_seconds: 60,
      store_output: false,
    },
  });

  const onAddNote = async (values: NoteForm) => {
    await apiFetch(`/api/servers/${serverId}/notes`, {
      method: "POST",
      body: JSON.stringify({ ...values, title: "Note" }),
    });
    reset();
    queryClient.invalidateQueries({ queryKey: ["server-notes", serverId] });
  };

  const saveNoteMutation = useMutation({
    mutationFn: async (data: { title: string; description: string; content: string }) => {
      if (editingNote) {
        return apiFetch(`/api/servers/${serverId}/notes/${editingNote.id}`, {
          method: "PUT",
          body: JSON.stringify(data),
        });
      } else {
        return apiFetch(`/api/servers/${serverId}/notes`, {
          method: "POST",
          body: JSON.stringify(data),
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["server-notes", serverId] });
      setNoteDialogOpen(false);
      setEditingNote(null);
      setNoteFormData({ title: "", description: "", content: "" });
      setNoteTab(0);
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: async (noteId: number) => {
      return apiFetch(`/api/servers/${serverId}/notes/${noteId}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["server-notes", serverId] });
    },
  });

  const handleOpenNoteDialog = (note?: ServerNote) => {
    if (note) {
      setEditingNote(note);
      setNoteFormData({ 
        title: note.title || "", 
        description: note.description || "", 
        content: note.content 
      });
    } else {
      setEditingNote(null);
      setNoteFormData({ title: "", description: "", content: "" });
    }
    setNoteTab(0);
    setNoteDialogOpen(true);
  };

  const handleSaveNote = () => {
    if (!noteFormData.content.trim()) {
      return;
    }
    saveNoteMutation.mutate(noteFormData);
  };

  const handleDeleteNote = (noteId: number) => {
    setNoteToDelete(noteId);
    setDeleteNoteDialogOpen(true);
  };

  const confirmDeleteNote = async () => {
    if (noteToDelete !== null) {
      await deleteNoteMutation.mutateAsync(noteToDelete);
      setDeleteNoteDialogOpen(false);
      setNoteToDelete(null);
    }
  };

  const uploadFileMutation = useMutation({
    mutationFn: async () => {
      if (!uploadFile) return;
      
      const formData = new FormData();
      formData.append('file', uploadFile);
      if (uploadFormData.title) formData.append('title', uploadFormData.title);
      if (uploadFormData.description) formData.append('description', uploadFormData.description);

      const response = await fetch(`/api/servers/${serverId}/notes/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["server-notes", serverId] });
      setUploadDialogOpen(false);
      setUploadFile(null);
      setUploadFormData({ title: "", description: "" });
    },
  });

  const handleFileUpload = () => {
    if (!uploadFile) return;
    uploadFileMutation.mutate();
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.md')) {
        alert('Please select a markdown file (.md)');
        return;
      }
      setUploadFile(file);
      // Auto-populate title from filename
      const titleFromFile = file.name.replace('.md', '').replace(/[-_]/g, ' ');
      setUploadFormData({ ...uploadFormData, title: titleFromFile });
    }
  };

  const toggleNoteExpansion = (noteId: number) => {
    const newExpanded = new Set(expandedNotes);
    if (newExpanded.has(noteId)) {
      newExpanded.delete(noteId);
    } else {
      newExpanded.add(noteId);
    }
    setExpandedNotes(newExpanded);
  };

  const handleViewNote = (note: ServerNote) => {
    setViewingNote(note);
    setViewNoteDialog(true);
  };

  const onCreateTask = async (values: TaskForm) => {
    createTaskMutation.mutate(values);
  };

  const handleCancelTask = (taskId: string) => {
    setTaskToCancel(taskId);
    setCancelTaskDialogOpen(true);
  };

  const confirmCancelTask = async () => {
    if (taskToCancel) {
      await cancelTaskMutation.mutateAsync(taskToCancel);
      setCancelTaskDialogOpen(false);
      setTaskToCancel(null);
    }
  };

  const handleRefreshInventory = () => {
    refreshInventoryMutation.mutate();
  };

  const getTaskStatusColor = (
    status: string
  ): "default" | "primary" | "success" | "error" | "warning" | "info" => {
    switch (status) {
      case "queued":
        return "default";
      case "running":
        return "primary";
      case "success":
        return "success";
      case "failed":
      case "timeout":
        return "error";
      case "cancelled":
        return "warning";
      default:
        return "default";
    }
  };

  if (serverLoading || !server) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Stack spacing={3}>
      {/* Header */}
      <Stack 
        direction={{ xs: "column", sm: "row" }} 
        alignItems={{ xs: "stretch", sm: "center" }} 
        spacing={2}
      >
        <Button
          component={Link}
          href="../dashboard"
          startIcon={<ArrowBackIcon />}
          sx={{ width: { xs: "100%", sm: "auto" } }}
          aria-label="Go back to dashboard"
        >
          Back
        </Button>
        <Typography 
          variant="h5" 
          fontWeight={700} 
          sx={{ 
            flexGrow: 1,
            textAlign: { xs: "center", sm: "left" },
            wordBreak: "break-word"
          }}
        >
          {server.name}
        </Typography>
        <Button
          component={Link}
          href={`../../terminal?server=${server.id}`}
          startIcon={<TerminalIcon />}
          variant="outlined"
          size="small"
          sx={{ width: { xs: "100%", sm: "auto" } }}
          aria-label={`Open terminal for ${server.name}`}
        >
          Open Terminal
        </Button>
      </Stack>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: "divider", overflowX: "auto" }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          aria-label="server workspace tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Overview" />
          <Tab label="Inventory" />
          <Tab label="Docker" />
          <Tab label="Services" />
          <Tab label="Network" />
          <Tab label="Tasks" />
          <Tab label="Agent" />
          <Tab label="Terminal" />
          <Tab label="Notes" />
          <Tab label="Power" />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {/* Overview Tab */}
        <Grid container spacing={3}>
          {/* Metric Gauges */}
          {server.cpu !== undefined && server.memory !== undefined && server.disk !== undefined && (
            <>
              <Grid item xs={12} sm={6} md={4}>
                <Card>
                  <CardContent>
                    <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                      <Typography variant="h6" color="text.secondary">
                        CPU Usage
                      </Typography>
                      <MetricGauge 
                        value={server.cpu || 0} 
                        max={100} 
                        unit="%" 
                        size={gaugeSize} 
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <Card>
                  <CardContent>
                    <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                      <Typography variant="h6" color="text.secondary">
                        Memory Usage
                      </Typography>
                      <MetricGauge 
                        value={server.memory || 0} 
                        max={100} 
                        unit="%" 
                        size={gaugeSize} 
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <Card>
                  <CardContent>
                    <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                      <Typography variant="h6" color="text.secondary">
                        Disk Usage
                      </Typography>
                      <MetricGauge 
                        value={server.disk || 0} 
                        max={100} 
                        unit="%" 
                        size={gaugeSize} 
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </>
          )}

          {/* Historical Metrics Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Stack 
                    direction={{ xs: "column", sm: "row" }} 
                    justifyContent="space-between" 
                    alignItems={{ xs: "flex-start", sm: "center" }}
                    spacing={2}
                  >
                    <Typography variant="h6">Historical Metrics</Typography>
                    
                    {/* Timeframe Selector */}
                    <Stack 
                      direction="row" 
                      spacing={1} 
                      sx={{ 
                        overflowX: "auto",
                        width: { xs: "100%", sm: "auto" }
                      }}
                    >
                      {(["1h", "6h", "24h", "7d", "30d"] as const).map((tf) => (
                        <Button
                          key={tf}
                          size="small"
                          variant={metricsTimeframe === tf ? "contained" : "outlined"}
                          onClick={() => setMetricsTimeframe(tf)}
                        >
                          {tf}
                        </Button>
                      ))}
                    </Stack>
                  </Stack>

                  {metricsLoading && (
                    <Box display="flex" justifyContent="center" p={4}>
                      <CircularProgress />
                    </Box>
                  )}

                  {metricsHistory && metricsHistory.length > 0 ? (
                    <Box sx={{ 
                      width: "100%", 
                      height: { xs: 300, sm: 400 },
                      overflowX: "auto"
                    }}>
                      <ServerMetricsChart data={metricsHistory} />
                    </Box>
                  ) : (
                    !metricsLoading && (
                      <Alert severity="info">
                        No historical metrics data available yet. Metrics are collected every minute.
                      </Alert>
                    )
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          {/* Server Details */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Server Details
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Host
                    </Typography>
                    <Typography>{server.host}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Status
                    </Typography>
                    <Box>
                      <Chip
                        label={server.status || "unknown"}
                        color={
                          server.status === "online" ? "success" : "default"
                        }
                        size="small"
                      />
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Description
                    </Typography>
                    <Typography>{server.description || "N/A"}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Tags
                    </Typography>
                    <Typography>{server.tags || "N/A"}</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          {/* Connection Info */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Connection Info
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Port
                    </Typography>
                    <Typography>{server.port}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Username
                    </Typography>
                    <Typography>{server.username}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Agent Port
                    </Typography>
                    <Typography>{server.agent_port || 8083}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Last Seen
                    </Typography>
                    <Typography>
                      {server.last_seen
                        ? new Date(server.last_seen).toLocaleString()
                        : "Never"}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {/* Inventory Tab */}
        <Stack spacing={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">System Inventory</Typography>
            <Button
              variant="contained"
              startIcon={
                refreshInventoryMutation.isPending ? (
                  <CircularProgress size={20} />
                ) : (
                  <RefreshIcon />
                )
              }
              onClick={handleRefreshInventory}
              disabled={refreshInventoryMutation.isPending}
              aria-label="Refresh system inventory data"
            >
              Refresh Inventory
            </Button>
          </Box>

          {refreshInventoryMutation.isError && (
            <Alert severity="error">
              Failed to refresh inventory:{" "}
              {(refreshInventoryMutation.error as Error)?.message}
            </Alert>
          )}

          {inventoryLoading && (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          )}

          {inventoryError && !inventory && (
            <Alert severity="info">
              No inventory data available. Click &quot;Refresh Inventory&quot; to
              collect system information.
            </Alert>
          )}

          {inventory && (
            <>
              <Typography variant="caption" color="text.secondary">
                Last collected:{" "}
                {new Date(inventory.collected_at).toLocaleString()}
              </Typography>

              <Grid container spacing={3}>
                {/* OS & Kernel */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        mb={2}
                      >
                        <ComputerIcon color="primary" />
                        <Typography variant="h6">Operating System</Typography>
                      </Stack>
                      <Divider sx={{ mb: 2 }} />
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            OS
                          </Typography>
                          <Typography>
                            {inventory.inventory.os.pretty_name ||
                              `${inventory.inventory.os.name} ${inventory.inventory.os.version}`}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Kernel
                          </Typography>
                          <Typography>{inventory.inventory.kernel}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Hostname
                          </Typography>
                          <Typography>
                            {inventory.inventory.hostname}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Uptime
                          </Typography>
                          <Typography>
                            {inventory.inventory.uptime.uptime_human ||
                              formatUptime(
                                inventory.inventory.uptime.uptime_seconds
                              )}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* CPU */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        mb={2}
                      >
                        <MemoryIcon color="primary" />
                        <Typography variant="h6">CPU</Typography>
                      </Stack>
                      <Divider sx={{ mb: 2 }} />
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Model
                          </Typography>
                          <Typography>
                            {inventory.inventory.cpu.model || "Unknown"}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Cores
                          </Typography>
                          <Typography>
                            {inventory.inventory.cpu.cores}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Memory */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        mb={2}
                      >
                        <StorageIcon color="primary" />
                        <Typography variant="h6">Memory</Typography>
                      </Stack>
                      <Divider sx={{ mb: 2 }} />
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Total
                          </Typography>
                          <Typography>
                            {formatBytes(
                              inventory.inventory.memory.total_mb * 1024 * 1024
                            )}
                          </Typography>
                        </Box>
                        {inventory.inventory.memory.used_mb !== undefined && (
                          <>
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Used
                              </Typography>
                              <Typography>
                                {formatBytes(
                                  inventory.inventory.memory.used_mb *
                                    1024 *
                                    1024
                                )}{" "}
                                ({inventory.inventory.memory.used_percent ?? "N/A"}%)
                              </Typography>
                            </Box>
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Available
                              </Typography>
                              <Typography>
                                {formatBytes(
                                  (inventory.inventory.memory.available_mb ||
                                    0) *
                                    1024 *
                                    1024
                                )}
                              </Typography>
                            </Box>
                          </>
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Disk */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        mb={2}
                      >
                        <StorageIcon color="primary" />
                        <Typography variant="h6">Disk</Typography>
                      </Stack>
                      <Divider sx={{ mb: 2 }} />
                      <Stack spacing={1}>
                        {inventory.inventory.disk.total_gb ? (
                          <>
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Total
                              </Typography>
                              <Typography>
                                {inventory.inventory.disk.total_gb} GB
                              </Typography>
                            </Box>
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Used
                              </Typography>
                              <Typography>
                                {inventory.inventory.disk.used_gb} GB (
                                {inventory.inventory.disk.used_percent ?? "N/A"}%)
                              </Typography>
                            </Box>
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Available
                              </Typography>
                              <Typography>
                                {inventory.inventory.disk.available_gb} GB
                              </Typography>
                            </Box>
                          </>
                        ) : (
                          <Typography color="text.secondary">
                            No disk information available
                          </Typography>
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Network */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        mb={2}
                      >
                        <DnsIcon color="primary" />
                        <Typography variant="h6">Network</Typography>
                      </Stack>
                      <Divider sx={{ mb: 2 }} />
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Primary IP
                          </Typography>
                          <Typography>
                            {inventory.inventory.network.primary_ip ||
                              "Unknown"}
                          </Typography>
                        </Box>
                        {inventory.inventory.network.interfaces &&
                          inventory.inventory.network.interfaces.length > 0 && (
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Interfaces
                              </Typography>
                              <Typography>
                                {inventory.inventory.network.interfaces.join(
                                  ", "
                                )}
                              </Typography>
                            </Box>
                          )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Packages */}
                {inventory.inventory.packages &&
                  inventory.inventory.packages.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Packages
                          </Typography>
                          <Divider sx={{ mb: 2 }} />
                          {inventory.inventory.packages.map((pkg, idx) => (
                            <Typography key={idx}>
                              {pkg.type}: {pkg.count} packages
                            </Typography>
                          ))}
                        </CardContent>
                      </Card>
                    </Grid>
                  )}

                {/* Services */}
                {inventory.inventory.services &&
                  inventory.inventory.services.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Services
                          </Typography>
                          <Divider sx={{ mb: 2 }} />
                          {inventory.inventory.services.map((svc, idx) => (
                            <Typography key={idx}>
                              {svc.type}: {svc.running_count} running
                            </Typography>
                          ))}
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
              </Grid>
            </>
          )}
        </Stack>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {/* Docker Management Tab */}
        <DockerManagementTab 
          serverId={parseInt(serverId)} 
          serverName={server.name} 
        />
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        {/* Services Management Tab */}
        <ServiceManagementTab 
          serverId={parseInt(serverId)} 
          serverName={server.name} 
        />
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        {/* Network Management Tab */}
        <NetworkManagementTab 
          serverId={parseInt(serverId)} 
          serverName={server.name} 
        />
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        {/* Tasks Tab */}
        <Stack spacing={3}>
          <Stack 
            direction={{ xs: "column", sm: "row" }} 
            spacing={2} 
            alignItems={{ xs: "stretch", sm: "center" }}
          >
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Remote Command Execution
            </Typography>
            <Button
              variant="contained"
              startIcon={<PlayArrowIcon />}
              onClick={() => setTaskDialogOpen(true)}
              fullWidth={{ xs: true, sm: false }}
              aria-label="Run new command on this server"
            >
              Run Command
            </Button>
          </Stack>

          {tasksLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : tasks && tasks.tasks && tasks.tasks.length > 0 ? (
            <Card sx={{ overflowX: "auto" }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell>Command</TableCell>
                    <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>Created</TableCell>
                    <TableCell sx={{ display: { xs: "none", md: "table-cell" } }}>Duration</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tasks.tasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <Chip
                          label={task.status}
                          color={getTaskStatusColor(task.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: "monospace",
                            maxWidth: { xs: "150px", sm: "400px" },
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {task.command}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>
                        <Typography variant="caption">
                          {new Date(task.created_at).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ display: { xs: "none", md: "table-cell" } }}>
                        <Typography variant="caption">
                          {task.finished_at && task.started_at
                            ? `${Math.round(
                                (new Date(task.finished_at).getTime() -
                                  new Date(task.started_at).getTime()) /
                                  1000
                              )}s`
                            : task.started_at
                            ? "Running..."
                            : "N/A"}
                        </Typography>
                      </TableCell>
                      <TableCell>
                          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => setSelectedTask(task)}
                              fullWidth
                              aria-label={`View task details: ${task.command.substring(0, 30)}...`}
                            >
                              View
                            </Button>
                            {(task.status === "running" ||
                              task.status === "queued") && (
                              <Button
                                size="small"
                                variant="outlined"
                                color="error"
                                startIcon={<StopIcon />}
                                onClick={() => handleCancelTask(task.id)}
                                disabled={cancelTaskMutation.isPending}
                                fullWidth
                                aria-label={`Cancel task: ${task.command.substring(0, 30)}...`}
                              >
                                Cancel
                              </Button>
                            )}
                          </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          ) : (
            <Alert severity="info">
              No tasks executed yet. Click &quot;Run Command&quot; to execute a
              command on this server.
            </Alert>
          )}
        </Stack>
      </TabPanel>

      <TabPanel value={tabValue} index={6}>
        {/* Agent Management Tab */}
        <AgentManagement serverId={serverId} server={server} />
      </TabPanel>

      <TabPanel value={tabValue} index={7}>
        {/* Terminal Tab */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Web Terminal
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography color="text.secondary" paragraph>
              Click the button below to open a terminal session for this
              server.
            </Typography>
            <Button
              component={Link}
              href={`../../terminal?server=${server.id}`}
              startIcon={<TerminalIcon />}
              variant="contained"
              aria-label={`Open web terminal for ${server.name}`}
            >
              Open Terminal
            </Button>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={tabValue} index={8}>
        {/* Notes Tab */}
        <Stack spacing={3}>
          <Stack 
            direction={{ xs: "column", sm: "row" }} 
            spacing={2} 
            alignItems={{ xs: "stretch", sm: "center" }}
          >
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Server Notes
            </Typography>
            <Button
              variant="outlined"
              startIcon={<UploadFileIcon />}
              onClick={() => setUploadDialogOpen(true)}
              fullWidth={{ xs: true, sm: false }}
              aria-label="Upload markdown file as note"
            >
              Upload .md File
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenNoteDialog()}
              fullWidth={{ xs: true, sm: false }}
              aria-label="Add new note"
            >
              Add Note
            </Button>
          </Stack>

          {notesLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : notes && notes.length > 0 ? (
            <Stack spacing={2}>
              {notes.map((note) => {
                const isExpanded = expandedNotes.has(note.id);
                const contentPreview = note.content.substring(0, 150);
                const hasMore = note.content.length > 150;

                return (
                  <Card key={note.id} variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        {/* Header */}
                        <Stack 
                          direction={{ xs: "column", sm: "row" }} 
                          justifyContent="space-between" 
                          alignItems={{ xs: "flex-start", sm: "center" }}
                          spacing={1}
                        >
                          <Box sx={{ flexGrow: 1, width: { xs: "100%", sm: "auto" } }}>
                            <Typography variant="h6" sx={{ wordBreak: "break-word" }}>
                              {note.title || "Untitled Note"}
                            </Typography>
                            {note.description && (
                              <Typography 
                                variant="body2" 
                                color="text.secondary" 
                                sx={{ mt: 0.5, wordBreak: "break-word" }}
                              >
                                {note.description}
                              </Typography>
                            )}
                          </Box>
                          
                          <Stack 
                            direction="row" 
                            spacing={1} 
                            sx={{ width: { xs: "100%", sm: "auto" } }}
                          >
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleViewNote(note)}
                              sx={{ flex: { xs: 1, sm: "unset" } }}
                              aria-label={`View note: ${note.title || 'Untitled'}`}
                            >
                              View
                            </Button>
                            <Button
                              size="small"
                              startIcon={<EditIcon />}
                              onClick={() => handleOpenNoteDialog(note)}
                              sx={{ flex: { xs: 1, sm: "unset" } }}
                              aria-label={`Edit note: ${note.title || 'Untitled'}`}
                            >
                              Edit
                            </Button>
                            <Button
                              size="small"
                              color="error"
                              startIcon={<DeleteIcon />}
                              onClick={() => handleDeleteNote(note.id)}
                              disabled={deleteNoteMutation.isPending}
                              sx={{ flex: { xs: 1, sm: "unset" } }}
                              aria-label={`Delete note: ${note.title || 'Untitled'}`}
                            >
                              Delete
                            </Button>
                          </Stack>
                        </Stack>

                        <Divider />

                        {/* Content Preview */}
                        <Box>
                          <Box 
                            className="markdown-content" 
                            sx={{ 
                              "& p:last-child": { mb: 0 },
                              maxHeight: isExpanded ? "none" : 100,
                              overflow: "hidden",
                              position: "relative"
                            }}
                          >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {isExpanded ? note.content : contentPreview + (hasMore ? "..." : "")}
                            </ReactMarkdown>
                          </Box>
                          
                          {hasMore && (
                            <Button
                              size="small"
                              onClick={() => toggleNoteExpansion(note.id)}
                              sx={{ mt: 1 }}
                            >
                              {isExpanded ? "Show Less" : "Show More"}
                            </Button>
                          )}
                        </Box>

                        {/* Footer */}
                        <Typography variant="caption" color="text.secondary">
                          Last updated: {note.updated_at ? new Date(note.updated_at).toLocaleString() : (note.created_at ? new Date(note.created_at).toLocaleString() : "N/A")}
                        </Typography>
                      </Stack>
                    </CardContent>
                  </Card>
                );
              })}
            </Stack>
          ) : (
            <Alert severity="info">
              No notes yet. Click "Add Note" to create your first note.
            </Alert>
          )}
        </Stack>
      </TabPanel>

      <TabPanel value={tabValue} index={9}>
        {/* Power Management Tab */}
        <PowerManagementControls 
          serverId={parseInt(serverId)} 
          serverName={server.name}
          userRole="admin"
        />
      </TabPanel>

      {/* Task Creation Dialog */}
      <Dialog
        open={taskDialogOpen}
        onClose={() => setTaskDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Run Remote Command</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity="warning">
              Be careful when running commands. Store output only when necessary
              to avoid exposing sensitive data.
            </Alert>
            <TextField
              label="Command"
              multiline
              minRows={3}
              fullWidth
              {...taskRegister("command")}
              error={!!taskErrors.command}
              helperText={taskErrors.command?.message}
              sx={{ fontFamily: "monospace" }}
              inputProps={{
                'aria-label': 'Command to execute on server',
              }}
            />
            <TextField
              label="Timeout (seconds)"
              type="number"
              fullWidth
              {...taskRegister("timeout_seconds", { valueAsNumber: true })}
              error={!!taskErrors.timeout_seconds}
              helperText={taskErrors.timeout_seconds?.message || "Max: 600 seconds"}
              inputProps={{
                'aria-label': 'Command timeout in seconds',
              }}
            />
            <FormControlLabel
              control={
                <Switch {...taskRegister("store_output")} />
              }
              label="Store output (stdout/stderr)"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTaskDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleTaskSubmit(onCreateTask)}
              disabled={taskIsSubmitting}
              startIcon={<PlayArrowIcon />}
              aria-label="Execute command on server"
            >
              Run Command
            </Button>
        </DialogActions>
      </Dialog>

      {/* Task Detail Dialog */}
      <Dialog
        open={!!selectedTask}
        onClose={() => setSelectedTask(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Task Details</DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Status
                </Typography>
                <Box mt={0.5}>
                  <Chip
                    label={selectedTask.status}
                    color={getTaskStatusColor(selectedTask.status)}
                    size="small"
                  />
                </Box>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Command
                </Typography>
                <Typography
                  component="pre"
                  sx={{
                    fontFamily: "monospace",
                    fontSize: "0.875rem",
                    backgroundColor: "action.hover",
                    p: 1,
                    borderRadius: 1,
                    overflowX: "auto",
                  }}
                >
                  {selectedTask.command}
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Created At
                  </Typography>
                  <Typography variant="body2">
                    {new Date(selectedTask.created_at).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Exit Code
                  </Typography>
                  <Typography variant="body2">
                    {selectedTask.exit_code ?? "N/A"}
                  </Typography>
                </Grid>
              </Grid>
              {selectedTask.stdout && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Standard Output
                  </Typography>
                  <Typography
                    component="pre"
                    sx={{
                      fontFamily: "monospace",
                      fontSize: "0.875rem",
                      backgroundColor: "action.hover",
                      p: 1,
                      borderRadius: 1,
                      overflowX: "auto",
                      maxHeight: "300px",
                      overflowY: "auto",
                    }}
                  >
                    {selectedTask.stdout}
                  </Typography>
                </Box>
              )}
              {selectedTask.stderr && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Standard Error
                  </Typography>
                  <Typography
                    component="pre"
                    sx={{
                      fontFamily: "monospace",
                      fontSize: "0.875rem",
                      backgroundColor: "error.dark",
                      color: "error.contrastText",
                      p: 1,
                      borderRadius: 1,
                      overflowX: "auto",
                      maxHeight: "300px",
                      overflowY: "auto",
                    }}
                  >
                    {selectedTask.stderr}
                  </Typography>
                </Box>
              )}
              {!selectedTask.store_output && selectedTask.status !== "running" && selectedTask.status !== "queued" && (
                <Alert severity="info">
                  Output was not stored for this task.
                </Alert>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedTask(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Note Editor Dialog */}
      <Dialog
        open={noteDialogOpen}
        onClose={() => setNoteDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingNote ? "Edit Note" : "Add Note"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={noteFormData.title}
              onChange={(e) => setNoteFormData({ ...noteFormData, title: e.target.value })}
              placeholder="Note title (optional)"
              inputProps={{
                'aria-label': 'Note title',
              }}
            />
            <TextField
              label="Description"
              fullWidth
              value={noteFormData.description}
              onChange={(e) => setNoteFormData({ ...noteFormData, description: e.target.value })}
              placeholder="Brief summary of this note"
              helperText="Optional description to help identify this note"
              inputProps={{
                'aria-label': 'Note description',
              }}
            />
            
            {/* Edit/Preview Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={noteTab} onChange={(_, v) => setNoteTab(v)}>
                <Tab label="Edit" />
                <Tab label="Preview" />
              </Tabs>
            </Box>

            {noteTab === 0 && (
              <TextField
                label="Content (Markdown supported)"
                multiline
                minRows={12}
                fullWidth
                value={noteFormData.content}
                onChange={(e) => setNoteFormData({ ...noteFormData, content: e.target.value })}
                placeholder="# Heading&#10;&#10;Your note content here..."
                helperText="Markdown formatting is supported (bold, italic, lists, code blocks, etc.)"
                inputProps={{
                  'aria-label': 'Note content in markdown format',
                }}
              />
            )}

            {noteTab === 1 && (
              <Box 
                sx={{ 
                  minHeight: 300, 
                  p: 2, 
                  border: 1, 
                  borderColor: 'divider', 
                  borderRadius: 1,
                  backgroundColor: 'background.paper',
                  overflowY: 'auto',
                  maxHeight: 500
                }}
              >
                {noteFormData.content ? (
                  <Box className="markdown-content" sx={{ "& p:last-child": { mb: 0 } }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {noteFormData.content}
                    </ReactMarkdown>
                  </Box>
                ) : (
                  <Typography color="text.secondary" fontStyle="italic">
                    No content to preview. Switch to Edit tab to add content.
                  </Typography>
                )}
              </Box>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNoteDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveNote}
            disabled={!noteFormData.content.trim() || saveNoteMutation.isPending}
            startIcon={<SaveIcon />}
            aria-label={editingNote ? "Update note" : "Save new note"}
          >
            {editingNote ? "Update" : "Save"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* File Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Upload Markdown File</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity="info">
              Upload a .md file to create a new note. The file content will be imported as the note content.
            </Alert>
            
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadFileIcon />}
              fullWidth
            >
              {uploadFile ? uploadFile.name : "Choose .md File"}
              <input
                type="file"
                hidden
                accept=".md"
                onChange={handleFileSelect}
              />
            </Button>

            {uploadFile && (
              <>
                <TextField
                  label="Title (optional)"
                  fullWidth
                  value={uploadFormData.title}
                  onChange={(e) => setUploadFormData({ ...uploadFormData, title: e.target.value })}
                  placeholder="Will use filename if not provided"
                  helperText="Optional custom title for this note"
                />
                <TextField
                  label="Description (optional)"
                  fullWidth
                  value={uploadFormData.description}
                  onChange={(e) => setUploadFormData({ ...uploadFormData, description: e.target.value })}
                  placeholder="Brief summary of this note"
                  helperText="Optional description to help identify this note"
                />
                <Alert severity="success">
                  File selected: {uploadFile.name} ({(uploadFile.size / 1024).toFixed(2)} KB)
                </Alert>
              </>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setUploadDialogOpen(false);
            setUploadFile(null);
            setUploadFormData({ title: "", description: "" });
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleFileUpload}
            disabled={!uploadFile || uploadFileMutation.isPending}
            startIcon={<UploadFileIcon />}
          >
            {uploadFileMutation.isPending ? "Uploading..." : "Upload"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Note Dialog */}
      <Dialog
        open={viewNoteDialog}
        onClose={() => setViewNoteDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {viewingNote?.title || "Untitled Note"}
        </DialogTitle>
        <DialogContent>
          {viewingNote && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              {viewingNote.description && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {viewingNote.description}
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                </Box>
              )}
              
              <Box className="markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {viewingNote.content}
                </ReactMarkdown>
              </Box>

              <Divider sx={{ my: 2 }} />
              
              <Typography variant="caption" color="text.secondary">
                Created: {viewingNote.created_at ? new Date(viewingNote.created_at).toLocaleString() : "N/A"}
                {viewingNote.updated_at && (
                  <> • Last updated: {new Date(viewingNote.updated_at).toLocaleString()}</>
                )}
              </Typography>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewNoteDialog(false)}>Close</Button>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => {
              setViewNoteDialog(false);
              if (viewingNote) handleOpenNoteDialog(viewingNote);
            }}
          >
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Note Confirmation Dialog */}
      <ConfirmDialog
        open={deleteNoteDialogOpen}
        onClose={() => {
          setDeleteNoteDialogOpen(false);
          setNoteToDelete(null);
        }}
        onConfirm={confirmDeleteNote}
        title="Delete Note"
        message="Are you sure you want to delete this note? This action cannot be undone."
        confirmText="Delete"
        severity="error"
        loading={deleteNoteMutation.isPending}
      />

      {/* Cancel Task Confirmation Dialog */}
      <ConfirmDialog
        open={cancelTaskDialogOpen}
        onClose={() => {
          setCancelTaskDialogOpen(false);
          setTaskToCancel(null);
        }}
        onConfirm={confirmCancelTask}
        title="Cancel Task"
        message="Are you sure you want to cancel this task? The task execution will be stopped."
        confirmText="Cancel Task"
        severity="warning"
        loading={cancelTaskMutation.isPending}
      />
    </Stack>
  );
}

// Agent Management Component
function AgentManagement({ serverId, server }: { serverId: string; server: Server }) {
  const [installing, setInstalling] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const queryClient = useQueryClient();
  const [uninstallConfirmOpen, setUninstallConfirmOpen] = useState(false);

  // Query agent status
  const { data: agentInfo, refetch: refetchAgentInfo } = useQuery({
    queryKey: ["agent-info", serverId],
    queryFn: async () => {
      try {
        const response = await apiFetch<{ success: boolean; running: boolean; installed: boolean; message?: string; error?: string }>(
          `/api/remote/agent/info/${serverId}`,
          { method: "POST" }
        );
        return response;
      } catch (error) {
        return { success: false, running: false, installed: false, error: (error as Error).message };
      }
    },
    refetchInterval: 10000, // Refresh every 10s
  });

  // Install agent mutation
  const installMutation = useMutation({
    mutationFn: async () => {
      setInstalling(true);
      setLogs(["Starting agent installation..."]);
      
      const response = await apiFetch<{ success: boolean; message?: string; log?: string }>(
        `/api/remote/agent/deploy/${serverId}`,
        { method: "POST" }
      );
      
      if (response.log) {
        setLogs(prev => [...prev, ...response.log!.split("\n")]);
      }
      
      return response;
    },
    onSuccess: (data) => {
      if (data.success) {
        setLogs(prev => [...prev, "✓ Agent deployed successfully"]);
        // Install with systemd
        installSystemdMutation.mutate();
      } else {
        setLogs(prev => [...prev, `✗ Failed: ${data.message}`]);
        setInstalling(false);
      }
    },
    onError: (error) => {
      setLogs(prev => [...prev, `✗ Error: ${(error as Error).message}`]);
      setInstalling(false);
    },
  });

  // Install systemd service
  const installSystemdMutation = useMutation({
    mutationFn: async () => {
      setLogs(prev => [...prev, "Installing systemd service..."]);
      const response = await apiFetch<{ success: boolean; message?: string }>(
        `/api/remote/agent/install/${serverId}`,
        { method: "POST" }
      );
      return response;
    },
    onSuccess: (data) => {
      if (data.success) {
        setLogs(prev => [...prev, "✓ Systemd service installed"]);
        // Start agent
        startMutation.mutate();
      } else {
        setLogs(prev => [...prev, `✗ Failed to install service: ${data.message}`]);
        setInstalling(false);
      }
    },
  });

  // Start agent mutation
  const startMutation = useMutation({
    mutationFn: async () => {
      setLogs(prev => [...prev, "Starting agent service..."]);
      const response = await apiFetch<{ success: boolean; message?: string }>(
        `/api/remote/agent/start/${serverId}`,
        { method: "POST" }
      );
      return response;
    },
    onSuccess: (data) => {
      if (data.success) {
        setLogs(prev => [...prev, "✓ Agent started successfully"]);
      } else {
        setLogs(prev => [...prev, `✗ Failed to start: ${data.message}`]);
      }
      setInstalling(false);
      refetchAgentInfo();
      queryClient.invalidateQueries({ queryKey: ["server", serverId] });
    },
  });

  // Stop agent mutation
  const stopMutation = useMutation({
    mutationFn: async () => {
      const response = await apiFetch<{ success: boolean; message?: string }>(
        `/api/remote/agent/stop/${serverId}`,
        { method: "POST" }
      );
      return response;
    },
    onSuccess: () => {
      refetchAgentInfo();
    },
  });

  // Uninstall agent mutation
  const uninstallMutation = useMutation({
    mutationFn: async () => {
      const response = await apiFetch<{ success: boolean; message?: string }>(
        `/api/remote/agent/uninstall/${serverId}`,
        { method: "POST" }
      );
      return response;
    },
    onSuccess: () => {
      setLogs([]);
      refetchAgentInfo();
      queryClient.invalidateQueries({ queryKey: ["server", serverId] });
      setUninstallConfirmOpen(false);
    },
  });

  const handleUninstall = () => {
    setUninstallConfirmOpen(true);
  };

  const confirmUninstall = async () => {
    await uninstallMutation.mutateAsync();
  };

  const handleInstall = () => {
    setLogs([]);
    installMutation.mutate();
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h6" gutterBottom>
          Agent Management
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Install and manage the monitoring agent on {server.name}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Agent Status Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Stack spacing={2}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Installed
                  </Typography>
                  <Box>
                    <Chip
                      label={agentInfo?.installed ? "Yes" : "No"}
                      color={agentInfo?.installed ? "success" : "default"}
                      size="small"
                    />
                  </Box>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Running
                  </Typography>
                  <Box>
                    <Chip
                      label={agentInfo?.running ? "Running" : "Stopped"}
                      color={agentInfo?.running ? "success" : "default"}
                      size="small"
                    />
                  </Box>
                </Box>
                {agentInfo?.message && (
                  <Alert severity={agentInfo.success ? "success" : "info"}>
                    {agentInfo.message}
                  </Alert>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Actions Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Actions
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Stack spacing={2}>
                {!agentInfo?.installed ? (
                  <Button
                    variant="contained"
                    onClick={handleInstall}
                    disabled={installing || installMutation.isPending}
                    aria-label={`Install monitoring agent on ${server.name}`}
                  >
                    {installing ? "Installing..." : "Install Agent"}
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="contained"
                      color={agentInfo.running ? "error" : "success"}
                      onClick={() => agentInfo.running ? stopMutation.mutate() : startMutation.mutate()}
                      disabled={stopMutation.isPending || startMutation.isPending}
                      startIcon={agentInfo.running ? <StopIcon /> : <PlayArrowIcon />}
                      aria-label={agentInfo.running ? `Stop monitoring agent on ${server.name}` : `Start monitoring agent on ${server.name}`}
                    >
                      {agentInfo.running ? "Stop Agent" : "Start Agent"}
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={handleUninstall}
                      disabled={uninstallMutation.isPending}
                      aria-label={`Uninstall monitoring agent from ${server.name}`}
                    >
                      Uninstall Agent
                    </Button>
                  </>
                )}
                <Button
                  variant="outlined"
                  onClick={() => refetchAgentInfo()}
                  startIcon={<RefreshIcon />}
                  aria-label="Refresh agent status"
                >
                  Refresh Status
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Installation Logs */}
        {logs.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Installation Log
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box
                  sx={{
                    bgcolor: "grey.900",
                    color: "common.white",
                    p: 2,
                    borderRadius: 1,
                    fontFamily: "monospace",
                    fontSize: "0.875rem",
                    maxHeight: "400px",
                    overflow: "auto",
                  }}
                >
                  {logs.map((log, index) => (
                    <Box key={index}>{log}</Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Agent Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                About the Agent
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Stack spacing={2}>
                <Typography variant="body2">
                  The monitoring agent is a lightweight Python service that collects system metrics
                  and sends them to the central server.
                </Typography>
                <Typography variant="body2">
                  <strong>Features:</strong>
                </Typography>
                <ul>
                  <li>
                    <Typography variant="body2">Real-time CPU, memory, disk, and network monitoring</Typography>
                  </li>
                  <li>
                    <Typography variant="body2">System inventory collection (OS, packages, services)</Typography>
                  </li>
                  <li>
                    <Typography variant="body2">Automatic startup with systemd</Typography>
                  </li>
                  <li>
                    <Typography variant="body2">Secure communication with the central server</Typography>
                  </li>
                </ul>
                <Alert severity="info">
                  <strong>Note:</strong> Admin or Operator role required to install agents.
                </Alert>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Uninstall Confirmation Dialog */}
      <ConfirmDialog
        open={uninstallConfirmOpen}
        onClose={() => setUninstallConfirmOpen(false)}
        onConfirm={confirmUninstall}
        title="Uninstall Agent"
        message="Are you sure you want to uninstall the agent? This will stop monitoring for this server."
        confirmText="Uninstall"
        severity="error"
        loading={uninstallMutation.isPending}
      />
    </Stack>
  );
}
