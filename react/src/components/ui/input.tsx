import type { InputHTMLAttributes } from "react";
import { forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, fullWidth = true, className = "", ...props }, ref) => {
    return (
      <div className={`flex flex-col gap-1 ${fullWidth ? "w-full" : ""}`}>
        {label && (
          <label className="text-sm font-medium text-secondary-700 dark:text-dark-text">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`
            px-4 py-2 rounded-xl text-sm outline-none
            bg-chat-input-bg dark:bg-dark-background
            border border-chat-input-border dark:border-dark-border
            text-secondary-800 dark:text-dark-text
            placeholder:text-secondary-400 dark:placeholder:text-dark-text-muted
            focus:ring-2 focus:ring-primary-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
            ${error ? "border-error focus:ring-error" : ""}
            ${fullWidth ? "w-full" : ""}
            ${className}
          `}
          {...props}
        />
        {error && (
          <span className="text-xs text-error">{error}</span>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;