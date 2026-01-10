"use client";

import { useEffect } from "react";
import { useTheme } from "next-themes";
import { useSession } from "./useSession";
import { apiFetch } from "@/lib/api-client";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Hook to sync theme changes to backend
 * Automatically saves theme preference to user account when theme changes
 */
export function useThemeSync() {
  const { resolvedTheme } = useTheme();
  const { data: session, isAuthenticated } = useSession();
  const queryClient = useQueryClient();

  useEffect(() => {
    // Only sync if user is authenticated and theme is resolved
    if (!isAuthenticated || !session?.authenticated || !resolvedTheme) {
      return;
    }

    const user = session.user;
    if (!user) return;

    // Map resolved theme to preference value
    const themePreference =
      resolvedTheme === "dark" ? "dark" : resolvedTheme === "light" ? "light" : "system";

    // Don't sync if theme hasn't changed from what's in session
    if (user.theme_preference === themePreference) {
      return;
    }

    // Sync theme to backend
    const syncTheme = async () => {
      try {
        // Get user ID from JWT token (stored in HttpOnly cookie, accessed via API)
        const response = await apiFetch(`/api/users/me`, {
          method: "PUT",
          body: JSON.stringify({ theme_preference: themePreference }),
        });

        if (response) {
          // Update session cache to reflect new theme preference
          queryClient.invalidateQueries({ queryKey: ["session"] });
        }
      } catch (error) {
        console.error("Failed to sync theme preference:", error);
      }
    };

    syncTheme();
  }, [resolvedTheme, isAuthenticated, session, queryClient]);
}
