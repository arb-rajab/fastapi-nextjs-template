import { afterEach, describe, expect, it, vi } from "vitest";

import { sessionCookieOptions } from "@/lib/session-cookie";

describe("sessionCookieOptions", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("is httpOnly and not Secure by default", () => {
    expect(sessionCookieOptions(60)).toMatchObject({ httpOnly: true, secure: false, maxAge: 60 });
  });

  it("is Secure only when COOKIE_SECURE=true", () => {
    vi.stubEnv("COOKIE_SECURE", "true");
    expect(sessionCookieOptions(60).secure).toBe(true);
  });
});
