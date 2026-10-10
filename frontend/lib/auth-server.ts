import { NextRequest, NextResponse } from "next/server";

import { BACKEND_URL, backendUnreachable } from "@/lib/backend";
import { SESSION_COOKIE, sessionCookieOptions } from "@/lib/session-cookie";

// Mirrors the backend's default `jwt_access_token_expire_minutes`. Best effort
// only: the backend verifies the token's own `exp` on every request, so a
// mismatch is a stale-cookie UX question, never a security one.
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24;

interface CredentialsTokenResponse {
  access_token: string;
  username: string;
}

/**
 * Shared by app/api/auth/register and /login: proxies a username and password
 * to the backend and, on success, sets this app's httpOnly session cookie from
 * the returned token. The token never appears in the response body, so page
 * JavaScript can never read it.
 */
export async function handleCredentialsAuth(
  request: NextRequest,
  backendPath: "/api/v1/auth/register" | "/api/v1/auth/login",
  successStatus: number,
): Promise<NextResponse> {
  const requestBody = await request.text();

  let response: Response;
  try {
    response = await fetch(`${BACKEND_URL}${backendPath}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: requestBody,
    });
  } catch {
    return backendUnreachable();
  }

  const responseBody = await response.text();
  if (!response.ok) {
    const headers = new Headers({
      "content-type": response.headers.get("content-type") ?? "application/json",
    });
    const retryAfter = response.headers.get("retry-after");
    if (retryAfter) headers.set("retry-after", retryAfter);
    return new NextResponse(responseBody, { status: response.status, headers });
  }

  const { access_token: accessToken, username } = JSON.parse(
    responseBody,
  ) as CredentialsTokenResponse;

  const nextResponse = NextResponse.json({ username }, { status: successStatus });
  nextResponse.cookies.set(
    SESSION_COOKIE,
    accessToken,
    sessionCookieOptions(SESSION_MAX_AGE_SECONDS),
  );
  return nextResponse;
}
