"use client";

import { MONITORING_WS_URL, TERMINAL_WS_URL } from "@/lib/config";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useState } from "react";

type CheckResult = {
  name: string;
  ok: boolean;
  detail?: string;
};

export default function SystemCheckPage() {
  const [results, setResults] = useState<CheckResult[]>([]);
  const [running, setRunning] = useState(false);

  const runChecks = async () => {
    setRunning(true);
    const newResults: CheckResult[] = [];

    try {
      const res = await fetch("/api/auth/session");
      newResults.push({
        name: "API",
        ok: res.ok,
        detail: res.ok ? "API reachable" : "API unreachable",
      });
    } catch (error: unknown) {
      const detail = error instanceof Error ? error.message : "API unreachable";
      newResults.push({ name: "API", ok: false, detail });
    }

    await Promise.all([
      new Promise<void>((resolve) => {
        const url =
          MONITORING_WS_URL || `${window.location.origin.replace("http", "ws")}/ws`;
        const ws = new WebSocket(url);
        ws.onopen = () => {
          newResults.push({ name: "Monitoring WS", ok: true });
          ws.close();
          resolve();
        };
        ws.onerror = () => {
          newResults.push({ name: "Monitoring WS", ok: false });
          resolve();
        };
      }),
      new Promise<void>((resolve) => {
        const url =
          TERMINAL_WS_URL || `${window.location.origin.replace("http", "ws")}/terminal`;
        const ws = new WebSocket(url);
        ws.onopen = () => {
          newResults.push({ name: "Terminal WS", ok: true });
          ws.close();
          resolve();
        };
        ws.onerror = () => {
          newResults.push({ name: "Terminal WS", ok: false });
          resolve();
        };
      }),
    ]);

    setResults(newResults);
    setRunning(false);
  };

  return (
    <Stack spacing={2}>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Typography variant="h5" fontWeight={700}>
          System Check
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={runChecks}
          disabled={running}
        >
          Run Checks
        </Button>
      </Box>

      {running && <LinearProgress />}

      {results.map((result) => (
        <Card key={result.name} variant="outlined">
          <CardContent
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Box>
              <Typography variant="subtitle1">{result.name}</Typography>
              {result.detail && (
                <Typography variant="body2" color="text.secondary">
                  {result.detail}
                </Typography>
              )}
            </Box>
            {result.ok ? (
              <CheckCircleIcon color="success" />
            ) : (
              <ErrorIcon color="error" />
            )}
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}
