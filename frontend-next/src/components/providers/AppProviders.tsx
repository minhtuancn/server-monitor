"use client";

import { CssBaseline, ThemeProvider } from "@mui/material";
import type { PaletteMode } from "@mui/material";
import { NextIntlClientProvider, type AbstractIntlMessages } from "next-intl";
import { ThemeProvider as NextThemesProvider, useTheme } from "next-themes";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { SnackbarProvider } from "../SnackbarProvider";
import { createAppTheme } from "@/theme/theme";

type Props = {
  locale: string;
  messages: AbstractIntlMessages;
  children: React.ReactNode;
};

function MuiThemeBridge({ children }: { children: React.ReactNode }) {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  
  // Fetch session to get theme_preference
  const { data: session } = useQuery({
    queryKey: ["session"],
    queryFn: async () => {
      const res = await fetch("/api/auth/session", { cache: "no-store" });
      if (!res.ok) return { authenticated: false };
      return res.json();
    },
    staleTime: 5 * 60 * 1000,
    enabled: mounted,
  });

  // Load theme from session on mount
  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (session?.authenticated && session.user?.theme_preference) {
      const savedTheme = session.user.theme_preference;
      if (savedTheme && savedTheme !== resolvedTheme) {
        setTheme(savedTheme);
      }
    }
  }, [session, setTheme, resolvedTheme]);

  const mode: PaletteMode = resolvedTheme === "dark" ? "dark" : "light";
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return null;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider>{children}</SnackbarProvider>
    </ThemeProvider>
  );
}

export function AppProviders({ locale, messages, children }: Props) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            staleTime: 15_000,
            retry: 1,
          },
          mutations: {
            retry: 1,
          },
        },
      }),
  );

  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryClientProvider client={queryClient}>
        <MuiThemeBridge>
          <NextIntlClientProvider locale={locale} messages={messages}>
            {children}
          </NextIntlClientProvider>
        </MuiThemeBridge>
      </QueryClientProvider>
    </NextThemesProvider>
  );
}
