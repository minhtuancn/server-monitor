"use client";

import { apiFetch } from "@/lib/api-client";
import { AuditLog } from "@/types";
import RefreshIcon from "@mui/icons-material/Refresh";
import InfoIcon from "@mui/icons-material/Info";
import DownloadIcon from "@mui/icons-material/Download";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Drawer,
  FormControl,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
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
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useSession } from "@/hooks/useSession";

export default function AuditLogsPage() {
  const { data: session } = useSession();
  const [actionFilter, setActionFilter] = useState<string>("");
  const [targetTypeFilter, setTargetTypeFilter] = useState<string>("");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Check if user is admin
  const isAdmin = session?.authenticated && session.user?.role === "admin";

  const queryParams = new URLSearchParams();
  if (actionFilter) queryParams.append("action", actionFilter);
  if (targetTypeFilter) queryParams.append("target_type", targetTypeFilter);
  if (startDate) queryParams.append("start_date", startDate);
  if (endDate) queryParams.append("end_date", endDate);
  queryParams.append("limit", "100");

  const { data: logsData, isLoading, error, refetch } = useQuery<{ logs: AuditLog[]; count: number }>({
    queryKey: ["audit-logs", actionFilter, targetTypeFilter, startDate, endDate],
    queryFn: () => apiFetch<{ logs: AuditLog[]; count: number }>(`/api/audit-logs?${queryParams.toString()}`),
    enabled: isAdmin, // Only fetch if user is admin
    refetchInterval: 10000, // Auto-refresh every 10 seconds
  });

  const logs = logsData?.logs || [];

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleString();
    } catch {
      return dateStr;
    }
  };

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log);
    setDrawerOpen(true);
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(logs, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    const exportFileDefaultName = `audit-logs-${new Date().toISOString()}.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  const handleExportCSV = () => {
    const headers = ["ID", "User", "Action", "Target Type", "Target ID", "IP", "Created At"];
    const csvRows = [
      headers.join(","),
      ...logs.map((log) =>
        [
          log.id,
          log.username || `User #${log.user_id}`,
          log.action,
          log.target_type || "",
          log.target_id || "",
          log.ip || "",
          log.created_at,
        ]
          .map((v) => `"${v}"`)
          .join(",")
      ),
    ];
    const csvString = csvRows.join("\n");
    const dataUri = `data:text/csv;charset=utf-8,${encodeURIComponent(csvString)}`;
    const exportFileDefaultName = `audit-logs-${new Date().toISOString()}.csv`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  if (!isAdmin) {
    return (
      <Stack spacing={3}>
        <Typography variant="h4" fontWeight={700}>
          Audit Logs
        </Typography>
        <Alert severity="error">
          Access denied. This page is only accessible to administrators.
        </Alert>
      </Stack>
    );
  }

  return (
    <Stack spacing={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4" fontWeight={700}>
            Audit Logs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View system audit trail and user activity
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Export as CSV">
            <IconButton onClick={handleExportCSV} color="primary" disabled={logs.length === 0} aria-label="Export audit logs as CSV file">
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={() => refetch()} color="primary" aria-label="Refresh audit logs">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Box display="flex" gap={2} flexWrap="wrap">
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel id="action-filter">Action</InputLabel>
                <Select
                  labelId="action-filter"
                  label="Action"
                  value={actionFilter}
                  onChange={(e) => setActionFilter(e.target.value)}
                  aria-label="Filter audit logs by action type"
                >
                  <MenuItem value="">
                    <em>All Actions</em>
                  </MenuItem>
                  <MenuItem value="ssh_key.create">SSH Key Created</MenuItem>
                  <MenuItem value="ssh_key.delete">SSH Key Deleted</MenuItem>
                  <MenuItem value="terminal.connect">Terminal Connect</MenuItem>
                  <MenuItem value="terminal.disconnect">Terminal Disconnect</MenuItem>
                  <MenuItem value="server.create">Server Created</MenuItem>
                  <MenuItem value="server.update">Server Updated</MenuItem>
                  <MenuItem value="server.delete">Server Deleted</MenuItem>
                  <MenuItem value="user.login">User Login</MenuItem>
                  <MenuItem value="user.logout">User Logout</MenuItem>
                </Select>
              </FormControl>

              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel id="target-type-filter">Target Type</InputLabel>
                <Select
                  labelId="target-type-filter"
                  label="Target Type"
                  value={targetTypeFilter}
                  onChange={(e) => setTargetTypeFilter(e.target.value)}
                  aria-label="Filter audit logs by target type"
                >
                  <MenuItem value="">
                    <em>All Types</em>
                  </MenuItem>
                  <MenuItem value="ssh_key">SSH Key</MenuItem>
                  <MenuItem value="terminal_session">Terminal Session</MenuItem>
                  <MenuItem value="server">Server</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="settings">Settings</MenuItem>
                </Select>
              </FormControl>

              <TextField
                type="date"
                label="Start Date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ minWidth: 200 }}
                inputProps={{ 'aria-label': 'Filter audit logs from start date' }}
              />

              <TextField
                type="date"
                label="End Date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ minWidth: 200 }}
                inputProps={{ 'aria-label': 'Filter audit logs until end date' }}
              />
            </Box>

            {(actionFilter || targetTypeFilter || startDate || endDate) && (
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  setActionFilter("");
                  setTargetTypeFilter("");
                  setStartDate("");
                  setEndDate("");
                }}
                aria-label="Clear all audit log filters"
              >
                Clear Filters
              </Button>
            )}
          </Stack>
        </CardContent>
      </Card>

      {isLoading && <LinearProgress />}

      {error && (
        <Alert severity="error">
          Failed to load audit logs. {error instanceof Error ? error.message : ""}
        </Alert>
      )}

      {!isLoading && !error && logs.length === 0 && (
        <Paper sx={{ p: 6, textAlign: "center" }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Audit Logs Found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No audit logs match the current filters.
          </Typography>
        </Paper>
      )}

      {!isLoading && !error && logs.length > 0 && (
        <>
          <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1}>
            <Typography variant="body2" color="text.secondary">
              Showing {logs.length} log entries
            </Typography>
            <Button variant="outlined" size="small" onClick={handleExportJSON} aria-label="Export audit logs as JSON file">
              Export JSON
            </Button>
          </Box>

          {/* Desktop Table View */}
          <TableContainer component={Paper} sx={{ display: { xs: 'none', md: 'block' } }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Timestamp</strong></TableCell>
                  <TableCell><strong>User</strong></TableCell>
                  <TableCell><strong>Action</strong></TableCell>
                  <TableCell><strong>Target</strong></TableCell>
                  <TableCell><strong>IP Address</strong></TableCell>
                  <TableCell align="right"><strong>Details</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(log.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {log.username || `User #${log.user_id}`}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {log.action}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {log.target_type || "N/A"}
                        </Typography>
                        {log.target_id && (
                          <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                            ID: {log.target_id}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" fontFamily="monospace">
                        {log.ip || "N/A"}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton onClick={() => handleViewDetails(log)} size="small" aria-label={`View details for ${log.action} by ${log.username || `User #${log.user_id}`}`}>
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Mobile Card View */}
          <Box sx={{ display: { xs: 'block', md: 'none' } }}>
            <Stack spacing={2}>
              {logs.map((log) => (
                <Card key={log.id} variant="outlined">
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box flex={1}>
                        <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                          {log.action}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {log.username || `User #${log.user_id}`}
                        </Typography>
                      </Box>
                      <IconButton 
                        onClick={() => handleViewDetails(log)} 
                        size="small" 
                        color="primary"
                        aria-label={`View details for ${log.action}`}
                      >
                        <InfoIcon />
                      </IconButton>
                    </Box>

                    <Stack spacing={1}>
                      <Box>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Timestamp
                        </Typography>
                        <Typography variant="body2">
                          {formatDate(log.created_at)}
                        </Typography>
                      </Box>

                      <Box display="flex" justifyContent="space-between" gap={2}>
                        <Box flex={1}>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Target
                          </Typography>
                          <Typography variant="body2">
                            {log.target_type || "N/A"}
                          </Typography>
                          {log.target_id && (
                            <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                              ID: {log.target_id}
                            </Typography>
                          )}
                        </Box>

                        <Box flex={1}>
                          <Typography variant="caption" color="text.secondary" display="block">
                            IP Address
                          </Typography>
                          <Typography variant="body2" fontFamily="monospace" sx={{ wordBreak: "break-all", fontSize: "0.75rem" }}>
                            {log.ip || "N/A"}
                          </Typography>
                        </Box>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Box>
        </>
      )}

      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 500, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Audit Log Details
          </Typography>
          {selectedLog && (
            <Stack spacing={2} mt={2}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Log ID
                </Typography>
                <Typography variant="body2">{selectedLog.id}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  User
                </Typography>
                <Typography variant="body2">
                  {selectedLog.username || `User #${selectedLog.user_id}`}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Action
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  {selectedLog.action}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Target Type
                </Typography>
                <Typography variant="body2">{selectedLog.target_type || "N/A"}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Target ID
                </Typography>
                <Typography variant="body2" fontFamily="monospace">
                  {selectedLog.target_id || "N/A"}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  IP Address
                </Typography>
                <Typography variant="body2" fontFamily="monospace">
                  {selectedLog.ip || "N/A"}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  User Agent
                </Typography>
                <Typography variant="body2" sx={{ wordBreak: "break-word" }}>
                  {selectedLog.user_agent || "N/A"}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Timestamp
                </Typography>
                <Typography variant="body2">{formatDate(selectedLog.created_at)}</Typography>
              </Box>
              {selectedLog.meta_json && (
                <Box>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Metadata (JSON)
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: "background.default", overflow: "auto" }}>
                    <pre style={{ margin: 0, fontSize: "0.75rem", fontFamily: "monospace" }}>
                      {JSON.stringify(JSON.parse(selectedLog.meta_json), null, 2)}
                    </pre>
                  </Paper>
                </Box>
              )}
            </Stack>
          )}
        </Box>
      </Drawer>
    </Stack>
  );
}
