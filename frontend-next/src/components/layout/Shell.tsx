"use client";

import { AppShell } from "./AppShell";

export default function Shell({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
