import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { FormField } from "@/components/ui/FormField";

describe("FormField", () => {
  it("links the label to the input", () => {
    render(<FormField label="Email" name="email" />);

    expect(screen.getByLabelText("Email")).toHaveAttribute("name", "email");
  });

  it("is valid when there is no error", () => {
    render(<FormField label="Email" name="email" />);

    expect(screen.getByLabelText("Email")).toHaveAttribute("aria-invalid", "false");
  });

  it("shows a field error and ties it to the input", () => {
    render(<FormField label="Email" name="email" error="Enter a valid email." />);

    const input = screen.getByLabelText("Email");
    const message = screen.getByText("Enter a valid email.");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input.getAttribute("aria-describedby")).toContain(message.parentElement!.id);
  });

  it("shows every message when given several", () => {
    render(<FormField label="Password" name="password" error={["Too short", "Too common"]} />);

    expect(screen.getByText("Too short")).toBeInTheDocument();
    expect(screen.getByText("Too common")).toBeInTheDocument();
  });

  it("shows a hint", () => {
    render(<FormField label="Name" name="name" hint="As on your ID" />);

    expect(screen.getByText("As on your ID").id).toBe(
      screen.getByLabelText("Name").getAttribute("aria-describedby"),
    );
  });

  it("passes input props through", async () => {
    render(<FormField label="Name" name="name" defaultValue="" />);
    const input = screen.getByLabelText<HTMLInputElement>("Name");

    await userEvent.type(input, "Ada");

    expect(input.value).toBe("Ada");
  });
});
