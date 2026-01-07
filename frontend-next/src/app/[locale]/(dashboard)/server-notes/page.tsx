"use client";

import { apiFetch } from "@/lib/api-client";
import { Server } from "@/types";
import DescriptionIcon from "@mui/icons-material/Description";
import {
  Alert,
  Card,
  CardActionArea,
  CardContent,
  Grid,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

export default function ServerNotesIndex() {
  const { data, isLoading, error } = useQuery<Server[]>({
    queryKey: ["servers"],
    queryFn: () => apiFetch<Server[]>("/api/servers"),
  });

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        Server Notes
      </Typography>
      {isLoading && <LinearProgress />}
      {error && <Alert severity="error">Failed to load servers</Alert>}

      <Grid container spacing={2}>
        {data?.map((server) => (
          <Grid item xs={12} md={6} key={server.id}>
            <Card>
              <CardActionArea component={Link} href={`../servers/${server.id}`}>
                <CardContent>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <DescriptionIcon />
                    <Typography variant="subtitle1" fontWeight={700}>
                      {server.name}
                    </Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {server.host}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}
