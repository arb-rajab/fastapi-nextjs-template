import type { Metadata, Viewport } from "next";

import { AuthGate } from "@/components/AuthGate";
import { AuthProvider } from "@/lib/auth";

import "./globals.css";

export const metadata: Metadata = {
  title: "starterapp",
  description: "starterapp web frontend",
};

// Lets the browser pick light/dark form controls and scrollbars to match.
export const viewport: Viewport = {
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <AuthGate>{children}</AuthGate>
        </AuthProvider>
      </body>
    </html>
  );
}
