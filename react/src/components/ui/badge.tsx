import type { ReactNode } from "react";

type BadgeVariant = "success" | "error" | "warning" | "info" | "default";

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
}

const Badge = ({ children, variant = "default" }: BadgeProps) => {
  const variants = {
    success: "bg-success-light text-success-dark",
    error:   "bg-error-light text-error-dark",
    warning: "bg-warning-light text-warning-dark",
    info:    "bg-info-light text-info-dark",
    default: "bg-secondary-200 dark:bg-dark-surface text-secondary-700 dark:text-dark-text",
  };

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5
        rounded-full text-xs font-medium
        ${variants[variant]}
      `}
    >
      {children}
    </span>
  );
};

export default Badge;