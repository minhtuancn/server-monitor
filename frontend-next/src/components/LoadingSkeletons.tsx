import { Card, CardContent, Skeleton, Stack } from "@mui/material";

export function ServerCardSkeleton() {
  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Skeleton variant="text" width="60%" height={32} />
          <Skeleton variant="text" width="40%" />
          <Stack direction="row" spacing={2}>
            <Skeleton variant="rectangular" width={80} height={60} />
            <Skeleton variant="rectangular" width={80} height={60} />
            <Skeleton variant="rectangular" width={80} height={60} />
          </Stack>
          <Skeleton variant="rectangular" width="100%" height={40} />
        </Stack>
      </CardContent>
    </Card>
  );
}

export function StatsCardSkeleton() {
  return (
    <Card>
      <CardContent>
        <Skeleton variant="text" width="40%" />
        <Skeleton variant="text" width="60%" height={48} />
        <Skeleton variant="text" width="30%" />
      </CardContent>
    </Card>
  );
}

export function TableRowSkeleton() {
  return (
    <Stack direction="row" spacing={2} py={1}>
      <Skeleton variant="text" width="20%" />
      <Skeleton variant="text" width="25%" />
      <Skeleton variant="text" width="15%" />
      <Skeleton variant="text" width="15%" />
      <Skeleton variant="text" width="15%" />
      <Skeleton variant="rectangular" width={80} height={32} />
    </Stack>
  );
}
