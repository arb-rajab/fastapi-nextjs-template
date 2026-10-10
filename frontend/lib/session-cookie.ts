// The session token (a backend-issued JWT) lives only in an httpOnly cookie
// that this server sets and reads; page JavaScript never has access to it
// (no localStorage, no readable cookie).
export const SESSION_COOKIE = "starterapp_session";

interface SessionCookieOptions {
  httpOnly: boolean;
  secure: boolean;
  sameSite: "lax";
  path: string;
  maxAge: number;
}

export function sessionCookieOptions(maxAgeSeconds: number): SessionCookieOptions {
  return {
    httpOnly: true,
    // Not tied to NODE_ENV: `next start` sets NODE_ENV=production even when
    // no TLS terminates in front of it, and a Secure cookie served over
    // plain HTTP is silently dropped by the browser. Set COOKIE_SECURE=true
    // once the app is actually served over HTTPS.
    secure: process.env.COOKIE_SECURE === "true",
    sameSite: "lax",
    path: "/",
    maxAge: maxAgeSeconds,
  };
}
