export type JwtPayload = {
  user_id?: number;
  username?: string;
  role?: string;
  permissions?: string[];
  exp?: number;
};

export function decodeJwtPayload(token: string): JwtPayload | null {
  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const payload = parts[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded =
      typeof window === "undefined"
        ? Buffer.from(normalized, "base64").toString("utf-8")
        : atob(normalized);
    return JSON.parse(decoded);
  } catch (error) {
    console.error("Failed to decode JWT", error);
    return null;
  }
}

export function isTokenExpired(token?: string | null) {
  if (!token) return true;
  const payload = decodeJwtPayload(token);
  if (!payload?.exp) return true;
  return Date.now() >= payload.exp * 1000;
}
import { Buffer } from "buffer";
