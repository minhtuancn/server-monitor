"use client";

import { apiFetch } from "@/lib/api-client";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
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
  Tooltip,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import BackupIcon from "@mui/icons-material/Backup";
import RestoreIcon from "@mui/icons-material/Restore";
import DeleteIcon from "@mui/icons-material/Delete";
import DownloadIcon from "@mui/icons-material/Download";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import StorageIcon from "@mui/icons-material/Storage";
import RefreshIcon from "@mui/icons-material/Refresh";

type BackupItem = {
  filename: string;
  path: string;
  size: number;
  size_human: string;
  created_at: string;
  encrypted: boolean;
  checksum?: string;
  timestamp?: string;
};

type BackupsResponse = {
  backups: BackupItem[];
  count: number;
};

type HealthResponse = {
  healthy: boolean;
  integrity_check: string;
  size: number;
  size_human: string;
  tables: number;
  table_details: Array<{ name: string; rows: number }>;
  page_count: number;
  page_size: number;
  foreign_key_errors: number;
  last_checked: string;
};

type StorageResponse = {
  database: {
    size: number;
    size_human: string;
  };
  backups: {
    count: number;
    total_size: number;
    size_human: string;
    average_size: number;
  };
  data_directory: {
    total_size: number;
    size_human: string;
  };
};

