import type { ApiErrorBody } from "@/lib/types";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly field: string | null;
  /** Per-field messages from a `validation_error`; empty otherwise. */
  readonly fields: Record<string, string[]>;
  readonly retryAfter: number | null;

  constructor(status: number, body: ApiErrorBody, retryAfter: number | null) {
    super(body.error.message);
    this.name = "ApiError";
    this.status = status;
    this.code = body.error.code;
    this.field = body.error.field;
    this.fields = body.error.fields ?? {};
    this.retryAfter = retryAfter;
  }
}

export async function unwrap<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const retryAfterHeader = response.headers.get("retry-after");
    const retryAfter = retryAfterHeader ? Number.parseInt(retryAfterHeader, 10) : null;
    let body: ApiErrorBody;
    try {
      body = await response.json();
    } catch {
      body = { error: { code: "unknown_error", message: response.statusText, field: null } };
    }
    throw new ApiError(response.status, body, retryAfter);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

// The browser sends this app's httpOnly session cookie automatically on
// every same-origin request; app/api/** route handlers turn it into the
// `Authorization: Bearer <token>` header the backend verifies.

export async function apiGet<T>(path: string): Promise<T> {
  return unwrap<T>(await fetch(path));
}

export async function apiSend<T>(
  method: "POST" | "PUT" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(path, {
    method,
    headers: body === undefined ? undefined : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return unwrap<T>(res);
}
