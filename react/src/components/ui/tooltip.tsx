import { useState } from "react";
import type {  ReactNode } from 'react';

interface TooltipProps {
  children: ReactNode;
  content: string;
  position?: "top" | "bottom" | "left" | "right";
}

const Tooltip = ({ children, content, position = "top" }: TooltipProps) => {
  const [isVisible, setIsVisible] = useState(false);

  const positions = {
    top:    "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left:   "right-full top-1/2 -translate-y-1/2 mr-2",
    right:  "left-full top-1/2 -translate-y-1/2 ml-2",
  };

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          className={`
            absolute z-50 px-2 py-1 text-xs rounded-lg whitespace-nowrap
            bg-secondary-800 dark:bg-dark-surface text-white dark:text-dark-text
            shadow-lg pointer-events-none
            ${positions[position]}
          `}
        >
          {content}
        </div>
      )}
    </div>
  );
};

export default Tooltip;