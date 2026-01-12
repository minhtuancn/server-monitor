"use client";

import { apiFetch } from "@/lib/api-client";
import { Server } from "@/types";
import { ServerFormDialog } from "@/components/server/ServerFormDialog";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import AddIcon from "@mui/icons-material/Add";
import StorageIcon from "@mui/icons-material/Storage";
import TerminalIcon from "@mui/icons-material/Terminal";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import VisibilityIcon from "@mui/icons-material/Visibility";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  InputAdornment,
} from "@mui/material";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import SearchIcon from "@mui/icons-material/Search";
import { useParams } from "next/navigation";

export default function ServersPage() {
  const params = useParams();
  const locale = (params?.locale as string) || "en";
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingServer, setEditingServer] = useState<Server | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [serverToDelete, setServerToDelete] = useState<Server | null>(null);

  const { data: servers, isLoading } = useQuery<Server[]>({
    queryKey: ["servers"],
    queryFn: () => apiFetch<Server[]>("/api/servers"),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const deleteServerMutation = useMutation({
    mutationFn: async (serverId: number) => {
      return apiFetch(`/api/servers/${serverId}`, { method: "DELETE" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["servers"] });
    },
  });

  const handleAddServer = () => {
    setEditingServer(null);
    setDialogOpen(true);
  };

  const handleEditServer = (server: Server) => {
    setEditingServer(server);
    setDialogOpen(true);
  };

  const handleDeleteServer = async (server: Server) => {
    setServerToDelete(server);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteServer = async () => {
    if (serverToDelete) {
      await deleteServerMutation.mutateAsync(serverToDelete.id);
      setDeleteDialogOpen(false);
      setServerToDelete(null);
    }
  };

  const filteredServers = servers?.filter((server) => {
    const query = searchQuery.toLowerCase();
    return (
      server.name.toLowerCase().includes(query) ||
      server.host.toLowerCase().includes(query) ||
      server.description?.toLowerCase().includes(query) ||
      server.tags?.toLowerCase().includes(query)
    );
  });

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "online":
        return "success";
      case "offline":
        return "error";
      case "warning":
        return "warning";
      default:
        return "default";
    }
  };

  return (
    <Stack spacing={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Servers
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and monitor all your servers from one place
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddServer}
          size="large"
          aria-label="Add new server"
        >
          Add Server
        </Button>
      </Box>

      {/* Search & Filter */}
      <Card>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search servers by name, host, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            inputProps={{
              'aria-label': 'Search servers by name, host, or tags',
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      {/* Stats Cards */}
      {servers && (
        <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }} gap={2}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Total Servers
              </Typography>
              <Typography variant="h4" fontWeight={700}>
                {servers.length}
              </Typography>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Online
              </Typography>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {servers.filter(s => s.status === 'online').length}
              </Typography>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Offline
              </Typography>
              <Typography variant="h4" fontWeight={700} color="error.main">
                {servers.filter(s => s.status === 'offline').length}
              </Typography>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Unknown
              </Typography>
              <Typography variant="h4" fontWeight={700} color="text.secondary">
                {servers.filter(s => s.status === 'unknown' || !s.status).length}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Server List */}
      <Card>
        {isLoading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : filteredServers && filteredServers.length > 0 ? (
          <>
            {/* Desktop Table View */}
            <Box sx={{ display: { xs: 'none', md: 'block' } }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Host</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>CPU</TableCell>
                    <TableCell>Memory</TableCell>
                    <TableCell>Disk</TableCell>
                    <TableCell>Group</TableCell>
                    <TableCell>Tags</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredServers.map((server) => (
                    <TableRow key={server.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <StorageIcon fontSize="small" color="primary" />
                          <Typography variant="body2" fontWeight={600}>
                            {server.name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {server.host}:{server.port}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={server.status || "unknown"}
                          color={getStatusColor(server.status)}
                          size="small"
                          sx={{ minWidth: 80 }}
                        />
                      </TableCell>
                      <TableCell>
                        {server.cpu !== undefined ? (
                          <Typography
                            variant="body2"
                            color={server.cpu > 90 ? "error" : server.cpu > 75 ? "warning" : "inherit"}
                          >
                            {server.cpu.toFixed(1)}%
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {server.memory !== undefined ? (
                          <Typography
                            variant="body2"
                            color={server.memory > 90 ? "error" : server.memory > 75 ? "warning" : "inherit"}
                          >
                            {server.memory.toFixed(1)}%
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {server.disk !== undefined ? (
                          <Typography
                            variant="body2"
                            color={server.disk > 90 ? "error" : server.disk > 75 ? "warning" : "inherit"}
                          >
                            {server.disk.toFixed(1)}%
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {server.group_name ? (
                          <Chip
                            label={server.group_name}
                            size="small"
                            sx={{
                              bgcolor: server.group_color || undefined,
                              color: server.group_color ? "#fff" : undefined,
                            }}
                          />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {server.tags ? (
                          <Typography variant="caption" color="text.secondary">
                            {server.tags}
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" gap={0.5} justifyContent="flex-end">
                          <Tooltip title="View Details">
                            <IconButton
                              component={Link}
                              href={`/${locale}/servers/${server.id}`}
                              size="small"
                              color="primary"
                              aria-label={`View details for ${server.name}`}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="Terminal">
                            <IconButton
                              component={Link}
                              href={`/${locale}/terminal?server=${server.id}`}
                              size="small"
                              color="info"
                              aria-label={`Open terminal for ${server.name}`}
                            >
                              <TerminalIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              color="default"
                              onClick={() => handleEditServer(server)}
                              aria-label={`Edit ${server.name}`}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteServer(server)}
                              disabled={deleteServerMutation.isPending}
                              aria-label={`Delete ${server.name}`}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>

            {/* Mobile Card View */}
            <Box sx={{ display: { xs: 'block', md: 'none' }, p: 2 }}>
              <Stack spacing={2}>
                {filteredServers.map((server) => (
                  <Card key={server.id} variant="outlined" sx={{ borderRadius: 2 }}>
                    <CardContent>
                      <Stack spacing={2}>
                        {/* Header */}
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" gap={1}>
                          <Box flex={1} minWidth={0}>
                            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                              <StorageIcon fontSize="small" color="primary" />
                              <Typography variant="h6" fontWeight={600} noWrap>
                                {server.name}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary" fontFamily="monospace" noWrap>
                              {server.host}:{server.port}
                            </Typography>
                          </Box>
                          <Chip
                            label={server.status || "unknown"}
                            color={getStatusColor(server.status)}
                            size="small"
                          />
                        </Box>

                        {/* Metrics */}
                        <Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={1.5}>
                          <Box>
                            <Typography variant="caption" color="text.secondary" display="block">
                              CPU
                            </Typography>
                            <Typography 
                              variant="body2" 
                              fontWeight={600}
                              color={
                                server.cpu === undefined ? "text.disabled" :
                                server.cpu > 90 ? "error.main" :
                                server.cpu > 75 ? "warning.main" :
                                "success.main"
                              }
                            >
                              {server.cpu !== undefined ? `${server.cpu.toFixed(1)}%` : "N/A"}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Memory
                            </Typography>
                            <Typography 
                              variant="body2" 
                              fontWeight={600}
                              color={
                                server.memory === undefined ? "text.disabled" :
                                server.memory > 90 ? "error.main" :
                                server.memory > 75 ? "warning.main" :
                                "success.main"
                              }
                            >
                              {server.memory !== undefined ? `${server.memory.toFixed(1)}%` : "N/A"}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Disk
                            </Typography>
                            <Typography 
                              variant="body2" 
                              fontWeight={600}
                              color={
                                server.disk === undefined ? "text.disabled" :
                                server.disk > 90 ? "error.main" :
                                server.disk > 75 ? "warning.main" :
                                "success.main"
                              }
                            >
                              {server.disk !== undefined ? `${server.disk.toFixed(1)}%` : "N/A"}
                            </Typography>
                          </Box>
                        </Box>

                        {/* Group & Tags */}
                        {(server.group_name || server.tags) && (
                          <Box display="flex" gap={1} flexWrap="wrap" alignItems="center">
                            {server.group_name && (
                              <Chip
                                label={server.group_name}
                                size="small"
                                sx={{
                                  bgcolor: server.group_color || undefined,
                                  color: server.group_color ? "#fff" : undefined,
                                }}
                              />
                            )}
                            {server.tags && (
                              <Typography variant="caption" color="text.secondary">
                                {server.tags}
                              </Typography>
                            )}
                          </Box>
                        )}

                        {/* Actions */}
                        <Box display="flex" gap={1}>
                          <Button
                            component={Link}
                            href={`/${locale}/servers/${server.id}`}
                            variant="contained"
                            size="small"
                            startIcon={<VisibilityIcon />}
                            fullWidth
                            aria-label={`View details for ${server.name}`}
                          >
                            Details
                          </Button>
                          <IconButton
                            component={Link}
                            href={`/${locale}/terminal?server=${server.id}`}
                            color="primary"
                            sx={{ border: 1, borderColor: 'divider' }}
                            aria-label={`Open terminal for ${server.name}`}
                          >
                            <TerminalIcon />
                          </IconButton>
                          <IconButton
                            onClick={() => handleEditServer(server)}
                            color="default"
                            sx={{ border: 1, borderColor: 'divider' }}
                            aria-label={`Edit ${server.name}`}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            onClick={() => handleDeleteServer(server)}
                            color="error"
                            disabled={deleteServerMutation.isPending}
                            sx={{ border: 1, borderColor: 'divider' }}
                            aria-label={`Delete ${server.name}`}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          </>
        ) : (
          <Box p={4}>
            <Alert severity="info">
              {searchQuery
                ? "No servers match your search criteria."
                : "No servers found. Click 'Add Server' to get started."}
            </Alert>
          </Box>
        )}
      </Card>

      {/* Add/Edit Dialog */}
      <ServerFormDialog
        open={dialogOpen}
        onClose={() => {
          setDialogOpen(false);
          setEditingServer(null);
        }}
        server={editingServer}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setServerToDelete(null);
        }}
        onConfirm={confirmDeleteServer}
        title="Delete Server"
        message={`Are you sure you want to delete "${serverToDelete?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        severity="error"
        loading={deleteServerMutation.isPending}
      />
    </Stack>
  );
}
