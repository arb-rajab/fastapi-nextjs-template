import { describe, expect, it } from "vitest";

import { ApiError, unwrap } from "@/lib/api-client";

function jsonResponse(body: unknown, init?: ResponseInit) {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    ...init,
  });
}

describe("unwrap", () => {
  it("returns the parsed body for a successful response", async () => {
    await expect(unwrap(jsonResponse({ ok: true }))).resolves.toEqual({ ok: true });
  });

  it("returns undefined for 204", async () => {
    await expect(unwrap(new Response(null, { status: 204 }))).resolves.toBeUndefined();
  });

  it("throws an ApiError carrying the error envelope and Retry-After", async () => {
    const response = jsonResponse(
      { error: { code: "rate_limited", message: "slow down", field: null } },
      { status: 429, headers: { "content-type": "application/json", "retry-after": "12" } },
    );
    const error = await unwrap(response).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 429, code: "rate_limited", retryAfter: 12 });
  });

  it("falls back to unknown_error when the body is not JSON", async () => {
    const error = await unwrap(new Response("boom", { status: 500, statusText: "Oops" })).catch(
      (e: unknown) => e,
    );
    expect(error).toMatchObject({ status: 500, code: "unknown_error" });
  });
});
