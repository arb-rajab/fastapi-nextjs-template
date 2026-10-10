import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EmptyState } from "@/components/ui/EmptyState";

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(<EmptyState title="No items" description="Create one to get started." />);

    expect(screen.getByRole("heading", { name: "No items" })).toBeInTheDocument();
    expect(screen.getByText("Create one to get started.")).toBeInTheDocument();
  });

  it("renders an action when given one", () => {
    render(<EmptyState title="No items" action={<button type="button">Add item</button>} />);

    expect(screen.getByRole("button", { name: "Add item" })).toBeInTheDocument();
  });
});
