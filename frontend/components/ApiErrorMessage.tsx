import { Alert } from "@/components/ui/Alert";
import { ApiError } from "@/lib/api-client";

// Friendly text per backend error code; unknown codes fall back to the
// backend's own message. Add codes your endpoints return.
const FRIENDLY_MESSAGE: Record<string, string> = {
  unauthenticated: "You need to sign in before doing that.",
  forbidden: "You don't have access to that.",
  not_found: "That resource doesn't exist.",
  rate_limited: "Too many requests too fast. Slow down and try again.",
  validation_error: "That request wasn't valid.",
  backend_unreachable: "Could not reach the server. Try again shortly.",
};

export function describeApiError(error: unknown): string {
  if (error instanceof ApiError) {
    const friendly = FRIENDLY_MESSAGE[error.code];
    const suffix = error.retryAfter != null ? ` (retry in ${error.retryAfter}s)` : "";
    return `${friendly ?? error.message}${suffix}`;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

export function ApiErrorMessage({ error }: { error: unknown }) {
  return <Alert>{describeApiError(error)}</Alert>;
}
