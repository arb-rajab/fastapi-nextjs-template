// Mirrors backend/src/starterapp/api/schemas.py; keep the two in sync.

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    field: string | null;
    /** Only on `validation_error`: every problem, keyed by field name. */
    fields?: Record<string, string[]>;
  };
}
