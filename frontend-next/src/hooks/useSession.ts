"use client";

import { SessionUser } from "@/types";
import { useQuery } from "@tanstack/react-query";

type SessionResponse =
  | { authenticated: false }
  | { authenticated: true; user?: SessionUser };

export function useSession() {
  return useQuery<SessionResponse>({
    queryKey: ["session"],
    queryFn: async () => {
      const res = await fetch("/api/auth/session", { cache: "no-store" });
      if (!res.ok) {
        return { authenticated: false };
      }
      return res.json();
    },
    staleTime: 5 * 60 * 1000,
  });
}
