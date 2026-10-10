import { NextRequest, NextResponse } from "next/server";

import { SESSION_COOKIE } from "@/lib/session-cookie";

// Server-side only: the real backend, never exposed to the browser directly.
// Route handlers under app/api/** proxy to it so the browser only talks
// same-origin to this Next.js server (the backend has no CORS middleware).
export const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8010";

export function backendUnreachable(): NextResponse {
  return NextResponse.json(
    {
      error: {
        code: "backend_unreachable",
        message: "Could not reach the backend. Is it running?",
        field: null,
      },
    },
    { status: 502 },
  );
}

/**
 * Forwards a request to the backend, attaching the caller's session token as
 * `Authorization: Bearer <token>`. The token is read from this app's own
 * httpOnly cookie, never from anything page JavaScript can see or set.
 *
 * Relays the backend's status code, body and Retry-After header unchanged so
 * the browser sees the real error contract.
 */
export async function proxyToBackend(
  request: NextRequest,
  path: string,
  init?: RequestInit,
): Promise<NextResponse> {
  const token = request.cookies.get(SESSION_COOKIE)?.value;
  const headers = new Headers(init?.headers);
  if (token) headers.set("authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${BACKEND_URL}${path}`, { ...init, headers });
  } catch {
    return backendUnreachable();
  }

  const body = response.status === 204 ? null : await response.text();
  const responseHeaders = new Headers();
  const contentType = response.headers.get("content-type");
  if (contentType) responseHeaders.set("content-type", contentType);
  const retryAfter = response.headers.get("retry-after");
  if (retryAfter) responseHeaders.set("retry-after", retryAfter);

  return new NextResponse(body, { status: response.status, headers: responseHeaders });
}
