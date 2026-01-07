"use client";

import { apiFetch } from "@/lib/api-client";
import { SSHKey } from "@/types";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  IconButton,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function SSHKeysPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<SSHKey[]>({
    queryKey: ["ssh-keys"],
    queryFn: () => apiFetch<SSHKey[]>("/api/ssh-keys"),
  });

  const [newKey, setNewKey] = useState<{ name: string; public_key: string }>({
    name: "",
    public_key: "",
  });
  const [formError, setFormError] = useState<string | null>(null);

  const addMutation = useMutation({
    mutationFn: async () => {
      if (!newKey.name || !newKey.public_key) {
        throw new Error("Name and public key are required");
      }
      await apiFetch("/api/ssh-keys", {
        method: "POST",
        body: JSON.stringify(newKey),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ssh-keys"] });
      setNewKey({ name: "", public_key: "" });
      setFormError(null);
    },
    onError: (err: unknown) =>
      setFormError(err instanceof Error ? err.message : "Failed to add key"),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiFetch(`/api/ssh-keys/${id}`, { method: "DELETE" });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ssh-keys"] }),
  });

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        SSH Keys
      </Typography>
      {isLoading && <LinearProgress />}
      {error && <Alert severity="error">Failed to load SSH keys</Alert>}

      <Grid container spacing={2}>
        {data?.map((key) => (
          <Grid item xs={12} md={6} key={key.id}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="subtitle1" fontWeight={700}>
                      {key.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {key.fingerprint}
                    </Typography>
                  </Box>
                  <IconButton onClick={() => deleteMutation.mutate(key.id)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
                <Typography variant="body2" sx={{ mt: 1 }} noWrap>
                  {key.public_key}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Add SSH Key
          </Typography>
          {formError && <Alert severity="error">{formError}</Alert>}
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Name"
                fullWidth
                value={newKey.name}
                onChange={(e) => setNewKey((prev) => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <TextField
                label="Public Key"
                fullWidth
                value={newKey.public_key}
                onChange={(e) =>
                  setNewKey((prev) => ({ ...prev, public_key: e.target.value }))
                }
              />
            </Grid>
            <Grid item xs={12} display="flex" justifyContent="flex-end">
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={() => addMutation.mutate()}
                disabled={addMutation.isPending}
              >
                Save Key
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Stack>
  );
}
