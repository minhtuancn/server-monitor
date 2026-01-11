"use client";

import { apiFetch } from "@/lib/api-client";
import { DomainSettings } from "@/types";
import SaveIcon from "@mui/icons-material/Save";
import PublicIcon from "@mui/icons-material/Public";
import LockIcon from "@mui/icons-material/Lock";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function DomainSettingsPage() {
  const queryClient = useQueryClient();
  const [success, setSuccess] = useState(false);
  
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["domain-settings"] });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    },
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
            Domain & SSL Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure custom domain and SSL certificates
          </Typography>
        </Box>
        <Alert severity="error">Failed to load domain settings. Please try again.</Alert>
      </Stack>
    );
  }

  const sslEnabled = (form.ssl_enabled ?? data?.ssl_enabled ?? 0) === 1;

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" fontWeight={700}>
          Domain & SSL Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Configure custom domain name and SSL certificate settings
        </Typography>
      </Box>

      {success && (
        <Alert severity="success" icon={<CheckCircleIcon />}>
          Domain settings saved successfully!
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
                <PublicIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Domain Configuration
                </Typography>
              </Box>
              {data?.domain_name && (
                <Chip label="Custom Domain" color="primary" size="small" />
              )}
            </Box>
            
            <Divider />

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Domain Name"
                  defaultValue={data?.domain_name}
                  onChange={(e) => setForm((prev) => ({ ...prev, domain_name: e.target.value }))}
                  placeholder="example.com"
                  helperText="Your custom domain name (without http:// or https://)"
                />
              </Grid>
            </Grid>
          </Stack>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
        <CardContent>
          <Stack spacing={3}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <LockIcon color="success" />
                <Typography variant="h6" fontWeight={600}>
                  SSL/TLS Configuration
                </Typography>
              </Box>
              {sslEnabled ? (
                <Chip label="SSL Enabled" color="success" size="small" />
              ) : (
                <Chip label="SSL Disabled" color="default" size="small" />
              )}
            </Box>
            
            <Divider />

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      defaultChecked={(data?.ssl_enabled ?? 0) === 1}
                      onChange={(e) =>
                        setForm((prev) => ({ ...prev, ssl_enabled: e.target.checked ? 1 : 0 }))
                      }
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body1" fontWeight={600}>
                        Enable SSL/TLS
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Use HTTPS with SSL certificate for secure connections
                      </Typography>
                    </Box>
                  }
                />
              </Grid>

              {sslEnabled && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      SSL Certificate Type
                    </Typography>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>SSL Type</InputLabel>
                      <Select
                        value={form.ssl_type ?? data?.ssl_type ?? "none"}
                        label="SSL Type"
                        onChange={(e) => setForm((prev) => ({ ...prev, ssl_type: e.target.value }))}
                      >
                        <MenuItem value="none">None</MenuItem>
                        <MenuItem value="letsencrypt">Let's Encrypt (Free)</MenuItem>
                        <MenuItem value="custom">Custom Certificate</MenuItem>
                        <MenuItem value="cloudflare">Cloudflare</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          defaultChecked={(data?.auto_renew ?? 0) === 1}
                          onChange={(e) =>
                            setForm((prev) => ({ ...prev, auto_renew: e.target.checked ? 1 : 0 }))
                          }
                        />
                      }
                      label={
                        <Box>
                          <Typography variant="body1" fontWeight={600}>
                            Auto Renew
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Automatically renew SSL certificate
                          </Typography>
                        </Box>
                      }
                    />
                  </Grid>

                  {(form.ssl_type ?? data?.ssl_type) === "custom" && (
                    <>
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Certificate Files
                        </Typography>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Certificate Path"
                          defaultValue={data?.cert_path}
                          onChange={(e) => setForm((prev) => ({ ...prev, cert_path: e.target.value }))}
                          placeholder="/path/to/certificate.crt"
                          helperText="Full path to SSL certificate file"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Private Key Path"
                          defaultValue={data?.key_path}
                          onChange={(e) => setForm((prev) => ({ ...prev, key_path: e.target.value }))}
                          placeholder="/path/to/private.key"
                          helperText="Full path to private key file"
                        />
                      </Grid>
                    </>
                  )}
                </>
              )}
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
          💡 SSL/TLS Best Practices:
        </Typography>
        <Typography variant="body2" component="div">
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>Let's Encrypt provides free SSL certificates with auto-renewal</li>
            <li>Always use HTTPS in production environments</li>
            <li>Keep your SSL certificates up to date</li>
            <li>Use strong cipher suites (TLS 1.2 or higher)</li>
          </ul>
        </Typography>
      </Alert>
    </Stack>
  );
}
