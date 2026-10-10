import { useId } from "react";
import type { InputHTMLAttributes } from "react";

export interface FormFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "id"> {
  label: string;
  /** Field-level error(s), for example `ApiError.fields[name]`. */
  error?: string | string[] | null;
  hint?: string;
  id?: string;
}

export function FormField({ label, error, hint, id, ...inputProps }: FormFieldProps) {
  const generatedId = useId();
  const fieldId = id ?? generatedId;
  const messages = error ? (Array.isArray(error) ? error : [error]) : [];
  const hasError = messages.length > 0;
  const errorId = `${fieldId}-error`;
  const hintId = `${fieldId}-hint`;
  const describedBy = [hasError ? errorId : null, hint ? hintId : null].filter(Boolean).join(" ");

  return (
    <div className="field">
      <label htmlFor={fieldId}>{label}</label>
      <input
        {...inputProps}
        id={fieldId}
        aria-invalid={hasError}
        aria-describedby={describedBy || undefined}
      />
      {hint ? (
        <small id={hintId} className="field__hint">
          {hint}
        </small>
      ) : null}
      {hasError ? (
        <small id={errorId} className="field__error">
          {messages.map((message) => (
            <span key={message}>{message}</span>
          ))}
        </small>
      ) : null}
    </div>
  );
}
