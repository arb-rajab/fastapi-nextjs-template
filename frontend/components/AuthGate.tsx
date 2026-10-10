"use client";

import { AuthBar } from "@/components/AuthBar";
import { AuthForm } from "@/components/AuthForm";
import { Spinner } from "@/components/ui/Spinner";
import { useAuth } from "@/lib/auth";

/** Shows the sign-in/register form until a session exists, then the app
 * with a header carrying the signed-in username. */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <main>
        <Spinner label="Checking your session" />
      </main>
    );
  }
  if (!user) return <AuthForm />;

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <span className="site-header__brand">starterapp</span>
        <AuthBar />
      </header>
      <div id="main">{children}</div>
    </>
  );
}
