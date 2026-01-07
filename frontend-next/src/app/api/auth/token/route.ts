import { isTokenExpired } from "@/lib/jwt";
import { NextRequest, NextResponse } from "next/server";

/**
 * Token endpoint for WebSocket authentication
 * This endpoint should only be used by WebSocket clients (terminal, monitoring)
 * and should not be cached or logged to prevent token leakage
 */
export async function GET(request: NextRequest) {
  const token = request.cookies.get("auth_token")?.value;
  
  if (!token) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }
  
  // Verify token is not expired
  if (isTokenExpired(token)) {
    return NextResponse.json({ error: "Token expired" }, { status: 401 });
  }
  
  // Return token with cache control headers to prevent caching
  const response = NextResponse.json({ token });
  response.headers.set("Cache-Control", "no-store, no-cache, must-revalidate");
  response.headers.set("Pragma", "no-cache");
  response.headers.set("Expires", "0");
  
  return response;
}
