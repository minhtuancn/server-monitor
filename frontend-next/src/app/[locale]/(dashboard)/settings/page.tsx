"use client";

import { apiFetch } from "@/lib/api-client";
import SaveIcon from "@mui/icons-material/Save";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";

type SettingsResponse = Record<string, unknown>;

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [localValues, setLocalValues] = useState<Record<string, unknown>>({});

  const { data: settings, isLoading, error } = useQuery<SettingsResponse>({
    queryKey: ["settings"],
    queryFn: () => apiFetch<SettingsResponse>("/api/settings"),
  });

  // Update local values when settings change
  useEffect(() => {
    if (settings) {
      setLocalValues(settings);
    }
  }, [settings]);

  const mutation = useMutation({
    mutationFn: async ({ key, value }: { key: string; value: unknown }) => {
      await apiFetch(`/api/settings/${key}`, {
        method: "POST",
        body: JSON.stringify({ value }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });

  const handleSave = (key: string) => {
    mutation.mutate({ key, value: localValues[key] });
  };

  if (isLoading) return <LinearProgress />;

  if (error) {
    return <Alert severity="error">Failed to load settings</Alert>;
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        System Settings
      </Typography>
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            {Object.entries(localValues || {}).map(([key, value]) => (
              <Grid item xs={12} md={6} key={key}>
                <Box display="flex" gap={1} alignItems="center">
                  <TextField
                    fullWidth
                    label={key}
                    value={value ?? ""}
                    onChange={(e) =>
                      setLocalValues((prev) => ({ ...prev, [key]: e.target.value }))
                    }
                  />
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={() => handleSave(key)}
                    disabled={mutation.isPending}
                  >
                    Save
                  </Button>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Stack>
  );
}
