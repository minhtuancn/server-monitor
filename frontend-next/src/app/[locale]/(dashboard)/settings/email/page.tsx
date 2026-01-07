"use client";

import { apiFetch } from "@/lib/api-client";
import { EmailConfig } from "@/types";
import SaveIcon from "@mui/icons-material/Save";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControlLabel,
  Grid,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function EmailSettingsPage() {
  const queryClient = useQueryClient();
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
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["email-config"] }),
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

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error) return <Alert severity="error">Failed to load email settings</Alert>;

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} mb={2}>
        Email Settings
      </Typography>
      <Card>
        <CardContent>
          <Grid container spacing={2}>
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
                label="Enable email alerts"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="SMTP Host"
                fullWidth
                defaultValue={data?.smtp_host}
                onChange={(e) => setForm((prev) => ({ ...prev, smtp_host: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="SMTP Port"
                type="number"
                fullWidth
                defaultValue={data?.smtp_port}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, smtp_port: Number(e.target.value) }))
                }
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="SMTP Username"
                fullWidth
                defaultValue={data?.smtp_username}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, smtp_username: e.target.value }))
                }
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
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Recipients (comma separated)"
                fullWidth
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
              />
            </Grid>
            <Grid item xs={12} display="flex" justifyContent="flex-end">
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={mutation.isPending}
              >
                Save
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}
