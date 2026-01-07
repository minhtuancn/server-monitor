"use client";

import { Alert, Box, Button, Card, CardContent, Stack, Typography } from "@mui/material";
import BlockIcon from "@mui/icons-material/Block";
import HomeIcon from "@mui/icons-material/Home";
import { useRouter, useSearchParams } from "next/navigation";

export default function AccessDeniedPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const from = searchParams.get("from");

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Card sx={{ maxWidth: 500, width: "100%" }}>
        <CardContent>
          <Stack spacing={3} alignItems="center" textAlign="center">
            <BlockIcon sx={{ fontSize: 80, color: "error.main" }} />
            
            <Typography variant="h4" fontWeight={700}>
              Access Denied
            </Typography>
            
            <Alert severity="error" sx={{ width: "100%" }}>
              You do not have permission to access this page.
              {from && (
                <>
                  <br />
                  <Typography variant="caption">
                    Requested: {from}
                  </Typography>
                </>
              )}
            </Alert>
            
            <Typography variant="body1" color="text.secondary">
              This page is restricted to administrators only. If you believe you should have access,
              please contact your system administrator.
            </Typography>
            
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                startIcon={<HomeIcon />}
                onClick={() => router.push("/")}
              >
                Go to Dashboard
              </Button>
              <Button
                variant="contained"
                onClick={() => router.back()}
              >
                Go Back
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
