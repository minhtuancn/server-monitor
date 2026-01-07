"use client";

import { apiFetch } from "@/lib/api-client";
import { TERMINAL_WS_URL } from "@/lib/config";
import { Server, SSHKey } from "@/types";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useSnackbar } from "@/components/SnackbarProvider";

export default function TerminalPage() {
  const searchParams = useSearchParams();
  const serverParam = searchParams.get("server");
  const { showSnackbar } = useSnackbar();
  
  const [serverId, setServerId] = useState<string | null>(serverParam);
  const [sshKeyId, setSshKeyId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("disconnected");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const terminalRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const termInstance = useRef<import("@xterm/xterm").Terminal | null>(null);
  const fitAddonRef = useRef<{ fit: () => void; proposeDimensions: () => { cols: number; rows: number } | undefined } | null>(null);

  const { data: servers } = useQuery<Server[]>({
    queryKey: ["servers"],
    queryFn: () => apiFetch<Server[]>("/api/servers"),
  });

  const { data: keysData } = useQuery<{ keys: SSHKey[] }>({
    queryKey: ["ssh-keys"],
    queryFn: () => apiFetch<{ keys: SSHKey[] }>("/api/ssh-keys"),
  });

  const keys = keysData?.keys || [];

  useEffect(() => {
    fetch("/api/auth/token")
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setToken(data.token))
      .catch(() => setToken(null));
  }, []);

  useEffect(() => {
    if (!serverId || !token || !terminalRef.current) return;

    const setupTerminal = async () => {
      const { Terminal } = await import("@xterm/xterm");
      const { FitAddon } = await import("@xterm/addon-fit");
      const term = new Terminal({
        cursorBlink: true,
        fontSize: 14,
        convertEol: true,
      });
      const fitAddon = new FitAddon();
      term.loadAddon(fitAddon);
      term.open(terminalRef.current!);
      fitAddon.fit();
      termInstance.current = term;
      fitAddonRef.current = fitAddon;

      const wsBase =
        TERMINAL_WS_URL || `${window.location.origin.replace("http", "ws")}/terminal`;
      const wsUrl = wsBase.startsWith("ws")
        ? wsBase
        : `${window.location.origin.replace("http", "ws")}${wsBase}`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      setStatus("connecting");

      ws.onopen = () => {
        setStatus("connected");
        const payload: any = {
          token,
          server_id: Number(serverId),
        };
        
        // Include SSH key ID if selected
        if (sshKeyId) {
          payload.ssh_key_id = sshKeyId;
        }
        
        ws.send(JSON.stringify(payload));
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "output") {
            term.write(payload.data);
          } else if (payload.type === "error") {
            term.writeln(`\r\nError: ${payload.message}`);
            setStatus("error");
            showSnackbar(payload.message || "Connection error", "error");
          } else if (payload.type === "connected") {
            term.writeln(payload.message || "Connected");
            // Extract session ID if provided
            if (payload.session_id) {
              setSessionId(payload.session_id);
            }
          }
        } catch {
          term.write(event.data);
        }
      };

      ws.onclose = () => {
        setStatus("disconnected");
        setSessionId(null);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setStatus("error");
        showSnackbar("WebSocket connection error", "error");
      };

      term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "input", data }));
        }
      });

      // Resize handler with cleanup
      const handleResize = () => {
        if (fitAddonRef.current) {
          fitAddonRef.current.fit();
          if (ws.readyState === WebSocket.OPEN) {
            const dims = fitAddonRef.current.proposeDimensions();
            if (dims) {
              ws.send(
                JSON.stringify({ type: "resize", cols: dims.cols, rows: dims.rows }),
              );
            }
          }
        }
      };

      window.addEventListener("resize", handleResize);

      // Cleanup function
      return () => {
        window.removeEventListener("resize", handleResize);
      };
    };

    const cleanup = setupTerminal();

    return () => {
      cleanup?.then((fn) => fn?.());
      wsRef.current?.close();
      termInstance.current?.dispose();
      termInstance.current = null;
      fitAddonRef.current = null;
      setSessionId(null);
    };
  }, [serverId, token, sshKeyId, showSnackbar]);

  const handleStopSession = async () => {
    if (!sessionId) return;
    
    try {
      await apiFetch(`/api/terminal/sessions/${sessionId}/stop`, {
        method: "POST",
      });
      showSnackbar("Session stopped", "success");
      wsRef.current?.close();
      setStatus("disconnected");
      setSessionId(null);
    } catch (error) {
      showSnackbar("Failed to stop session", "error");
    }
  };

  const handleConnect = () => {
    // Force reconnect by updating serverId
    setServerId(serverId);
  };

  const getStatusColor = () => {
    switch (status) {
      case "connected":
        return "success";
      case "connecting":
        return "warning";
      case "error":
        return "error";
      default:
        return "default";
    }
  };

  return (
    <Stack spacing={2}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4" fontWeight={700}>
            Web Terminal
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Connect to servers via SSH with secure key vault
          </Typography>
        </Box>
        <Chip 
          label={status.toUpperCase()} 
          color={getStatusColor()}
          size="small"
        />
      </Box>

      {!token && <Alert severity="warning">Login to start terminal session.</Alert>}
      
      {keys.length === 0 && token && (
        <Alert severity="info">
          No SSH keys found. Add SSH keys in Settings to enable terminal connections.
        </Alert>
      )}

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <FormControl fullWidth>
              <InputLabel id="server-select">Server</InputLabel>
              <Select
                labelId="server-select"
                label="Server"
                value={serverId || ""}
                onChange={(e) => setServerId(e.target.value)}
                disabled={status === "connected" || status === "connecting"}
              >
                {servers?.map((server) => (
                  <MenuItem key={server.id} value={server.id.toString()}>
                    {server.name} ({server.host})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth>
              <InputLabel id="ssh-key-select">SSH Key (Optional)</InputLabel>
              <Select
                labelId="ssh-key-select"
                label="SSH Key (Optional)"
                value={sshKeyId || ""}
                onChange={(e) => setSshKeyId(e.target.value || null)}
                disabled={status === "connected" || status === "connecting"}
              >
                <MenuItem value="">
                  <em>Use server default credentials</em>
                </MenuItem>
                {keys.map((key) => (
                  <MenuItem key={key.id} value={key.id}>
                    {key.name} ({key.key_type?.toUpperCase() || "RSA"})
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>
                Select an SSH key from the vault or use default credentials
              </FormHelperText>
            </FormControl>
            
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<PlayArrowIcon />}
                disabled={!serverId || !token || status === "connecting"}
                onClick={handleConnect}
                fullWidth
              >
                {status === "connected" ? "Reconnect" : "Connect"}
              </Button>
              
              {sessionId && status === "connected" && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={handleStopSession}
                >
                  Stop
                </Button>
              )}
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Terminal Output
            </Typography>
            {sessionId && (
              <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                Session: {sessionId.substring(0, 8)}...
              </Typography>
            )}
          </Box>
          <Box
            ref={terminalRef}
            sx={{
              backgroundColor: "black",
              minHeight: 380,
              borderRadius: 2,
              overflow: "hidden",
            }}
          />
        </CardContent>
      </Card>
    </Stack>
  );
}
