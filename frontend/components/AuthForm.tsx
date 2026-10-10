"use client";

import { useState } from "react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { AuthError, useAuth } from "@/lib/auth";

const FRIENDLY_MESSAGE: Record<string, string> = {
  invalid_credentials: "Invalid username or password.",
  username_taken: "That username is already registered.",
  rate_limited: "Too many attempts — slow down and try again shortly.",
  validation_error: "Check your username and password and try again.",
};

export function AuthForm() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setFieldErrors({});
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, password);
      }
    } catch (err) {
      if (err instanceof AuthError) {
        setError(FRIENDLY_MESSAGE[err.code] ?? err.message);
        setFieldErrors(err.fields);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <h1>starterapp</h1>

      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        <h2>{mode === "login" ? "Sign in" : "Create an account"}</h2>

        <FormField
          label="Username"
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          disabled={submitting}
          error={fieldErrors.username}
        />

        <FormField
          label="Password"
          name="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          disabled={submitting}
          error={fieldErrors.password}
        />

        {error ? <Alert>{error}</Alert> : null}

        <Button type="submit" loading={submitting} disabled={!username.trim() || !password}>
          {mode === "login" ? "Sign in" : "Create account"}
        </Button>

        <Button
          variant="secondary"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
            setFieldErrors({});
          }}
          disabled={submitting}
        >
          {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
        </Button>
      </form>
    </main>
  );
}
