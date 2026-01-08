"use client";

import { apiFetch } from "@/lib/api-client";
import { useSession } from "@/hooks/useSession";
import { Webhook, WebhookDelivery } from "@/types";
import { useSnackbar } from "@/components/SnackbarProvider";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import VisibilityIcon from "@mui/icons-material/Visibility";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Drawer,
  FormControlLabel,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  Autocomplete,
  FormHelperText,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

// Event types for multi-select
const EVENT_TYPES = [
  "server.created",
  "server.updated",
  "server.deleted",
  "server.status_changed",
  "task.created",
  "task.started",
  "task.finished",
  "task.failed",
  "task.cancelled",
  "terminal.connect",
  "terminal.disconnect",
  "terminal.command",
  "user.login",
  "user.logout",
  "user.created",
  "user.updated",
  "user.deleted",
  "webhook.created",
  "webhook.updated",
  "webhook.deleted",
  "webhook.test",
  "alert.triggered",
  "alert.resolved",
  "settings.updated",
  "inventory.collected",
  "ssh_key.created",
  "ssh_key.deleted",
];

type WebhookFormData = {
  name: string;
  url: string;
  secret: string;
  enabled: boolean;
  event_types: string[];
  retry_max: number;
  timeout: number;
};

export default function WebhooksPage() {
  const router = useRouter();
  const { isAdmin, isLoading: sessionLoading } = useSession();
  const { showSuccess, showError } = useSnackbar();
  const queryClient = useQueryClient();

  // Redirect non-admin users
  useEffect(() => {
    if (!sessionLoading && !isAdmin) {
      router.push("/access-denied");
    }
  }, [isAdmin, sessionLoading, router]);

  // State
  const [openDialog, setOpenDialog] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState<Webhook | null>(null);
  const [openDeliveries, setOpenDeliveries] = useState(false);
  const [selectedWebhookId, setSelectedWebhookId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const [formData, setFormData] = useState<WebhookFormData>({
    name: "",
    url: "",
    secret: "",
    enabled: true,
    event_types: [],
    retry_max: 3,
    timeout: 10,
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Queries
  const { data: webhooksData, isLoading } = useQuery({
    queryKey: ["webhooks"],
    queryFn: () => apiFetch<{ webhooks: Webhook[] }>("/api/webhooks"),
    enabled: isAdmin,
  });

  const { data: deliveriesData, isLoading: deliveriesLoading } = useQuery({
    queryKey: ["webhook-deliveries", selectedWebhookId],
    queryFn: () =>
      apiFetch<{ deliveries: WebhookDelivery[] }>(
        `/api/webhooks/${selectedWebhookId}/deliveries?limit=50&offset=0`
      ),
    enabled: !!selectedWebhookId && openDeliveries,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: async (data: WebhookFormData) => {
      const payload: Record<string, unknown> = {
        name: data.name,
        url: data.url,
        enabled: data.enabled,
        event_types: data.event_types.length > 0 ? data.event_types : null,
        retry_max: data.retry_max,
        timeout: data.timeout,
      };
      if (data.secret) {
        payload.secret = data.secret;
      }
      return apiFetch("/api/webhooks", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      showSuccess("Webhook created successfully");
      handleCloseDialog();
    },
    onError: (error: Error) => {
      showError(error.message || "Failed to create webhook");
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<WebhookFormData> }) => {
      const payload: Record<string, unknown> = {};
      if (data.name !== undefined) payload.name = data.name;
      if (data.url !== undefined) payload.url = data.url;
      if (data.enabled !== undefined) payload.enabled = data.enabled;
      if (data.event_types !== undefined) {
        payload.event_types = data.event_types.length > 0 ? data.event_types : null;
      }
      if (data.retry_max !== undefined) payload.retry_max = data.retry_max;
      if (data.timeout !== undefined) payload.timeout = data.timeout;
      if (data.secret !== undefined && data.secret !== "") {
        payload.secret = data.secret;
      }
      return apiFetch(`/api/webhooks/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      showSuccess("Webhook updated successfully");
      handleCloseDialog();
    },
    onError: (error: Error) => {
      showError(error.message || "Failed to update webhook");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      return apiFetch(`/api/webhooks/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      showSuccess("Webhook deleted successfully");
      setDeleteConfirmId(null);
    },
    onError: (error: Error) => {
      showError(error.message || "Failed to delete webhook");
    },
  });

  const testMutation = useMutation({
    mutationFn: async (id: string) => {
      return apiFetch(`/api/webhooks/${id}/test`, {
        method: "POST",
      });
    },
    onSuccess: () => {
      showSuccess("Test webhook sent successfully");
    },
    onError: (error: Error) => {
      showError(error.message || "Failed to send test webhook");
    },
  });

  // Handlers
  const handleOpenDialog = (webhook?: Webhook) => {
    if (webhook) {
      setEditingWebhook(webhook);
      setFormData({
        name: webhook.name,
        url: webhook.url,
        secret: "", // Never populate secret from existing webhook
        enabled: webhook.enabled === 1,
        event_types: webhook.event_types || [],
        retry_max: webhook.retry_max,
        timeout: webhook.timeout,
      });
    } else {
      setEditingWebhook(null);
      setFormData({
        name: "",
        url: "",
        secret: "",
        enabled: true,
        event_types: [],
        retry_max: 3,
        timeout: 10,
      });
    }
    setFormErrors({});
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingWebhook(null);
    setFormData({
      name: "",
      url: "",
      secret: "",
      enabled: true,
      event_types: [],
      retry_max: 3,
      timeout: 10,
    });
    setFormErrors({});
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = "Name is required";
    }

    if (!formData.url.trim()) {
      errors.url = "URL is required";
    } else {
      try {
        const url = new URL(formData.url);
        if (!["http:", "https:"].includes(url.protocol)) {
          errors.url = "URL must be http or https";
        }
      } catch {
        errors.url = "Invalid URL format";
      }
    }

    if (formData.retry_max < 1 || formData.retry_max > 10) {
      errors.retry_max = "Retry max must be between 1 and 10";
    }

    if (formData.timeout < 1 || formData.timeout > 60) {
      errors.timeout = "Timeout must be between 1 and 60 seconds";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) {
      return;
    }

    if (editingWebhook) {
      updateMutation.mutate({ id: editingWebhook.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleViewDeliveries = (webhookId: string) => {
    setSelectedWebhookId(webhookId);
    setOpenDeliveries(true);
  };

  const webhooks = webhooksData?.webhooks || [];

  if (sessionLoading) {
    return <LinearProgress />;
  }

  if (!isAdmin) {
    return null; // Will redirect
  }

  return (
    <Stack spacing={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" fontWeight={700}>
          Webhooks Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Webhook
        </Button>
      </Box>

      <Alert severity="warning" sx={{ mb: 2 }}>
        <strong>SSRF Protection:</strong> Internal and private IP addresses are blocked.
        Only public HTTP/HTTPS URLs are allowed.
      </Alert>

      {isLoading && <LinearProgress />}

      {!isLoading && webhooks.length === 0 && (
        <Card>
          <CardContent>
            <Stack spacing={2} alignItems="center" py={4}>
              <Typography variant="h6" color="text.secondary">
                No webhooks configured
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Create a webhook to receive HTTP callbacks when events occur
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog()}
              >
                Create Your First Webhook
              </Button>
            </Stack>
          </CardContent>
        </Card>
      )}

      {!isLoading && webhooks.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>URL</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Events</TableCell>
                <TableCell>Retry/Timeout</TableCell>
                <TableCell>Last Triggered</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {webhooks.map((webhook) => (
                <TableRow key={webhook.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {webhook.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        maxWidth: 300,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {webhook.url}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={webhook.enabled ? "Enabled" : "Disabled"}
                      color={webhook.enabled ? "success" : "default"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {webhook.event_types
                        ? `${webhook.event_types.length} event${webhook.event_types.length !== 1 ? "s" : ""}`
                        : "All events"}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {webhook.retry_max} / {webhook.timeout}s
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {webhook.last_triggered_at
                        ? new Date(webhook.last_triggered_at).toLocaleString()
                        : "Never"}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} justifyContent="flex-end">
                      <Tooltip title="View Deliveries">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDeliveries(webhook.id)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Test Webhook">
                        <IconButton
                          size="small"
                          onClick={() => testMutation.mutate(webhook.id)}
                          disabled={testMutation.isPending}
                        >
                          <PlayArrowIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(webhook)}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => setDeleteConfirmId(webhook.id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingWebhook ? "Edit Webhook" : "Create Webhook"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              error={!!formErrors.name}
              helperText={formErrors.name}
              required
              fullWidth
            />

            <TextField
              label="URL"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              error={!!formErrors.url}
              helperText={formErrors.url || "Must be a public HTTP or HTTPS URL"}
              required
              fullWidth
              placeholder="https://example.com/webhook"
            />

            <Box>
              <TextField
                label="Secret"
                type="password"
                value={formData.secret}
                onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                fullWidth
                placeholder={editingWebhook ? "Leave empty to keep existing" : ""}
              />
              <FormHelperText>
                {editingWebhook
                  ? "Enter a new secret to replace the existing one, or leave empty to keep it"
                  : "Optional HMAC-SHA256 signature secret for webhook verification"}
              </FormHelperText>
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={formData.enabled}
                  onChange={(e) =>
                    setFormData({ ...formData, enabled: e.target.checked })
                  }
                />
              }
              label="Enabled"
            />

            <Autocomplete
              multiple
              options={EVENT_TYPES}
              value={formData.event_types}
              onChange={(_, newValue) =>
                setFormData({ ...formData, event_types: newValue })
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Event Types"
                  helperText="Leave empty to subscribe to all events"
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    size="small"
                    {...getTagProps({ index })}
                    key={option}
                  />
                ))
              }
            />

            <TextField
              label="Retry Max"
              type="number"
              value={formData.retry_max}
              onChange={(e) =>
                setFormData({ ...formData, retry_max: parseInt(e.target.value) || 3 })
              }
              error={!!formErrors.retry_max}
              helperText={formErrors.retry_max || "Number of retry attempts (1-10)"}
              inputProps={{ min: 1, max: 10 }}
              fullWidth
            />

            <TextField
              label="Timeout (seconds)"
              type="number"
              value={formData.timeout}
              onChange={(e) =>
                setFormData({ ...formData, timeout: parseInt(e.target.value) || 10 })
              }
              error={!!formErrors.timeout}
              helperText={formErrors.timeout || "Request timeout in seconds (1-60)"}
              inputProps={{ min: 1, max: 60 }}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={createMutation.isPending || updateMutation.isPending}
          >
            {editingWebhook ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteConfirmId}
        onClose={() => setDeleteConfirmId(null)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this webhook? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmId(null)}>Cancel</Button>
          <Button
            onClick={() => deleteConfirmId && deleteMutation.mutate(deleteConfirmId)}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Deliveries Drawer */}
      <Drawer
        anchor="right"
        open={openDeliveries}
        onClose={() => setOpenDeliveries(false)}
        PaperProps={{ sx: { width: { xs: "100%", sm: 600 } } }}
      >
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Webhook Deliveries
          </Typography>

          {deliveriesLoading && <LinearProgress />}

          {!deliveriesLoading && deliveriesData && (
            <Stack spacing={2} sx={{ mt: 2 }}>
              {deliveriesData.deliveries.length === 0 && (
                <Typography color="text.secondary">
                  No deliveries recorded yet
                </Typography>
              )}

              {deliveriesData.deliveries.map((delivery) => (
                <Card key={delivery.id} variant="outlined">
                  <CardContent>
                    <Stack spacing={1}>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2" fontWeight={600}>
                          {delivery.event_type}
                        </Typography>
                        <Chip
                          label={delivery.status}
                          color={delivery.status === "success" ? "success" : "error"}
                          size="small"
                        />
                      </Box>

                      <Typography variant="body2" color="text.secondary">
                        Status Code: {delivery.status_code || "N/A"}
                      </Typography>

                      <Typography variant="body2" color="text.secondary">
                        Attempt: {delivery.attempt}
                      </Typography>

                      <Typography variant="body2" color="text.secondary">
                        Delivered:{" "}
                        {new Date(delivery.delivered_at).toLocaleString()}
                      </Typography>

                      {delivery.error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          <Typography variant="body2" sx={{ wordBreak: "break-word" }}>
                            {delivery.error.length > 200
                              ? `${delivery.error.substring(0, 200)}...`
                              : delivery.error}
                          </Typography>
                        </Alert>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          )}
        </Box>
      </Drawer>
    </Stack>
  );
}
