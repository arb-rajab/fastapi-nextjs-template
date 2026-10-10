import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AuthForm } from "@/components/AuthForm";
import { AuthProvider } from "@/lib/auth";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("AuthForm", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows a friendly message for invalid credentials", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch)
      // AuthProvider's initial /api/auth/me check: signed out.
      .mockResolvedValueOnce(
        jsonResponse({ error: { code: "unauthenticated", message: "x", field: null } }, 401),
      )
      .mockResolvedValueOnce(
        jsonResponse({ error: { code: "invalid_credentials", message: "x", field: null } }, 401),
      );

    render(
      <AuthProvider>
        <AuthForm />
      </AuthProvider>,
    );

    await user.type(screen.getByLabelText("Username"), "alice");
    await user.type(screen.getByLabelText("Password"), "wrong-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid username or password.");
  });

  it("switches to register mode", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValue(jsonResponse({}, 401));

    render(
      <AuthProvider>
        <AuthForm />
      </AuthProvider>,
    );

    await user.click(screen.getByRole("button", { name: /need an account/i }));
    expect(screen.getByRole("heading", { name: "Create an account" })).toBeInTheDocument();
  });
});
