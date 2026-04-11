import type { LabelHTMLAttributes, ReactNode } from "react";

interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  children: ReactNode;
  required?: boolean;
}

const Label = ({ children, required, className = "", ...props }: LabelProps) => {
  return (
    <label
      className={`
        text-sm font-medium
        text-secondary-700 dark:text-dark-text
        ${className}
      `}
      {...props}
    >
      {children}
      {required && (
        <span className="text-error ml-1">*</span>
      )}
    </label>
  );
};

export default Label;