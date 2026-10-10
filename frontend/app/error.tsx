"use client";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";

// Error boundary for every route below the root layout. `reset` re-renders
// the failed segment. The error message is not shown: in production Next
// replaces server errors with a generic message and a digest, and a client
// error's text may not be fit for users.
export default function RouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main>
      <h1>Something went wrong</h1>
      <Alert>An unexpected error occurred. You can try again.</Alert>
      {error.digest ? <p className="muted">Reference: {error.digest}</p> : null}
      <Button onClick={reset}>Try again</Button>
    </main>
  );
}
