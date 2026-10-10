import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ApiErrorMessage, describeApiError } from "@/components/ApiErrorMessage";
import { ApiError } from "@/lib/api-client";

describe("describeApiError", () => {
  it("uses friendly text for known codes and appends Retry-After", () => {
    const error = new ApiError(
      429,
      { error: { code: "rate_limited", message: "raw", field: null } },
      7,
    );
    expect(describeApiError(error)).toMatch(/Too many requests.*retry in 7s/);
  });

  it("falls back to the backend message for unknown codes", () => {
    const error = new ApiError(
      400,
      { error: { code: "something_new", message: "raw message", field: null } },
      null,
    );
    expect(describeApiError(error)).toBe("raw message");
  });
});

describe("ApiErrorMessage", () => {
  it("renders an alert", () => {
    render(<ApiErrorMessage error={new Error("nope")} />);
    expect(screen.getByRole("alert")).toHaveTextContent("nope");
  });
});
