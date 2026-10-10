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

describe("AuthForm field errors", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the backend's per-field validation messages next to the inputs", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({}, 401)) // AuthProvider's /me check
      .mockResolvedValueOnce(
        jsonResponse(
          {
            error: {
              code: "validation_error",
              message: "String should have at least 8 characters",
              field: "password",
              fields: { password: ["String should have at least 8 characters"] },
            },
          },
          422,
        ),
      );

    render(
      <AuthProvider>
        <AuthForm />
      </AuthProvider>,
    );
    await user.click(screen.getByRole("button", { name: /need an account/i }));
    await user.type(screen.getByLabelText("Username"), "alice");
    await user.type(screen.getByLabelText("Password"), "short");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    const message = await screen.findByText("String should have at least 8 characters");
    expect(screen.getByLabelText("Password")).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByLabelText("Password").getAttribute("aria-describedby")).toContain(
      message.parentElement!.id,
    );
    expect(screen.getByLabelText("Username")).toHaveAttribute("aria-invalid", "false");
  });
});
