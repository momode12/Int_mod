import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  fullWidth?: boolean;
}

const Button = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  fullWidth = false,
  disabled,
  className = "",
  ...props
}: ButtonProps) => {
  const variants = {
    primary:  "bg-primary-500 hover:bg-primary-600 text-white",
    secondary:"bg-secondary-200 hover:bg-secondary-300 text-secondary-800 dark:bg-dark-surface dark:hover:bg-dark-border dark:text-dark-text",
    danger:   "bg-error hover:bg-error-dark text-white",
    ghost:    "hover:bg-secondary-100 dark:hover:bg-dark-surface text-secondary-700 dark:text-dark-text",
    outline:  "border border-secondary-300 dark:border-dark-border hover:bg-secondary-100 dark:hover:bg-dark-surface text-secondary-700 dark:text-dark-text",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs rounded-lg",
    md: "px-4 py-2 text-sm rounded-xl",
    lg: "px-6 py-3 text-base rounded-xl",
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`
        inline-flex items-center justify-center gap-2 font-medium
        transition-colors disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? "w-full" : ""}
        ${className}
      `}
      {...props}
    >
      {isLoading && (
        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
};

export default Button;