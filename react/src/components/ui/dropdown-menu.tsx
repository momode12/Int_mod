import { useState, useRef, useEffect } from "react";
import type { ReactNode } from "react";

interface DropdownItem {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  danger?: boolean;
}

interface DropdownMenuProps {
  trigger: ReactNode;
  items: DropdownItem[];
}

const DropdownMenu = ({ trigger, items }: DropdownMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <div onClick={() => setIsOpen((prev) => !prev)}>
        {trigger}
      </div>

      {isOpen && (
        <div className="
          absolute right-0 mt-2 w-48 z-50
          bg-auth-card-bg dark:bg-dark-surface
          border border-auth-card-border dark:border-dark-border
          rounded-xl shadow-lg overflow-hidden
        ">
          {items.map((item, index) => (
            <button
              key={index}
              onClick={() => {
                item.onClick();
                setIsOpen(false);
              }}
              className={`
                w-full flex items-center gap-2 px-4 py-2 text-sm text-left
                transition-colors
                ${item.danger
                  ? "text-error hover:bg-error-light"
                  : "text-secondary-700 dark:text-dark-text hover:bg-secondary-100 dark:hover:bg-dark-border"}
              `}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default DropdownMenu;