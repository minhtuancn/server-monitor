"use client";

import { Alert, Box, Button, Card, CardContent, Stack, Typography } from "@mui/material";
import { useState } from "react";

type Result = { ok: boolean; status: number; cors?: string | null; error?: string };

export default function TestCorsPage() {
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);

  const runTest = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/stats/overview");
      const cors = res.headers.get("access-control-allow-origin");
      setResult({ ok: res.ok, status: res.status, cors });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Request failed";
      setResult({ ok: false, status: 0, error: message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        CORS Test
      </Typography>
      <Card>
        <CardContent>
          <Button variant="contained" onClick={runTest} disabled={loading}>
            {loading ? "Testing..." : "Run CORS Test"}
          </Button>
          {result && (
            <Box mt={2}>
              {result.ok ? (
                <Alert severity="success">CORS OK (status {result.status})</Alert>
              ) : (
                <Alert severity="error">Failed (status {result.status})</Alert>
              )}
              <Typography variant="body2" color="text.secondary">
                Access-Control-Allow-Origin: {result.cors || "N/A"}
              </Typography>
              {result.error && (
                <Typography variant="body2" color="error">
                  {result.error}
                </Typography>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}
