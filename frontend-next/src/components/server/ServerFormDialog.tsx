"use client";

import { apiFetch } from "@/lib/api-client";
import { useGroups } from "@/hooks/use-groups";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";

const serverSchema = z.object({
  name: z.string().min(1, "Name is required"),
  host: z.string().min(1, "Host is required"),
  port: z.coerce.number().min(1).max(65535).optional(),
  username: z.string().min(1, "Username is required"),
  description: z.string().optional(),
  tags: z.string().optional(),
  group_id: z.coerce.number().nullable().optional(),
});

type ServerForm = z.infer<typeof serverSchema>;

interface ServerFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingServer?: {
    id: number;
    name: string;
    host: string;
    port: number;
    username: string;
    description?: string;
    tags?: string;
    group_id?: number;
  };
}

export function ServerFormDialog({
  open,
  onClose,
  onSuccess,
  editingServer,
}: ServerFormDialogProps) {
  const [formError, setFormError] = useState<string | null>(null);
  const { data: groups = [], isLoading: groupsLoading } = useGroups("servers");

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ServerForm>({
    resolver: zodResolver(serverSchema),
    defaultValues: editingServer || {
      port: 22,
      group_id: null,
    },
  });

  const onSubmit = async (values: ServerForm) => {
    setFormError(null);
    try {
      const url = editingServer
        ? `/api/servers/${editingServer.id}`
        : "/api/servers";
      const method = editingServer ? "PUT" : "POST";

      await apiFetch(url, {
        method,
        body: JSON.stringify(values),
      });

      reset();
      onSuccess();
      onClose();
    } catch (error: any) {
      setFormError(error.message || "Failed to save server");
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>
          {editingServer ? "Edit Server" : "Add New Server"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {formError && <Alert severity="error">{formError}</Alert>}

            <TextField
              label="Server Name"
              {...register("name")}
              error={!!errors.name}
              helperText={errors.name?.message}
              fullWidth
              required
            />

            <TextField
              label="Host (IP or Hostname)"
              {...register("host")}
              error={!!errors.host}
              helperText={errors.host?.message}
              fullWidth
              required
            />

            <TextField
              label="Port"
              type="number"
              {...register("port")}
              error={!!errors.port}
              helperText={errors.port?.message}
              fullWidth
              defaultValue={22}
            />

            <TextField
              label="Username"
              {...register("username")}
              error={!!errors.username}
              helperText={errors.username?.message}
              fullWidth
              required
            />

            <TextField
              label="Description"
              {...register("description")}
              error={!!errors.description}
              helperText={errors.description?.message}
              fullWidth
              multiline
              rows={2}
            />

            <TextField
              label="Tags (comma-separated)"
              {...register("tags")}
              error={!!errors.tags}
              helperText={errors.tags?.message || "e.g., production, web, database"}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel id="group-label">Group (Optional)</InputLabel>
              <Controller
                name="group_id"
                control={control}
                render={({ field }) => (
                  <Select
                    labelId="group-label"
                    label="Group (Optional)"
                    {...field}
                    value={field.value ?? ""}
                    onChange={(e) => field.onChange(e.target.value === "" ? null : Number(e.target.value))}
                    disabled={groupsLoading}
                  >
                    <MenuItem value="">
                      <em>No Group</em>
                    </MenuItem>
                    {groups.map((group) => (
                      <MenuItem key={group.id} value={group.id}>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              borderRadius: "50%",
                              bgcolor: group.color,
                            }}
                          />
                          <span>{group.name}</span>
                        </Stack>
                      </MenuItem>
                    ))}
                  </Select>
                )}
              />
              {errors.group_id && (
                <FormHelperText error>{errors.group_id.message}</FormHelperText>
              )}
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            {editingServer ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
