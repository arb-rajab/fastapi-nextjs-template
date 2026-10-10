"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

// Talks to the same-origin auth routes (app/api/auth/*). The session token is
// never held here or anywhere in page JavaScript: it lives only in an httpOnly
// cookie those route handlers set and read server-side.

export class AuthError extends Error {
  readonly status: number;
  readonly code: string;
  /** Per-field messages from a `validation_error`; empty otherwise. */
  readonly fields: Record<string, string[]>;

  constructor(status: number, code: string, message: string, fields: Record<string, string[]> = {}) {
    super(message);
    this.name = "AuthError";
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

interface AuthUser {
  username: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

async function parseErrorBody(response: Response): Promise<AuthError> {
  try {
    const body = await response.json();
    return new AuthError(
      response.status,
      body?.error?.code ?? "unknown_error",
      body?.error?.message ?? response.statusText,
      body?.error?.fields ?? {},
    );
  } catch {
    return new AuthError(response.status, "unknown_error", response.statusText);
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      let next: AuthUser | null = null;
      try {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
          const body = await res.json();
          next = { username: body.username };
        }
      } catch {
        next = null;
      }
      if (!cancelled) {
        setUser(next);
        setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const submitCredentials = useCallback(
    async (path: "login" | "register", username: string, password: string) => {
      const res = await fetch(`/api/auth/${path}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw await parseErrorBody(res);
      const body = await res.json();
      setUser({ username: body.username });
    },
    [],
  );

  const login = useCallback(
    (username: string, password: string) => submitCredentials("login", username, password),
    [submitCredentials],
  );
  const register = useCallback(
    (username: string, password: string) => submitCredentials("register", username, password),
    [submitCredentials],
  );

  const logout = useCallback(async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
