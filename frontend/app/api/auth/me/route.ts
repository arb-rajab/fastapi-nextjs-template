import { NextRequest } from "next/server";

import { proxyToBackend } from "@/lib/backend";

// With no session cookie, proxyToBackend sends no Authorization header and
// the backend answers 401, so there is no separate "am I logged in" check to
// keep in sync with the backend's own verification.
export async function GET(request: NextRequest) {
  return proxyToBackend(request, "/api/v1/auth/me", { method: "GET" });
}
