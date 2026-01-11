"use client";

import { apiFetch } from "@/lib/api-client";
import { EmailConfig } from "@/types";
import SaveIcon from "@mui/icons-material/Save";
import EmailIcon from "@mui/icons-material/Email";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControlLabel,
  Grid,
  Stack,
  Switch,
  TextField,
  Typography,
  Chip,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function EmailSettingsPage() {
  const queryClient = useQueryClient();
  const [success, setSuccess] = useState(false);
  
  const { data, isLoading, error } = useQuery<EmailConfig>({
    queryKey: ["email-config"],
    queryFn: () => apiFetch<EmailConfig>("/api/email/config"),
  });

  const [form, setForm] = useState<Partial<EmailConfig>>({});

  const mutation = useMutation({
    mutationFn: async (payload: Partial<EmailConfig>) => {
      await apiFetch("/api/email/config", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["email-config"] });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    },
  });

  const handleSave = () => {
    mutation.mutate({
      enabled: form.enabled ?? data?.enabled ?? false,
      smtp_host: form.smtp_host ?? data?.smtp_host,
      smtp_port: form.smtp_port ?? data?.smtp_port,
      smtp_username: form.smtp_username ?? data?.smtp_username,
      smtp_password: form.smtp_password ?? data?.smtp_password,
      recipients: form.recipients ?? data?.recipients,
    });
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Stack spacing={3}>
        <Box>
          <Typography variant="h5" fontWeight={700}>
            Email Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure email notifications and alerts
          </Typography>
        </Box>
        <Alert severity="error">Failed to load email settings</Alert>
      </Stack>
    );
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" fontWeight={700}>
          Email Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Configure SMTP settings and email notifications for server alerts
        </Typography>
      </Box>

      {success && (
        <Alert severity="success" icon={<CheckCircleIcon />}>
          Email settings saved successfully!
        </Alert>
      )}
      
      {mutation.isError && (
        <Alert severity="error">Failed to save settings. Please try again.</Alert>
      )}

      <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
        <CardContent>
          <Stack spacing={3}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <EmailIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  SMTP Configuration
                </Typography>
              </Box>
              {data?.enabled ? (
                <Chip label="Enabled" color="success" size="small" />
              ) : (
                <Chip label="Disabled" color="default" size="small" />
              )}
            </Box>
            
            <Divider />

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      defaultChecked={!!data?.enabled}
                      onChange={(e) =>
                        setForm((prev) => ({ ...prev, enabled: e.target.checked }))
                      }
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body1" fontWeight={600}>
                        Enable Email Alerts
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Send email notifications for server alerts and issues
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  SMTP Server Details
                </Typography>
              </Grid>

              <Grid item xs={12} md={8}>
                <TextField
                  label="SMTP Host"
                  fullWidth
                  defaultValue={data?.smtp_host}
                  onChange={(e) => setForm((prev) => ({ ...prev, smtp_host: e.target.value }))}
                  placeholder="smtp.gmail.com"
                  helperText="Your SMTP server hostname"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="SMTP Port"
                  type="number"
                  fullWidth
                  defaultValue={data?.smtp_port}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, smtp_port: Number(e.target.value) }))
                  }
                  placeholder="587"
                  helperText="Usually 587 or 465"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Authentication
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="SMTP Username"
                  fullWidth
                  defaultValue={data?.smtp_username}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, smtp_username: e.target.value }))
                  }
                  placeholder="your-email@example.com"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="SMTP Password"
                  type="password"
                  fullWidth
                  defaultValue={data?.smtp_password}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, smtp_password: e.target.value }))
                  }
                  placeholder="••••••••"
                  helperText="Your SMTP password or app password"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Recipients
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label="Email Recipients"
                  fullWidth
                  multiline
                  rows={3}
                  defaultValue={data?.recipients?.join(", ")}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      recipients: e.target.value
                        .split(",")
                        .map((r) => r.trim())
                        .filter(Boolean),
                    }))
                  }
                  placeholder="admin@example.com, alerts@example.com"
                  helperText="Comma-separated list of email addresses to receive alerts"
                />
              </Grid>
            </Grid>

            <Divider />

            <Box display="flex" justifyContent="flex-end" gap={2}>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={mutation.isPending}
                size="large"
              >
                {mutation.isPending ? "Saving..." : "Save Settings"}
              </Button>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Alert severity="info" sx={{ borderRadius: 2 }}>
        <Typography variant="body2" fontWeight={600} gutterBottom>
          Gmail Users:
        </Typography>
        <Typography variant="body2">
          Use an App Password instead of your regular password. Generate one at:{" "}
          <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer">
            Google App Passwords
          </a>
        </Typography>
      </Alert>
    </Stack>
  );
}
