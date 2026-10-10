import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Pagination } from "@/components/ui/Pagination";
import { pageQuery, pageWindow } from "@/lib/pagination";

describe("pageWindow", () => {
  it("shows every page when there are few", () => {
    expect(pageWindow(2, 3)).toEqual([1, 2, 3]);
  });

  it("collapses the gaps on both sides of the current page", () => {
    expect(pageWindow(5, 10)).toEqual([1, "…", 4, 5, 6, "…", 10]);
  });

  it("collapses only the far side near an edge", () => {
    expect(pageWindow(1, 10)).toEqual([1, 2, "…", 10]);
    expect(pageWindow(10, 10)).toEqual([1, "…", 9, 10]);
  });

  it("does not insert a gap for a single hidden page", () => {
    expect(pageWindow(3, 5)).toEqual([1, 2, 3, 4, 5]);
  });

  it("clamps an out-of-range page and handles no pages", () => {
    expect(pageWindow(99, 3)).toEqual([1, 2, 3]);
    expect(pageWindow(1, 0)).toEqual([]);
  });
});

describe("pageQuery", () => {
  it("builds the query string the backend expects", () => {
    expect(pageQuery(2)).toBe("?page=2");
    expect(pageQuery(2, 50)).toBe("?page=2&per_page=50");
  });
});

describe("Pagination", () => {
  it("renders nothing for a single page", () => {
    render(<Pagination page={1} totalPages={1} onPageChange={vi.fn()} />);

    expect(screen.queryByRole("navigation")).toBeNull();
  });

  it("marks the current page", () => {
    render(<Pagination page={2} totalPages={3} onPageChange={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Page 2" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("button", { name: "Page 3" })).not.toHaveAttribute("aria-current");
  });

  it("reports the chosen page", async () => {
    const onPageChange = vi.fn();
    render(<Pagination page={2} totalPages={5} onPageChange={onPageChange} />);

    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    await userEvent.click(screen.getByRole("button", { name: "Previous" }));
    await userEvent.click(screen.getByRole("button", { name: "Page 5" }));

    expect(onPageChange.mock.calls).toEqual([[3], [1], [5]]);
  });

  it("disables Previous on the first page and Next on the last", () => {
    const { unmount } = render(<Pagination page={1} totalPages={3} onPageChange={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
    unmount();

    render(<Pagination page={3} totalPages={3} onPageChange={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });
});
