import type { ReactNode } from "react";
import { X } from "lucide-react";

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

const Dialog = ({ isOpen, onClose, title, children }: DialogProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="
        relative w-full max-w-md
        bg-auth-card-bg dark:bg-dark-surface
        border border-auth-card-border dark:border-dark-border
        rounded-2xl shadow-xl p-6 z-10
      ">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          {title && (
            <h3 className="font-semibold text-secondary-800 dark:text-dark-text">
              {title}
            </h3>
          )}
          <button
            onClick={onClose}
            className="ml-auto text-secondary-400 hover:text-secondary-700 dark:text-dark-text-muted dark:hover:text-dark-text"
          >
            <X size={18} />
          </button>
        </div>

        {/* Contenu */}
        {children}
      </div>
    </div>
  );
};

export default Dialog;