import type { ButtonHTMLAttributes } from "react";

import { Spinner } from "@/components/ui/Spinner";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  /** Shows a spinner and disables the button while an action is in flight. */
  loading?: boolean;
}

export function Button({
  variant = "primary",
  loading = false,
  type = "button",
  disabled,
  className,
  children,
  ...rest
}: ButtonProps) {
  const classes = ["btn", `btn--${variant}`, className].filter(Boolean).join(" ");
  return (
    <button {...rest} type={type} className={classes} disabled={disabled || loading} aria-busy={loading}>
      {loading ? <Spinner label="Working" /> : null}
      {children}
    </button>
  );
}
