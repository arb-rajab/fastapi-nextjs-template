import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Modal } from "@/components/ui/Modal";

describe("Modal", () => {
  it("renders nothing while closed", () => {
    render(
      <Modal open={false} title="Confirm" onClose={vi.fn()}>
        x
      </Modal>,
    );

    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("renders an accessible dialog and focuses it when open", () => {
    render(
      <Modal open title="Confirm" onClose={vi.fn()}>
        Are you sure?
      </Modal>,
    );

    const dialog = screen.getByRole("dialog", { name: "Confirm" });
    expect(dialog).toHaveAttribute("aria-modal", "true");
    expect(screen.getByText("Are you sure?")).toBeInTheDocument();
    expect(dialog).toHaveFocus();
  });

  it("closes on Escape", async () => {
    const onClose = vi.fn();
    render(
      <Modal open title="Confirm" onClose={onClose}>
        x
      </Modal>,
    );

    await userEvent.keyboard("{Escape}");

    expect(onClose).toHaveBeenCalledOnce();
  });

  it("closes on a backdrop click but not on a click inside the dialog", async () => {
    const onClose = vi.fn();
    render(
      <Modal open title="Confirm" onClose={onClose}>
        x
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");

    await userEvent.click(dialog);
    expect(onClose).not.toHaveBeenCalled();

    await userEvent.click(dialog.parentElement!);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("renders a footer", () => {
    render(
      <Modal open title="Confirm" onClose={vi.fn()} footer={<button type="button">OK</button>}>
        x
      </Modal>,
    );

    expect(screen.getByRole("button", { name: "OK" })).toBeInTheDocument();
  });

  it("gives focus back to the opener when it closes", () => {
    function Harness({ open }: { open: boolean }) {
      return (
        <>
          <button type="button">Open</button>
          <Modal open={open} title="Confirm" onClose={vi.fn()}>
            x
          </Modal>
        </>
      );
    }
    const { rerender } = render(<Harness open={false} />);
    screen.getByRole("button", { name: "Open" }).focus();

    rerender(<Harness open />);
    expect(screen.getByRole("dialog")).toHaveFocus();

    rerender(<Harness open={false} />);
    expect(screen.getByRole("button", { name: "Open" })).toHaveFocus();
  });
});
