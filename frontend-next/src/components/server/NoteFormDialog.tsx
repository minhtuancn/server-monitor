"use client";

import { apiFetch } from "@/lib/api-client";
import { useGroups } from "@/hooks/use-groups";
import { zodResolver } from "@hookform/resolvers/zod";
import {
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

const noteSchema = z.object({
  title: z.string().min(1, "Title is required"),
  content: z.string().optional(),
  group_id: z.coerce.number().nullable().optional(),
});

type NoteForm = z.infer<typeof noteSchema>;

interface NoteFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  serverId: number;
  editingNote?: {
    id: number;
    title: string;
    content?: string;
    group_id?: number;
  };
}

export function NoteFormDialog({
  open,
  onClose,
  onSuccess,
  serverId,
  editingNote,
}: NoteFormDialogProps) {
  const [formError, setFormError] = useState<string | null>(null);
  const { data: groups = [], isLoading: groupsLoading } = useGroups("notes");

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<NoteForm>({
    resolver: zodResolver(noteSchema),
    defaultValues: editingNote || {
      title: "",
      content: "",
      group_id: null,
    },
  });

  const onSubmit = async (values: NoteForm) => {
    setFormError(null);
    try {
      const url = editingNote
        ? `/api/servers/${serverId}/notes/${editingNote.id}`
        : `/api/servers/${serverId}/notes`;
      const method = editingNote ? "PUT" : "POST";

      await apiFetch(url, {
        method,
        body: JSON.stringify(values),
      });

      reset();
      onSuccess();
      onClose();
    } catch (error: any) {
      setFormError(error.message || "Failed to save note");
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>
          {editingNote ? "Edit Note" : "Add New Note"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Note Title"
              {...register("title")}
              error={!!errors.title}
              helperText={errors.title?.message}
              fullWidth
              required
            />

            <TextField
              label="Content (Markdown supported)"
              {...register("content")}
              error={!!errors.content}
              helperText={errors.content?.message}
              fullWidth
              multiline
              rows={8}
            />

            <FormControl fullWidth>
              <InputLabel id="note-group-label">Group (Optional)</InputLabel>
              <Controller
                name="group_id"
                control={control}
                render={({ field }) => (
                  <Select
                    labelId="note-group-label"
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
            {editingNote ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
