import { API_BASE_URL } from "@/lib/config";
import { decodeJwtPayload, isTokenExpired } from "@/lib/jwt";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const token = request.cookies.get("auth_token")?.value;
  if (!token || isTokenExpired(token)) {
    const res = NextResponse.json({ authenticated: false }, { status: 401 });
    res.cookies.set("auth_token", "", {
      path: "/",
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 0,
    });
    return res;
  }

  const verifyResponse = await fetch(`${API_BASE_URL}/api/auth/verify`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!verifyResponse.ok) {
    const res = NextResponse.json({ authenticated: false }, { status: 401 });
    res.cookies.set("auth_token", "", {
      path: "/",
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 0,
    });
    return res;
  }

  const verifyData = await verifyResponse.json();
  const payload = decodeJwtPayload(token);

  return NextResponse.json({
    authenticated: true,
    user: {
      username: verifyData.username || payload?.username,
      role: verifyData.role || payload?.role,
      permissions: payload?.permissions || [],
    },
  });
}
