"use client";

import { apiFetch } from "@/lib/api-client";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import CategoryIcon from "@mui/icons-material/Category";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

interface Group {
  id: number;
  name: string;
  description?: string;
  type: "servers" | "notes" | "snippets" | "inventory";
  color?: string;
  created_at?: string;
  item_count?: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function GroupsPage() {
  const searchParams = useSearchParams();
  const initialType = searchParams.get("type") || "servers";
  const [tabValue, setTabValue] = useState(
    ["servers", "notes", "snippets", "inventory"].indexOf(initialType)
  );
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState<Group | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    color: "#1976d2",
  });
  const queryClient = useQueryClient();

  const groupTypes = ["servers", "notes", "snippets", "inventory"] as const;
  const currentType = groupTypes[tabValue];

  // Fetch groups for current type
  const { data: groups = [], isLoading } = useQuery<Group[]>({
    queryKey: ["groups", currentType],
    queryFn: async () => {
      try {
        const data = await apiFetch<Group[]>(`/api/groups?type=${currentType}`);
        return data || [];
      } catch (err) {
        console.error("Failed to fetch groups:", err);
        return [];
      }
    },
  });

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (group: Partial<Group>) => {
      if (editingGroup) {
        return apiFetch(`/api/groups/${editingGroup.id}`, {
          method: "PUT",
          body: JSON.stringify(group),
        });
      } else {
        return apiFetch("/api/groups", {
          method: "POST",
          body: JSON.stringify({ ...group, type: currentType }),
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups", currentType] });
      handleCloseDialog();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      return apiFetch(`/api/groups/${id}`, { method: "DELETE" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups", currentType] });
    },
  });

  const handleOpenDialog = (group?: Group) => {
    if (group) {
      setEditingGroup(group);
      setFormData({
        name: group.name,
        description: group.description || "",
        color: group.color || "#1976d2",
      });
    } else {
      setEditingGroup(null);
      setFormData({ name: "", description: "", color: "#1976d2" });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingGroup(null);
    setFormData({ name: "", description: "", color: "#1976d2" });
  };

  const handleSave = () => {
    if (!formData.name.trim()) return;
    saveMutation.mutate(formData);
  };

  const handleDelete = (id: number, name: string) => {
    if (confirm(`Delete group "${name}"? Items in this group will not be deleted.`)) {
      deleteMutation.mutate(id);
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      servers: "Server Groups",
      notes: "Note Groups",
      snippets: "Command Snippet Groups",
      inventory: "Inventory Groups",
    };
    return labels[type] || type;
  };

  const getTypeDescription = (type: string) => {
    const descriptions: Record<string, string> = {
      servers: "Organize servers by environment (Production, Staging, Development), location, or function",
      notes: "Categorize server notes by topic, priority, or department",
      snippets: "Group terminal commands by category (System, Network, Docker, Database, etc.)",
      inventory: "Classify inventory items by type (Hardware, Software, Network Equipment, etc.)",
    };
    return descriptions[type] || "";
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" fontWeight={700}>
          Groups Management
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Organize and categorize your servers, notes, commands, and inventory
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Server Groups" />
          <Tab label="Note Groups" />
          <Tab label="Command Snippets" />
          <Tab label="Inventory Groups" />
        </Tabs>
      </Box>

      {groupTypes.map((type, index) => (
        <TabPanel key={type} value={tabValue} index={index}>
          <Card>
            <CardContent>
              <Stack spacing={3}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h6">{getTypeLabel(type)}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {getTypeDescription(type)}
                    </Typography>
                  </Box>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                  >
                    Add Group
                  </Button>
                </Box>

                {isLoading ? (
                  <LinearProgress />
                ) : groups.length === 0 ? (
                  <Alert severity="info">
                    No groups created yet. Click "Add Group" to create your first group.
                  </Alert>
                ) : (
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Color</TableCell>
                        <TableCell>Name</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell align="center">Items</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {groups.map((group) => (
                        <TableRow key={group.id} hover>
                          <TableCell>
                            <Box
                              sx={{
                                width: 32,
                                height: 32,
                                borderRadius: 1,
                                bgcolor: group.color || "#1976d2",
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body1" fontWeight={600}>
                              {group.name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {group.description || "-"}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={group.item_count || 0}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {group.created_at
                                ? new Date(group.created_at).toLocaleDateString()
                                : "-"}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Tooltip title="Edit">
                              <IconButton
                                size="small"
                                onClick={() => handleOpenDialog(group)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDelete(group.id, group.name)}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </Stack>
            </CardContent>
          </Card>
        </TabPanel>
      ))}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingGroup ? "Edit Group" : "Create New Group"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Group Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              autoFocus
            />
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={2}
            />
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Color
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                {[
                  "#1976d2", // Blue
                  "#2e7d32", // Green
                  "#ed6c02", // Orange
                  "#d32f2f", // Red
                  "#9c27b0", // Purple
                  "#0288d1", // Light Blue
                  "#f57c00", // Deep Orange
                  "#5e35b1", // Deep Purple
                  "#c2185b", // Pink
                  "#00796b", // Teal
                ].map((color) => (
                  <Box
                    key={color}
                    onClick={() => setFormData({ ...formData, color })}
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      bgcolor: color,
                      cursor: "pointer",
                      border:
                        formData.color === color ? "3px solid #000" : "1px solid #ddd",
                      "&:hover": {
                        opacity: 0.8,
                      },
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={!formData.name.trim() || saveMutation.isPending}
          >
            {editingGroup ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>

      {saveMutation.isSuccess && (
        <Alert severity="success">
          Group {editingGroup ? "updated" : "created"} successfully!
        </Alert>
      )}
      {saveMutation.isError && (
        <Alert severity="error">Failed to save group. Please try again.</Alert>
      )}
      {deleteMutation.isError && (
        <Alert severity="error">Failed to delete group. Please try again.</Alert>
      )}
    </Stack>
  );
}
