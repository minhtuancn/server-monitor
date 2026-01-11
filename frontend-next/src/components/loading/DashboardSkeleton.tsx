import { Box, Grid, Skeleton, Stack } from "@mui/material";

interface DashboardSkeletonProps {
  variant?: "full" | "cards-only" | "servers-only";
}

export function DashboardSkeleton({ variant = "full" }: DashboardSkeletonProps) {
  return (
    <Stack spacing={3}>
      {/* Header Skeleton */}
      {variant === "full" && (
        <Box>
          <Skeleton variant="text" width="30%" height={40} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="50%" height={24} />
        </Box>
      )}

      {/* Stats Cards Skeleton */}
      {(variant === "full" || variant === "cards-only") && (
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={4} key={i}>
              <Box
                sx={{
                  borderRadius: 2,
                  overflow: "hidden",
                  height: 120,
                }}
              >
                <Skeleton
                  variant="rectangular"
                  width="100%"
                  height="100%"
                  animation="wave"
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Server Cards Skeleton */}
      {(variant === "full" || variant === "servers-only") && (
        <Box>
          <Skeleton variant="text" width="20%" height={32} sx={{ mb: 2 }} />
          <Grid container spacing={3}>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Grid item xs={12} md={6} lg={4} key={i}>
                <Box
                  sx={{
                    borderRadius: 2,
                    p: 2,
                    border: 1,
                    borderColor: "divider",
                  }}
                >
                  <Stack spacing={2}>
                    <Box display="flex" justifyContent="space-between">
                      <Skeleton variant="text" width="40%" height={28} />
                      <Skeleton variant="rounded" width={60} height={24} />
                    </Box>
                    <Skeleton variant="text" width="60%" height={20} />
                    <Stack spacing={1}>
                      <Skeleton variant="rectangular" width="100%" height={6} sx={{ borderRadius: 1 }} />
                      <Skeleton variant="rectangular" width="100%" height={6} sx={{ borderRadius: 1 }} />
                      <Skeleton variant="rectangular" width="100%" height={6} sx={{ borderRadius: 1 }} />
                    </Stack>
                    <Box display="flex" gap={1}>
                      <Skeleton variant="rectangular" width="48%" height={36} sx={{ borderRadius: 1 }} />
                      <Skeleton variant="rectangular" width="48%" height={36} sx={{ borderRadius: 1 }} />
                    </Box>
                  </Stack>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Stack>
  );
}
