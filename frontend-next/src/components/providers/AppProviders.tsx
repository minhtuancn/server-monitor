"use client";

import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import type { PaletteMode } from "@mui/material";
import { NextIntlClientProvider, type AbstractIntlMessages } from "next-intl";
import { ThemeProvider as NextThemesProvider, useTheme } from "next-themes";
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useMemo, useState } from "react";

type Props = {
  locale: string;
  messages: AbstractIntlMessages;
  children: React.ReactNode;
};

function MuiThemeBridge({ children }: { children: React.ReactNode }) {
  const { resolvedTheme } = useTheme();
  const mode: PaletteMode = resolvedTheme === "dark" ? "dark" : "light";
  const theme = useMemo(
    () =>
      createTheme({
        palette: { mode },
        shape: { borderRadius: 10 },
      }),
    [mode],
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
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
      <MuiThemeBridge>
        <QueryClientProvider client={queryClient}>
          <NextIntlClientProvider locale={locale} messages={messages}>
            {children}
          </NextIntlClientProvider>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </MuiThemeBridge>
    </NextThemesProvider>
  );
}
