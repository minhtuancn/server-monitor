import { Box, Card, CardContent, Skeleton, Stack } from "@mui/material";

interface CardSkeletonProps {
  variant?: "default" | "list" | "stats" | "table";
  count?: number;
}

export function CardSkeleton({ variant = "default", count = 1 }: CardSkeletonProps) {
  if (variant === "stats") {
    return (
      <>
        {Array.from({ length: count }).map((_, i) => (
          <Card key={i} sx={{ borderRadius: 2 }}>
            <CardContent>
              <Skeleton variant="text" width="40%" height={24} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="60%" height={40} />
            </CardContent>
          </Card>
        ))}
      </>
    );
  }

  if (variant === "list") {
    return (
      <Card sx={{ borderRadius: 2 }}>
        <CardContent>
          <Stack spacing={2}>
            {Array.from({ length: count }).map((_, i) => (
              <Box key={i}>
                <Skeleton variant="text" width="30%" height={24} sx={{ mb: 0.5 }} />
                <Skeleton variant="text" width="80%" height={20} />
              </Box>
            ))}
          </Stack>
        </CardContent>
      </Card>
    );
  }

  if (variant === "table") {
    return (
      <Card sx={{ borderRadius: 2 }}>
        <CardContent>
          <Stack spacing={1.5}>
            <Skeleton variant="rectangular" width="100%" height={50} sx={{ borderRadius: 1 }} />
            {Array.from({ length: count }).map((_, i) => (
              <Skeleton key={i} variant="rectangular" width="100%" height={60} sx={{ borderRadius: 1 }} />
            ))}
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} sx={{ borderRadius: 2 }}>
          <CardContent>
            <Skeleton variant="text" width="40%" height={32} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" width="100%" height={120} sx={{ borderRadius: 1, mb: 2 }} />
            <Skeleton variant="text" width="60%" height={24} />
          </CardContent>
        </Card>
      ))}
    </>
  );
}
