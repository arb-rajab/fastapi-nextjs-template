export interface AlertProps {
  variant?: "error" | "success" | "info";
  children: React.ReactNode;
}

/** Errors interrupt screen readers (role=alert); success and info do not. */
export function Alert({ variant = "error", children }: AlertProps) {
  return (
    <div className={`alert alert--${variant}`} role={variant === "error" ? "alert" : "status"}>
      {children}
    </div>
  );
}
