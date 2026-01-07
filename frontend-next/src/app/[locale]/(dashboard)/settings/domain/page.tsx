"use client";

import { apiFetch } from "@/lib/api-client";
import { DomainSettings } from "@/types";
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

export default function DomainSettingsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<DomainSettings>({
    queryKey: ["domain-settings"],
    queryFn: () => apiFetch<DomainSettings>("/api/domain/settings"),
  });

  const [form, setForm] = useState<Partial<DomainSettings>>({});

  const mutation = useMutation({
    mutationFn: async (payload: Partial<DomainSettings>) => {
      await apiFetch("/api/domain/settings", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["domain-settings"] }),
  });

  const handleSave = () => {
    mutation.mutate({
      domain_name: form.domain_name ?? data?.domain_name ?? "",
      ssl_enabled: form.ssl_enabled ?? data?.ssl_enabled ?? 0,
      ssl_type: form.ssl_type ?? data?.ssl_type ?? "none",
      cert_path: form.cert_path ?? data?.cert_path ?? "",
      key_path: form.key_path ?? data?.key_path ?? "",
      auto_renew: form.auto_renew ?? data?.auto_renew ?? 0,
    });
  };

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error) return <Alert severity="error">Failed to load domain settings</Alert>;

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} mb={2}>
        Domain & SSL
      </Typography>
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Domain"
                defaultValue={data?.domain_name}
                onChange={(e) => setForm((prev) => ({ ...prev, domain_name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="SSL Type"
                defaultValue={data?.ssl_type}
                onChange={(e) => setForm((prev) => ({ ...prev, ssl_type: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Certificate Path"
                defaultValue={data?.cert_path}
                onChange={(e) => setForm((prev) => ({ ...prev, cert_path: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Key Path"
                defaultValue={data?.key_path}
                onChange={(e) => setForm((prev) => ({ ...prev, key_path: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    defaultChecked={(data?.ssl_enabled ?? 0) === 1}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, ssl_enabled: e.target.checked ? 1 : 0 }))
                    }
                  />
                }
                label="Enable SSL"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    defaultChecked={(data?.auto_renew ?? 0) === 1}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, auto_renew: e.target.checked ? 1 : 0 }))
                    }
                  />
                }
                label="Auto renew"
              />
            </Grid>
            <Grid item xs={12} md={4} display="flex" justifyContent="flex-end" alignItems="center">
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
