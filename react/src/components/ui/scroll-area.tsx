import type { ReactNode } from "react";

interface ScrollAreaProps {
  children: ReactNode;
  className?: string;
  maxHeight?: string;
}

const ScrollArea = ({ children, className = "", maxHeight = "100%" }: ScrollAreaProps) => {
  return (
    <div
      className={`overflow-y-auto scrollbar-thin
        scrollbar-thumb-secondary-300 dark:scrollbar-thumb-dark-border
        scrollbar-track-transparent
        ${className}
      `}
      style={{ maxHeight }}
    >
      {children}
    </div>
  );
};

export default ScrollArea;