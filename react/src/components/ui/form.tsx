import type { FormHTMLAttributes, ReactNode } from "react";

interface FormProps extends FormHTMLAttributes<HTMLFormElement> {
  children: ReactNode;
  title?: string;
  subtitle?: string;
}

const Form = ({ children, title, subtitle, className = "", ...props }: FormProps) => {
  return (
    <div className="flex flex-col gap-4">
      {title && (
        <div className="text-center mb-2">
          <h2 className="text-xl font-bold text-secondary-800 dark:text-dark-text">
            {title}
          </h2>
          {subtitle && (
            <p className="text-sm text-secondary-500 dark:text-dark-text-muted mt-1">
              {subtitle}
            </p>
          )}
        </div>
      )}
      <form className={`flex flex-col gap-4 ${className}`} {...props}>
        {children}
      </form>
    </div>
  );
};

export default Form;