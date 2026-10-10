import Link from "next/link";

import { EmptyState } from "@/components/ui/EmptyState";

export default function NotFound() {
  return (
    <main>
      <EmptyState
        title="Page not found"
        description="That page doesn't exist or has moved."
        action={<Link href="/">Back to the start</Link>}
      />
    </main>
  );
}
