"use client";

import { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Paper,
  IconButton,
  Tooltip,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import RefreshIcon from "@mui/icons-material/Refresh";
import TerminalIcon from "@mui/icons-material/Terminal";

interface TerminalSession {
  id: string;
  server_id: number;
  server_name?: string;
  user_id: number;
  username?: string;
  status: string;
  started_at: string;
  ended_at?: string;
  duration?: number;
}

export default function TerminalSessionsPage() {
  const { data: sessions, isLoading, error, refetch } = useQuery<TerminalSession[]>({
    queryKey: ["terminal-sessions"],
    queryFn: () => apiFetch<TerminalSession[]>("/api/terminal/sessions"),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "-";
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) return `${hours}h ${minutes}m ${secs}s`;
    if (minutes > 0) return `${minutes}m ${secs}s`;
    return `${secs}s`;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "success";
      case "closed":
        return "default";
      case "error":
        return "error";
      default:
        return "default";
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            <TerminalIcon sx={{ mr: 1, verticalAlign: "middle" }} />
            Terminal Sessions
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View and manage all terminal sessions
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={() => refetch()} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Card>
        <CardContent>
          {isLoading && (
            <Typography color="text.secondary">Loading sessions...</Typography>
          )}

          {error && (
            <Typography color="error">
              Error loading sessions: {error instanceof Error ? error.message : "Unknown error"}
            </Typography>
          )}

          {sessions && sessions.length === 0 && (
            <Typography color="text.secondary">No terminal sessions found</Typography>
          )}

          {sessions && sessions.length > 0 && (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Session ID</TableCell>
                    <TableCell>Server</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Started At</TableCell>
                    <TableCell>Ended At</TableCell>
                    <TableCell>Duration</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sessions.map((session) => (
                    <TableRow key={session.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {session.id.substring(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {session.server_name || `Server ${session.server_id}`}
                      </TableCell>
                      <TableCell>
                        {session.username || `User ${session.user_id}`}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={session.status}
                          color={getStatusColor(session.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{formatDate(session.started_at)}</TableCell>
                      <TableCell>{formatDate(session.ended_at)}</TableCell>
                      <TableCell>{formatDuration(session.duration)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
