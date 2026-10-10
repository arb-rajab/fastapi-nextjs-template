import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DataTable, type Column } from "@/components/ui/DataTable";

interface Row {
  id: number;
  name: string;
  role: string;
}

const columns: Column<Row>[] = [
  { header: "Name", cell: (row) => row.name },
  { header: "Role", cell: (row) => <em>{row.role}</em> },
];

describe("DataTable", () => {
  it("renders headers and rows", () => {
    render(
      <DataTable
        columns={columns}
        rows={[
          { id: 1, name: "Ada", role: "admin" },
          { id: 2, name: "Grace", role: "user" },
        ]}
        caption="Users"
        rowKey={(row) => row.id}
      />,
    );

    expect(screen.getByRole("table", { name: "Users" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Name" })).toBeInTheDocument();
    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(3); // header + 2 data rows
    expect(within(rows[1]).getByText("Ada")).toBeInTheDocument();
    expect(within(rows[2]).getByText("user")).toBeInTheDocument();
  });

  it("shows the empty state when there are no rows", () => {
    render(
      <DataTable
        columns={columns}
        rows={[]}
        caption="Users"
        rowKey={(row) => row.id}
        emptyTitle="No users"
      />,
    );

    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.getByRole("heading", { name: "No users" })).toBeInTheDocument();
  });

  it("shows a spinner while loading, even if rows exist", () => {
    render(
      <DataTable
        columns={columns}
        rows={[{ id: 1, name: "Ada", role: "admin" }]}
        caption="Users"
        rowKey={(row) => row.id}
        loading
      />,
    );

    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.getByRole("status", { name: "Loading Users" })).toBeInTheDocument();
  });
});
