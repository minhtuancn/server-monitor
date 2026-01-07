"use client";

import { apiFetch } from "@/lib/api-client";
import { Server, ServerNote, ServerInventory } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import RefreshIcon from "@mui/icons-material/Refresh";
import SaveIcon from "@mui/icons-material/Save";
import TerminalIcon from "@mui/icons-material/Terminal";
import StorageIcon from "@mui/icons-material/Storage";
import MemoryIcon from "@mui/icons-material/Memory";
import DnsIcon from "@mui/icons-material/Dns";
import ComputerIcon from "@mui/icons-material/Computer";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { z } from "zod";

const noteSchema = z.object({
  content: z.string().min(3, "Note is too short"),
});

type NoteForm = z.infer<typeof noteSchema>;

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
      id={\`server-tabpanel-\${index}\`}
      aria-labelledby={\`server-tab-\${index}\`}
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
  return \`\${days}d \${hours}h \${minutes}m\`;
}

export default function ServerWorkspacePage() {
  const params = useParams();
  const serverId = params?.id as string;
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);

  const { data: server, isLoading: serverLoading } = useQuery<Server>({
    queryKey: ["server", serverId],
    queryFn: () => apiFetch<Server>(\`/api/servers/\${serverId}\`),
    enabled: !!serverId,
  });

  const { data: notes, isLoading: notesLoading } = useQuery<ServerNote[]>({
    queryKey: ["server-notes", serverId],
    queryFn: () => apiFetch<ServerNote[]>(\`/api/servers/\${serverId}/notes\`),
    enabled: !!serverId,
  });

  const {
    data: inventory,
    isLoading: inventoryLoading,
    error: inventoryError,
  } = useQuery<ServerInventory>({
    queryKey: ["server-inventory", serverId],
    queryFn: () =>
      apiFetch<ServerInventory>(\`/api/servers/\${serverId}/inventory/latest\`),
    enabled: !!serverId && tabValue === 1,
    retry: false,
  });

  const refreshInventoryMutation = useMutation({
    mutationFn: async () => {
      return apiFetch(\`/api/servers/\${serverId}/inventory/refresh\`, {
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
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<NoteForm>({ resolver: zodResolver(noteSchema) });

  const onAddNote = async (values: NoteForm) => {
    await apiFetch(\`/api/servers/\${serverId}/notes\`, {
      method: "POST",
      body: JSON.stringify({ title: "Note", ...values }),
    });
    reset();
    queryClient.invalidateQueries({ queryKey: ["server-notes", serverId] });
  };

  const handleRefreshInventory = () => {
    refreshInventoryMutation.mutate();
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
      <Stack direction="row" alignItems="center" spacing={2}>
        <Button
          component={Link}
          href="../dashboard"
          startIcon={<ArrowBackIcon />}
        >
          Back
        </Button>
        <Typography variant="h5" fontWeight={700} sx={{ flexGrow: 1 }}>
          {server.name}
        </Typography>
        <Button
          component={Link}
          href={\`../../terminal?server=\${server.id}\`}
          startIcon={<TerminalIcon />}
          variant="outlined"
          size="small"
        >
          Open Terminal
        </Button>
      </Stack>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          aria-label="server workspace tabs"
        >
          <Tab label="Overview" />
          <Tab label="Inventory" />
          <Tab label="Terminal" />
          <Tab label="Notes" />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {/* Overview Tab */}
        <Grid container spacing={3}>
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

          {server.cpu !== undefined && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Current Metrics
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        CPU Usage
                      </Typography>
                      <Typography>{server.cpu}%</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Memory Usage
                      </Typography>
                      <Typography>{server.memory}%</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Disk Usage
                      </Typography>
                      <Typography>{server.disk}%</Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )}
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
                              \`\${inventory.inventory.os.name} \${inventory.inventory.os.version}\`}
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
                                ({inventory.inventory.memory.used_percent}%)
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
                                {inventory.inventory.disk.used_percent}%)
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
              href={\`../../terminal?server=\${server.id}\`}
              startIcon={<TerminalIcon />}
              variant="contained"
            >
              Open Terminal
            </Button>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        {/* Notes Tab */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Server Notes
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Stack spacing={2}>
              {notesLoading ? (
                <CircularProgress />
              ) : notes && notes.length > 0 ? (
                notes.map((note) => (
                  <Card key={note.id} variant="outlined">
                    <CardContent>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {note.content}
                      </ReactMarkdown>
                      <Typography variant="caption" color="text.secondary">
                        {note.updated_at || note.created_at}
                      </Typography>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Alert severity="info">No notes yet</Alert>
              )}
              <Divider />
              <Typography variant="subtitle2">Add New Note</Typography>
              <TextField
                label="Note content (Markdown supported)"
                multiline
                minRows={4}
                {...register("content")}
                error={!!errors.content}
                helperText={errors.content?.message}
              />
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSubmit(onAddNote)}
                disabled={isSubmitting}
              >
                Save Note
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>
    </Stack>
  );
}
