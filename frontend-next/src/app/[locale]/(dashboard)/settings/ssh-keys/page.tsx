"use client";

import { apiFetch } from "@/lib/api-client";
import { SSHKey } from "@/types";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import KeyIcon from "@mui/icons-material/Key";
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Tooltip,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useSnackbar } from "@/components/SnackbarProvider";

interface NewKeyData {
  name: string;
  description: string;
  private_key: string;
}

export default function SSHKeysPage() {
  const queryClient = useQueryClient();
  const { showSnackbar } = useSnackbar();
  
  const { data: keysData, isLoading, error } = useQuery<{ keys: SSHKey[] }>({
    queryKey: ["ssh-keys"],
    queryFn: () => apiFetch<{ keys: SSHKey[] }>("/api/ssh-keys"),
  });

  const keys = keysData?.keys || [];

  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  
  const [newKey, setNewKey] = useState<NewKeyData>({
    name: "",
    description: "",
    private_key: "",
  });
  const [formError, setFormError] = useState<string | null>(null);

  const addMutation = useMutation({
    mutationFn: async () => {
      if (!newKey.name.trim() || !newKey.private_key.trim()) {
        throw new Error("Name and private key are required");
      }
      
      const trimmedKey = newKey.private_key.trim();
      if (!trimmedKey.includes("BEGIN") || !trimmedKey.includes("PRIVATE KEY")) {
        throw new Error("Invalid SSH private key format. Please paste a valid private key.");
      }

      return await apiFetch("/api/ssh-keys", {
        method: "POST",
        body: JSON.stringify({
          name: newKey.name.trim(),
          description: newKey.description.trim(),
          private_key: trimmedKey,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ssh-keys"] });
      setNewKey({ name: "", description: "", private_key: "" });
      setFormError(null);
      setOpenAddDialog(false);
      showSnackbar("SSH key created successfully", "success");
    },
    onError: (err: unknown) => {
      const errorMsg = err instanceof Error ? err.message : "Failed to add key";
      setFormError(errorMsg);
      showSnackbar(errorMsg, "error");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiFetch(`/api/ssh-keys/${id}`, { method: "DELETE" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ssh-keys"] });
      setDeleteConfirmId(null);
      showSnackbar("SSH key deleted successfully", "success");
    },
    onError: (err: unknown) => {
      const errorMsg = err instanceof Error ? err.message : "Failed to delete key";
      showSnackbar(errorMsg, "error");
    },
  });

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleString();
    } catch {
      return dateStr;
    }
  };

  const getKeyTypeColor = (keyType?: string) => {
    switch (keyType?.toLowerCase()) {
      case "ed25519": return "success";
      case "rsa": return "primary";
      case "ecdsa": return "info";
      default: return "default";
    }
  };

  return (
    <Stack spacing={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            SSH Key Vault
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Securely manage SSH private keys with AES-256-GCM encryption
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setFormError(null);
            setNewKey({ name: "", description: "", private_key: "" });
            setOpenAddDialog(true);
          }}
          disabled={isLoading}
        >
          Add SSH Key
        </Button>
      </Box>

      <Alert severity="info" icon={<KeyIcon />}>
        <Typography variant="body2" fontWeight={600}>🔒 Security Notice</Typography>
        <Typography variant="body2">
          Private keys are encrypted with AES-256-GCM and never stored in plaintext.
        </Typography>
      </Alert>

      {isLoading && <LinearProgress />}
      {error && <Alert severity="error">Failed to load SSH keys.</Alert>}

      {!isLoading && !error && keys.length === 0 && (
        <Paper sx={{ p: 6, textAlign: "center" }}>
          <KeyIcon sx={{ fontSize: 64, color: "text.disabled", mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>No SSH Keys</Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Add your first SSH private key to use for server connections
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenAddDialog(true)}
          >
            Add SSH Key
          </Button>
        </Paper>
      )}

      {!isLoading && !error && keys.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Type</strong></TableCell>
                <TableCell><strong>Fingerprint</strong></TableCell>
                <TableCell><strong>Created By</strong></TableCell>
                <TableCell><strong>Created At</strong></TableCell>
                <TableCell align="right"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {keys.map((key) => (
                <TableRow key={key.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body1" fontWeight={600}>{key.name}</Typography>
                      {key.description && (
                        <Typography variant="body2" color="text.secondary">{key.description}</Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={key.key_type?.toUpperCase() || "RSA"}
                      size="small"
                      color={getKeyTypeColor(key.key_type)}
                    />
                  </TableCell>
                  <TableCell>
                    <Tooltip title={key.fingerprint || ""}>
                      <Typography variant="body2" fontFamily="monospace"
                        sx={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                      >
                        {key.fingerprint || "N/A"}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{key.created_by || "Unknown"}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">{formatDate(key.created_at)}</Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Delete Key (Admin Only)">
                      <IconButton onClick={() => setDeleteConfirmId(key.id)} color="error" size="small">
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openAddDialog} onClose={() => !addMutation.isPending && setOpenAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add SSH Private Key</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {formError && <Alert severity="error">{formError}</Alert>}
            
            <Alert severity="warning">
              <Typography variant="body2" fontWeight={600}>⚠️ Security Warning</Typography>
              <Typography variant="body2">
                Only paste private keys you trust. Keys will be encrypted with AES-256-GCM before storage.
              </Typography>
            </Alert>

            <TextField label="Key Name" required fullWidth value={newKey.name}
              onChange={(e) => setNewKey((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Production Server Key" helperText="A unique name to identify this key"
            />

            <TextField label="Description (Optional)" fullWidth multiline rows={2} value={newKey.description}
              onChange={(e) => setNewKey((prev) => ({ ...prev, description: e.target.value }))}
              placeholder="Optional description for this key"
            />

            <TextField label="Private Key" required fullWidth multiline rows={12} value={newKey.private_key}
              onChange={(e) => setNewKey((prev) => ({ ...prev, private_key: e.target.value }))}
              placeholder="-----BEGIN OPENSSH PRIVATE KEY-----\n...\n-----END OPENSSH PRIVATE KEY-----"
              helperText="Paste your SSH private key here. Supports RSA, ED25519, ECDSA formats."
              sx={{ "& .MuiInputBase-input": { fontFamily: "monospace", fontSize: "0.875rem" } }}
            />

            <Alert severity="info">
              <Typography variant="body2">
                💡 <strong>Tip:</strong> ED25519 keys are recommended for better security and performance.
              </Typography>
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)} disabled={addMutation.isPending}>Cancel</Button>
          <Button onClick={() => { setFormError(null); addMutation.mutate(); }} variant="contained"
            disabled={addMutation.isPending || !newKey.name.trim() || !newKey.private_key.trim()}
          >
            {addMutation.isPending ? "Adding..." : "Add Key"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteConfirmId !== null} onClose={() => !deleteMutation.isPending && setDeleteConfirmId(null)}>
        <DialogTitle>Delete SSH Key?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this SSH key? This action will soft-delete the key
            and it will no longer be available for server connections.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmId(null)} disabled={deleteMutation.isPending}>Cancel</Button>
          <Button onClick={() => { if (deleteConfirmId) deleteMutation.mutate(deleteConfirmId); }}
            variant="contained" color="error" disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
