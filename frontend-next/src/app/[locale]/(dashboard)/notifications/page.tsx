"use client";

import { apiFetch } from "@/lib/api-client";
import { Alert as AlertType } from "@/types";
import {
  Alert,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";

export default function NotificationsPage() {
  const { data, isLoading, error } = useQuery<AlertType[]>({
    queryKey: ["alerts"],
    queryFn: () => apiFetch<AlertType[]>("/api/alerts"),
  });

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        Notifications
      </Typography>
      {isLoading && <LinearProgress />}
      {error && <Alert severity="error">Failed to load alerts</Alert>}

      {data?.length ? (
        data.map((alert) => (
          <Card key={alert.id} variant="outlined">
            <CardContent>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="subtitle1" fontWeight={700}>
                  {alert.message}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {alert.created_at}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Severity: {alert.severity || "info"}
              </Typography>
            </CardContent>
          </Card>
        ))
      ) : (
        <Alert severity="info">No alerts available</Alert>
      )}
    </Stack>
  );
}
