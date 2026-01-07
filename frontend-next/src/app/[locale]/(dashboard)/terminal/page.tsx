"use client";

import { apiFetch } from "@/lib/api-client";
import { TERMINAL_WS_URL } from "@/lib/config";
import { Server } from "@/types";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

export default function TerminalPage() {
  const searchParams = useSearchParams();
  const serverParam = searchParams.get("server");
  const [serverId, setServerId] = useState<string | null>(serverParam);
  const [token, setToken] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("disconnected");
  const terminalRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const termInstance = useRef<import("@xterm/xterm").Terminal | null>(null);
  const fitAddonRef = useRef<{ fit: () => void; proposeDimensions: () => { cols: number; rows: number } | undefined } | null>(null);

  const { data: servers } = useQuery<Server[]>({
    queryKey: ["servers"],
    queryFn: () => apiFetch<Server[]>("/api/servers"),
  });

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
        ws.send(
          JSON.stringify({
            token,
            server_id: Number(serverId),
          }),
        );
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "output") {
            term.write(payload.data);
          } else if (payload.type === "error") {
            term.writeln(`\r\nError: ${payload.message}`);
          } else if (payload.type === "connected") {
            term.writeln(payload.message || "Connected");
          }
        } catch {
          term.write(event.data);
        }
      };

      ws.onclose = () => {
        setStatus("disconnected");
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setStatus("error");
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
    };
  }, [serverId, token]);

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        Web Terminal
      </Typography>

      {!token && <Alert severity="warning">Login to start terminal session.</Alert>}

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
              >
                {servers?.map((server) => (
                  <MenuItem key={server.id} value={server.id.toString()}>
                    {server.name} ({server.host})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button
              variant="contained"
              startIcon={<PlayArrowIcon />}
              disabled={!serverId || !token}
              onClick={() => setServerId(serverId)}
            >
              {status === "connected" ? "Reconnect" : "Connect"}
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary" mb={1}>
            Status: {status}
          </Typography>
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
