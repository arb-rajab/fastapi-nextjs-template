import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";

export interface Column<Row> {
  header: string;
  /** Renders the cell. Return plain values or elements. */
  cell: (row: Row) => React.ReactNode;
  align?: "left" | "right";
}

export interface DataTableProps<Row> {
  columns: Column<Row>[];
  rows: Row[];
  /** Accessible table name. */
  caption: string;
  /** Unique, stable value per row (React key). */
  rowKey: (row: Row) => string | number;
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function DataTable<Row>({
  columns,
  rows,
  caption,
  rowKey,
  loading = false,
  emptyTitle = "Nothing here yet",
  emptyDescription,
}: DataTableProps<Row>) {
  if (loading) {
    return (
      <p className="data-table__loading">
        <Spinner label={`Loading ${caption}`} />
      </p>
    );
  }
  if (rows.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <table className="data-table">
      <caption className="visually-hidden">{caption}</caption>
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column.header} scope="col" className={column.align}>
              {column.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={rowKey(row)}>
            {columns.map((column) => (
              <td key={column.header} className={column.align}>
                {column.cell(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
