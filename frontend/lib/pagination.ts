// Mirrors backend/src/starterapp/api/pagination.py (the `Page` envelope).

export interface Page<T> {
  items: T[];
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

/**
 * The page numbers a pagination control should show: always the first and last
 * page, plus `radius` pages either side of the current one. A gap between two
 * shown numbers is the string "…".
 *
 *   pageWindow(5, 10) -> [1, "…", 4, 5, 6, "…", 10]
 */
export function pageWindow(page: number, totalPages: number, radius = 1): (number | "…")[] {
  if (totalPages < 1) return [];
  const current = Math.min(Math.max(page, 1), totalPages);
  const wanted = new Set<number>([1, totalPages]);
  for (let p = current - radius; p <= current + radius; p++) {
    if (p >= 1 && p <= totalPages) wanted.add(p);
  }
  const sorted = [...wanted].sort((a, b) => a - b);
  const out: (number | "…")[] = [];
  sorted.forEach((p, i) => {
    if (i > 0 && p - sorted[i - 1] > 1) out.push("…");
    out.push(p);
  });
  return out;
}

/** Query string for a list request, e.g. `?page=2&per_page=20`. */
export function pageQuery(page: number, perPage?: number): string {
  const params = new URLSearchParams({ page: String(page) });
  if (perPage !== undefined) params.set("per_page", String(perPage));
  return `?${params.toString()}`;
}
