import { API_BASE_URL } from "@/lib/config";
import { NextRequest, NextResponse } from "next/server";

async function proxyRequest(request: NextRequest, path: string[]) {
  const token = request.cookies.get("auth_token")?.value;
  const targetPath = path.join("/");
  const targetUrl = new URL(`${API_BASE_URL}/${targetPath}`);
  targetUrl.search = request.nextUrl.search;

  const headers = new Headers(request.headers);
  headers.set("host", targetUrl.host);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  headers.delete("cookie");

  const isGetLike = request.method === "GET" || request.method === "HEAD";
  const contentType = request.headers.get("content-type") || "";
  let body: BodyInit | undefined;

  if (!isGetLike) {
    if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      body = formData;
    } else if (contentType.includes("application/json")) {
      const json = await request.json();
      body = JSON.stringify(json);
      headers.set("content-type", "application/json");
    } else {
      body = await request.arrayBuffer();
    }
  }

  const backendResponse = await fetch(targetUrl, {
    method: request.method,
    headers,
    body: isGetLike ? undefined : body,
    redirect: "manual",
  });

  const responseHeaders = new Headers();
  backendResponse.headers.forEach((value, key) => {
    // Skip hop-by-hop headers
    if (!["transfer-encoding", "connection"].includes(key.toLowerCase())) {
      responseHeaders.set(key, value);
    }
  });

  const response = new NextResponse(backendResponse.body, {
    status: backendResponse.status,
    headers: responseHeaders,
  });

  return response;
}

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(request, params.path);
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(request, params.path);
}

export async function PUT(request: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(request, params.path);
}

export async function PATCH(request: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(request, params.path);
}

export async function DELETE(request: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(request, params.path);
}
