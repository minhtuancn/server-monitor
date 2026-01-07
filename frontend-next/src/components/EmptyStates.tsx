import { Alert, Box, Button, Stack, Typography } from "@mui/material";
import InboxIcon from "@mui/icons-material/Inbox";
import AddIcon from "@mui/icons-material/Add";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  title,
  description,
  icon,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight={300}
      textAlign="center"
      p={4}
    >
      <Box mb={2} sx={{ opacity: 0.5, fontSize: 80 }}>
        {icon || <InboxIcon fontSize="inherit" />}
      </Box>
      <Typography variant="h6" fontWeight={600} mb={1}>
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" mb={3} maxWidth={400}>
          {description}
        </Typography>
      )}
      {actionLabel && onAction && (
        <Button variant="contained" startIcon={<AddIcon />} onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
}

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <Stack spacing={2} alignItems="center" py={4}>
      <Alert severity="error" sx={{ width: "100%", maxWidth: 600 }}>
        <Typography variant="subtitle2" fontWeight={600} mb={1}>
          {title}
        </Typography>
        <Typography variant="body2">{message}</Typography>
      </Alert>
      {onRetry && (
        <Button variant="outlined" onClick={onRetry}>
          Retry
        </Button>
      )}
    </Stack>
  );
}
