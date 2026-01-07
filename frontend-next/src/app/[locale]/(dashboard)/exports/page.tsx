"use client";

import { downloadFile } from "@/lib/api-client";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import { Box, Button, Card, CardContent, Stack, Typography } from "@mui/material";

export default function ExportsPage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        Export Data
      </Typography>
      <Card>
        <CardContent>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Button
              variant="contained"
              startIcon={<CloudDownloadIcon />}
              onClick={() => downloadFile("/api/export/servers/csv", "servers.csv")}
            >
              Export Servers CSV
            </Button>
            <Button
              variant="outlined"
              startIcon={<CloudDownloadIcon />}
              onClick={() => downloadFile("/api/export/servers/json", "servers.json")}
            >
              Export Servers JSON
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Stack>
  );
}
