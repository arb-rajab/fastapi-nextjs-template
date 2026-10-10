import { NextResponse } from "next/server";

import { SESSION_COOKIE } from "@/lib/session-cookie";

// Session tokens are not revocable server-side: "logout" means this browser
// stops sending the token, not that the token is invalidated early.
export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete(SESSION_COOKIE);
  return response;
}
