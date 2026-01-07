"use client";

import { apiFetch } from "@/lib/api-client";
import { Server, ServerNote } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SaveIcon from "@mui/icons-material/Save";
import TerminalIcon from "@mui/icons-material/Terminal";
import {
  Alert,
  Button,
  Card,
  CardContent,
  Divider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { z } from "zod";

const noteSchema = z.object({
  content: z.string().min(3, "Note is too short"),
});

type NoteForm = z.infer<typeof noteSchema>;

export default function ServerDetailPage() {
  const params = useParams();
  const serverId = params?.id as string;
  const queryClient = useQueryClient();

  const { data: server, isLoading } = useQuery<Server>({
    queryKey: ["server", serverId],
    queryFn: () => apiFetch<Server>(`/api/servers/${serverId}`),
    enabled: !!serverId,
  });

  const { data: notes } = useQuery<ServerNote[]>({
    queryKey: ["server-notes", serverId],
    queryFn: () => apiFetch<ServerNote[]>(`/api/servers/${serverId}/notes`),
    enabled: !!serverId,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<NoteForm>({ resolver: zodResolver(noteSchema) });

  const onAddNote = async (values: NoteForm) => {
    await apiFetch(`/api/servers/${serverId}/notes`, {
      method: "POST",
      body: JSON.stringify(values),
    });
    reset();
    queryClient.invalidateQueries({ queryKey: ["server-notes", serverId] });
  };

  if (isLoading || !server) {
    return <Typography>Loading server...</Typography>;
  }

  return (
    <Stack spacing={3}>
      <Stack direction="row" alignItems="center" spacing={2}>
        <Button component={Link} href="../dashboard" startIcon={<ArrowBackIcon />}>
          Back
        </Button>
        <Typography variant="h5" fontWeight={700}>
          {server.name}
        </Typography>
        <Button
          component={Link}
          href={`../../terminal?server=${server.id}`}
          startIcon={<TerminalIcon />}
          variant="outlined"
          size="small"
        >
          Open Terminal
        </Button>
      </Stack>

      <Card>
        <CardContent>
          <Typography variant="h6">Details</Typography>
          <Divider sx={{ my: 2 }} />
          <Stack spacing={1}>
            <Typography>Host: {server.host}</Typography>
            <Typography>Status: {server.status || "unknown"}</Typography>
            <Typography>Description: {server.description || "N/A"}</Typography>
            <Typography>Tags: {server.tags || "N/A"}</Typography>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6">Notes</Typography>
          <Divider sx={{ my: 2 }} />
          <Stack spacing={2}>
            {notes?.length ? (
              notes.map((note) => (
                <Card key={note.id} variant="outlined">
                  <CardContent>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {note.content}
                    </ReactMarkdown>
                    <Typography variant="caption" color="text.secondary">
                      {note.updated_at || note.created_at}
                    </Typography>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Alert severity="info">No notes yet</Alert>
            )}
            <Stack spacing={2}>
              <TextField
                label="Add note (Markdown supported)"
                multiline
                minRows={4}
                {...register("content")}
                error={!!errors.content}
                helperText={errors.content?.message}
              />
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSubmit(onAddNote)}
                disabled={isSubmitting}
              >
                Save Note
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
