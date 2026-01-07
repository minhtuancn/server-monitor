"use client";

import { apiFetch } from "@/lib/api-client";
import { User } from "@/types";
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
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function UsersPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<User[]>({
    queryKey: ["users"],
    queryFn: () => apiFetch<User[]>("/api/users"),
  });

  const [form, setForm] = useState<Partial<User> & { password?: string }>({
    username: "",
    email: "",
    password: "",
    role: "user",
  });
  const [formError, setFormError] = useState<string | null>(null);

  const addMutation = useMutation({
    mutationFn: async () => {
      if (!form.username || !form.password || !form.role) {
        throw new Error("Username, password, and role are required");
      }
      await apiFetch("/api/users", {
        method: "POST",
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
          role: form.role,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setFormError(null);
      setForm({ username: "", email: "", password: "", role: "user" });
    },
    onError: (err: unknown) =>
      setFormError(err instanceof Error ? err.message : "Failed to create user"),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiFetch(`/api/users/${id}`, { method: "DELETE" });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        User Management
      </Typography>
      {isLoading && <LinearProgress />}
      {error && <Alert severity="error">Failed to load users</Alert>}

      <Grid container spacing={2}>
        {data?.map((user) => (
          <Grid item xs={12} md={6} key={user.id}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" justifyContent="space-between">
                  <Box>
                    <Typography variant="subtitle1" fontWeight={700}>
                      {user.username}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {user.email}
                    </Typography>
                    <Typography variant="body2">Role: {user.role}</Typography>
                  </Box>
                  <IconButton color="error" onClick={() => deleteMutation.mutate(user.id)}>
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Add User
          </Typography>
          {formError && <Alert severity="error">{formError}</Alert>}
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Username"
                fullWidth
                value={form.username}
                onChange={(e) => setForm((prev) => ({ ...prev, username: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Email"
                fullWidth
                value={form.email}
                onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Password"
                type="password"
                fullWidth
                value={form.password}
                onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                label="Role"
                fullWidth
                value={form.role}
                onChange={(e) => setForm((prev) => ({ ...prev, role: e.target.value }))}
              >
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="user">User</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} display="flex" justifyContent="flex-end">
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={() => addMutation.mutate()}
                disabled={addMutation.isPending}
              >
                Create User
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Stack>
  );
}
