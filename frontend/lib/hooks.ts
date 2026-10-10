"use client";

import { useCallback, useEffect, useState } from "react";

import type { ApiError } from "@/lib/api-client";

export interface AsyncState<T> {
  data: T | null;
  error: ApiError | Error | null;
  loading: boolean;
}

/**
 * Runs `load` on mount and whenever it changes; `refetch` runs it again.
 * Pass a stable `load` (module-level function or `useCallback`), otherwise it
 * re-runs on every render.
 */
export function useAsync<T>(load: () => Promise<T>) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    loading: true,
  });
  const [reloads, setReloads] = useState(0);

  useEffect(() => {
    let cancelled = false;
    load()
      .then((data) => {
        if (!cancelled) setState({ data, error: null, loading: false });
      })
      .catch((error) => {
        if (!cancelled) setState({ data: null, error, loading: false });
      });
    return () => {
      cancelled = true;
    };
  }, [load, reloads]);

  const refetch = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: null }));
    setReloads((n) => n + 1);
  }, []);

  return { ...state, refetch };
}
