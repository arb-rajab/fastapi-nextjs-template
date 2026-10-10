import { NextRequest } from "next/server";

import { proxyToBackend } from "@/lib/backend";

// Generic same-origin proxy: /api/v1/<path> in the browser becomes
// <BACKEND_URL>/api/v1/<path> on the server, with the session cookie turned
// into a bearer token. Replace with per-resource handlers if you need to
// reshape requests or responses.
type Context = { params: Promise<{ path: string[] }> };

async function handle(request: NextRequest, context: Context) {
  const { path } = await context.params;
  const search = request.nextUrl.search;
  const hasBody = !["GET", "HEAD"].includes(request.method);
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  return proxyToBackend(request, `/api/v1/${path.join("/")}${search}`, {
    method: request.method,
    headers,
    body: hasBody ? await request.arrayBuffer() : undefined,
  });
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
