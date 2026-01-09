import { API_BASE_URL } from "@/lib/config";
import { decodeJwtPayload } from "@/lib/jwt";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { username, email, password, avatar_url } = body || {};

  if (!username || !email || !password) {
    return NextResponse.json(
      { success: false, error: "Username, email and password are required" },
      { status: 400 },
    );
  }

  const backendResponse = await fetch(`${API_BASE_URL}/api/setup/initialize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, avatar_url }),
    cache: "no-store",
  });

  if (!backendResponse.ok) {
    const error = await backendResponse.json().catch(() => ({}));
    return NextResponse.json(
      { success: false, error: error.error || "Setup failed" },
      { status: backendResponse.status },
    );
  }

  const data = await backendResponse.json();
  const token: string | undefined = data.token;
  if (!token) {
    return NextResponse.json(
      { success: false, error: "Token missing from response" },
      { status: 500 },
    );
  }

  const payload = decodeJwtPayload(token);
  const user = data.user || {
    id: payload?.user_id,
    username: payload?.username,
    role: payload?.role,
    permissions: payload?.permissions || [],
  };

  let maxAge = 60 * 60 * 8;
  if (payload?.exp) {
    const expiresIn = payload.exp - Math.floor(Date.now() / 1000);
    if (expiresIn > 0) maxAge = expiresIn;
  }

  const response = NextResponse.json({ success: true, user });
  response.cookies.set("auth_token", token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge,
  });
  return response;
}
