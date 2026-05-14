import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padding?: "sm" | "md" | "lg";
}

const Card = ({ children, padding = "md", className = "", ...props }: CardProps) => {
  const paddings = {
    sm: "p-3",
    md: "p-5",
    lg: "p-8",
  };

  return (
    <div
      className={`
        bg-auth-card-bg dark:bg-dark-surface
        border border-auth-card-border dark:border-dark-border
        rounded-2xl shadow-sm
        ${paddings[padding]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;