export default function DatabaseSettingsPage() {
  const queryClient = useQueryClient();
  const [restoreDialog, setRestoreDialog] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<BackupItem | null>(null);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [confirmText, setConfirmText] = useState("");

  // Fetch database health
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useQuery<HealthResponse>({
    queryKey: ["database-health"],
    queryFn: () => apiFetch<HealthResponse>("/api/database/health"),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch backups
  const { data: backupsData, isLoading: backupsLoading, refetch: refetchBackups } = useQuery<BackupsResponse>({
    queryKey: ["database-backups"],
    queryFn: () => apiFetch<BackupsResponse>("/api/database/backups"),
  });

  // Fetch storage stats
  const { data: storage, isLoading: storageLoading } = useQuery<StorageResponse>({
    queryKey: ["database-storage"],
    queryFn: () => apiFetch<StorageResponse>("/api/database/storage"),
  });

  // Create backup mutation
  const createBackupMutation = useMutation({
    mutationFn: () => apiFetch("/api/database/backup", { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["database-backups"] });
      queryClient.invalidateQueries({ queryKey: ["database-storage"] });
    },
  });

  // Restore backup mutation
  const restoreBackupMutation = useMutation({
    mutationFn: (filename: string) =>
      apiFetch("/api/database/restore", {
        method: "POST",
        body: JSON.stringify({ filename }),
      }),
    onSuccess: () => {
      setRestoreDialog(false);
      setSelectedBackup(null);
      queryClient.invalidateQueries({ queryKey: ["database-health"] });
    },
  });

  // Delete backup mutation
  const deleteBackupMutation = useMutation({
    mutationFn: (filename: string) =>
      apiFetch(`/api/database/backups/${filename}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["database-backups"] });
      queryClient.invalidateQueries({ queryKey: ["database-storage"] });
      setDeleteDialog(false);
      setSelectedBackup(null);
      setConfirmText("");
    },
  });

  const handleCreateBackup = () => {
    createBackupMutation.mutate();
  };

  const handleRestoreClick = (backup: BackupItem) => {
    setSelectedBackup(backup);
    setRestoreDialog(true);
  };

  const handleRestoreConfirm = () => {
    if (selectedBackup) {
      restoreBackupMutation.mutate(selectedBackup.filename);
    }
  };

  const handleDeleteClick = (backup: BackupItem) => {
    setSelectedBackup(backup);
    setDeleteDialog(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedBackup && confirmText === "DELETE") {
      deleteBackupMutation.mutate(selectedBackup.filename);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ xs: "flex-start", sm: "center" }} mb={3}>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" gutterBottom>
            Database Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Backup, restore, and monitor database health
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh data">
            <IconButton
              onClick={() => {
                refetchHealth();
                refetchBackups();
              }}
              sx={{ width: 44, height: 44 }}
              aria-label="Refresh database data"
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={createBackupMutation.isPending ? <CircularProgress size={20} /> : <BackupIcon />}
            onClick={handleCreateBackup}
            disabled={createBackupMutation.isPending}
          >
            Create Backup
          </Button>
        </Stack>
      </Stack>

      {/* Status Messages */}
      {createBackupMutation.isSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => createBackupMutation.reset()}>
          Backup created successfully
        </Alert>
      )}
      {createBackupMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => createBackupMutation.reset()}>
          Failed to create backup: {(createBackupMutation.error as Error)?.message}
        </Alert>
      )}
      {restoreBackupMutation.isSuccess && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => restoreBackupMutation.reset()}>
          Database restored successfully. Please restart services for changes to take effect.
        </Alert>
      )}
      {restoreBackupMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => restoreBackupMutation.reset()}>
          Failed to restore backup: {(restoreBackupMutation.error as Error)?.message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Database Health Card */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <StorageIcon color="primary" />
                <Typography variant="h6">Database Health</Typography>
              </Stack>

              {healthLoading ? (
                <LinearProgress />
              ) : health ? (
                <Stack spacing={2}>
                  <Box>
                    <Stack direction="row" alignItems="center" spacing={1} mb={1}>
                      {health.healthy ? (
                        <>
                          <CheckCircleIcon color="success" />
                          <Typography color="success.main" fontWeight={600}>
                            Healthy
                          </Typography>
                        </>
                      ) : (
                        <>
                          <ErrorIcon color="error" />
                          <Typography color="error.main" fontWeight={600}>
                            Issues Detected
                          </Typography>
                        </>
                      )}
                    </Stack>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Integrity Check
                      </Typography>
                      <Typography variant="body1" fontWeight={500}>
                        {health.integrity_check}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Database Size
                      </Typography>
                      <Typography variant="body1" fontWeight={500}>
                        {health.size_human}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Tables
                      </Typography>
                      <Typography variant="body1" fontWeight={500}>
                        {health.tables}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Foreign Key Errors
                      </Typography>
                      <Typography variant="body1" fontWeight={500} color={health.foreign_key_errors > 0 ? "error" : "inherit"}>
                        {health.foreign_key_errors}
                      </Typography>
                    </Grid>
                  </Grid>

                  {health.table_details && health.table_details.length > 0 && (
                    <Box>
                      <Typography variant="body2" color="text.secondary" mb={1}>
                        Table Statistics
                      </Typography>
                      <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 200 }}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Table</TableCell>
                              <TableCell align="right">Rows</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {health.table_details.map((table) => (
                              <TableRow key={table.name}>
                                <TableCell>{table.name}</TableCell>
                                <TableCell align="right">{table.rows.toLocaleString()}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                  )}

                  <Typography variant="caption" color="text.secondary">
                    Last checked: {formatDate(health.last_checked)}
                  </Typography>
                </Stack>
              ) : (
                <Typography color="text.secondary">No health data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Storage Statistics Card */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Storage Statistics
              </Typography>

              {storageLoading ? (
                <LinearProgress />
              ) : storage ? (
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      Database
                    </Typography>
                    <Typography variant="h5" fontWeight={600}>
                      {storage.database.size_human}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      Backups
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Count
                        </Typography>
                        <Typography variant="h6">{storage.backups.count}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Total Size
                        </Typography>
                        <Typography variant="h6">{storage.backups.size_human}</Typography>
                      </Grid>
                    </Grid>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      Data Directory Total
                    </Typography>
                    <Typography variant="h6" fontWeight={600}>
                      {storage.data_directory.size_human}
                    </Typography>
                  </Box>
                </Stack>
              ) : (
                <Typography color="text.secondary">No storage data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Backups List Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Backup History
              </Typography>

              {backupsLoading ? (
                <LinearProgress />
              ) : backupsData && backupsData.backups.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Filename</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Size</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {backupsData.backups.map((backup) => (
                        <TableRow key={backup.filename} hover>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {backup.filename}
                            </Typography>
                          </TableCell>
                          <TableCell>{formatDate(backup.created_at)}</TableCell>
                          <TableCell>{backup.size_human}</TableCell>
                          <TableCell>
                            <Stack direction="row" spacing={1}>
                              {backup.encrypted && <Chip label="Encrypted" size="small" color="success" />}
                              {backup.checksum && (
                                <Tooltip title={`Checksum: ${backup.checksum.substring(0, 16)}...`}>
                                  <Chip label="Verified" size="small" variant="outlined" />
                                </Tooltip>
                              )}
                            </Stack>
                          </TableCell>
                          <TableCell align="right">
                            <Stack direction="row" spacing={1} justifyContent="flex-end">
                              <Tooltip title="Restore backup">
                                <IconButton
                                  size="small"
                                  onClick={() => handleRestoreClick(backup)}
                                  disabled={restoreBackupMutation.isPending}
                                  aria-label="Restore backup"
                                >
                                  <RestoreIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Delete backup">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteClick(backup)}
                                  disabled={deleteBackupMutation.isPending}
                                  color="error"
                                  aria-label="Delete backup"
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Stack>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="info">
                  No backups found. Create your first backup to get started.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Restore Confirmation Dialog */}
      <Dialog open={restoreDialog} onClose={() => !restoreBackupMutation.isPending && setRestoreDialog(false)}>
        <DialogTitle>Restore Database Backup</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to restore from backup <strong>{selectedBackup?.filename}</strong>?
          </DialogContentText>
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2" fontWeight={600} mb={1}>
              Warning:
            </Typography>
            <Typography variant="body2">
              • Current database will be backed up automatically
              <br />
              • All services will be stopped during restore
              <br />• You will need to restart services manually after restore
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRestoreDialog(false)} disabled={restoreBackupMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleRestoreConfirm}
            variant="contained"
            color="warning"
            disabled={restoreBackupMutation.isPending}
            startIcon={restoreBackupMutation.isPending ? <CircularProgress size={20} /> : <RestoreIcon />}
          >
            Restore
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => !deleteBackupMutation.isPending && setDeleteDialog(false)}>
        <DialogTitle>Delete Backup</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete backup <strong>{selectedBackup?.filename}</strong>?
          </DialogContentText>
          <DialogContentText sx={{ mt: 2 }}>
            Type <strong>DELETE</strong> to confirm:
          </DialogContentText>
          <TextField
            fullWidth
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="DELETE"
            sx={{ mt: 2 }}
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDeleteDialog(false);
            setConfirmText("");
          }} disabled={deleteBackupMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            disabled={confirmText !== "DELETE" || deleteBackupMutation.isPending}
            startIcon={deleteBackupMutation.isPending ? <CircularProgress size={20} /> : <DeleteIcon />}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
