import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Alert } from "@/components/ui/Alert";
import { Spinner } from "@/components/ui/Spinner";

describe("Alert", () => {
  it("announces errors with role=alert", () => {
    render(<Alert>Bad things</Alert>);

    expect(screen.getByRole("alert")).toHaveTextContent("Bad things");
  });

  it("uses role=status for non-error variants", () => {
    render(<Alert variant="success">Saved</Alert>);

    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.getByRole("status")).toHaveTextContent("Saved");
  });
});

describe("Spinner", () => {
  it("exposes an accessible label", () => {
    render(<Spinner label="Loading users" />);

    expect(screen.getByRole("status", { name: "Loading users" })).toBeInTheDocument();
  });
});
