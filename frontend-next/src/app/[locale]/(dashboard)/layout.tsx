"use client";

import Shell from "@/components/layout/Shell";
import { useSession } from "@/hooks/useSession";
import { useRouter, useParams } from "next/navigation";
import { useEffect } from "react";
import { Box, CircularProgress } from "@mui/material";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const params = useParams();
  const locale = (params?.locale as string) || "en";
  const { isAuthenticated, isLoading } = useSession();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/${locale}/login`);
    }
  }, [isAuthenticated, isLoading, router, locale]);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return <Shell>{children}</Shell>;
}
