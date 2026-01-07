import { API_PROXY_PREFIX } from "./config";

type Options = RequestInit & { rawResponse?: boolean };

export async function apiFetch<T>(path: string, options: Options = {}) {
  const url = `${API_PROXY_PREFIX}${path.startsWith("/") ? "" : "/"}${path}`;
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.error || errorBody.detail || response.statusText);
  }

  if (options.rawResponse) {
    return response as unknown as T;
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  return (await response.text()) as unknown as T;
}

export async function downloadFile(path: string, filename: string) {
  const response = await apiFetch<Response>(path, { rawResponse: true });
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
