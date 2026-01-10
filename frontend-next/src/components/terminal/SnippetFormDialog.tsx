"use client";

import { apiFetch } from "@/lib/api-client";
import { useGroups } from "@/hooks/use-groups";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
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

const snippetSchema = z.object({
  name: z.string().min(1, "Name is required"),
  command: z.string().min(1, "Command is required"),
  description: z.string().optional(),
  category: z.string().optional(),
  is_sudo: z.boolean(),
  group_id: z.coerce.number().nullable().optional(),
});

type SnippetForm = z.infer<typeof snippetSchema>;

interface SnippetFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingSnippet?: {
    id: number;
    name: string;
    command: string;
    description?: string;
    category?: string;
    is_sudo?: number;
    group_id?: number;
  };
}

export function SnippetFormDialog({
  open,
  onClose,
  onSuccess,
  editingSnippet,
}: SnippetFormDialogProps) {
  const [formError, setFormError] = useState<string | null>(null);
  const { data: groups = [], isLoading: groupsLoading } = useGroups("snippets");

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<SnippetForm>({
    resolver: zodResolver(snippetSchema),
    defaultValues: editingSnippet
      ? {
          ...editingSnippet,
          is_sudo: !!editingSnippet.is_sudo,
        }
      : {
          name: "",
          command: "",
          description: "",
          category: "general",
          is_sudo: false,
          group_id: null,
        },
  });

  const onSubmit = async (values: SnippetForm) => {
    setFormError(null);
    try {
      const url = editingSnippet
        ? `/api/snippets/${editingSnippet.id}`
        : "/api/snippets";
      const method = editingSnippet ? "PUT" : "POST";

      await apiFetch(url, {
        method,
        body: JSON.stringify({
          ...values,
          is_sudo: values.is_sudo ? 1 : 0,
        }),
      });

      reset();
      onSuccess();
      onClose();
    } catch (error: any) {
      setFormError(error.message || "Failed to save snippet");
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>
          {editingSnippet ? "Edit Command Snippet" : "Add Command Snippet"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Snippet Name"
              {...register("name")}
              error={!!errors.name}
              helperText={errors.name?.message}
              fullWidth
              required
            />

            <TextField
              label="Command"
              {...register("command")}
              error={!!errors.command}
              helperText={errors.command?.message}
              fullWidth
              required
              multiline
              rows={3}
              placeholder="ls -la"
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
              label="Category (Legacy)"
              {...register("category")}
              error={!!errors.category}
              helperText={errors.category?.message || "Use groups for better organization"}
              fullWidth
              placeholder="general, system, network, docker, etc."
            />

            <FormControl fullWidth>
              <InputLabel id="snippet-group-label">Group (Recommended)</InputLabel>
              <Controller
                name="group_id"
                control={control}
                render={({ field }) => (
                  <Select
                    labelId="snippet-group-label"
                    label="Group (Recommended)"
                    {...field}
                    value={field.value ?? ""}
                    onChange={(e) =>
                      field.onChange(e.target.value === "" ? null : Number(e.target.value))
                    }
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

            <FormControlLabel
              control={
                <Controller
                  name="is_sudo"
                  control={control}
                  render={({ field }) => (
                    <Checkbox
                      {...field}
                      checked={field.value}
                      onChange={(e) => field.onChange(e.target.checked)}
                    />
                  )}
                />
              }
              label="Requires sudo"
            />

            {formError && (
              <Box sx={{ color: "error.main", fontSize: "0.875rem" }}>
                {formError}
              </Box>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            {editingSnippet ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
