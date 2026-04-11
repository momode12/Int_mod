import { useToastContext } from "../../providers/toastContext";
import { X, CheckCircle, XCircle, AlertTriangle, Info } from "lucide-react";

const icons = {
  success: <CheckCircle size={16} className="text-success" />,
  error:   <XCircle size={16} className="text-error" />,
  warning: <AlertTriangle size={16} className="text-warning" />,
  info:    <Info size={16} className="text-info" />,
};

const Toast = () => {
  const { toasts, removeToast } = useToastContext();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="
            flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg
            bg-auth-card-bg dark:bg-dark-surface
            border border-auth-card-border dark:border-dark-border
            min-w-64 max-w-sm
            animate-in slide-in-from-right
          "
        >
          {icons[toast.type]}
          <span className="text-sm text-secondary-800 dark:text-dark-text flex-1">
            {toast.message}
          </span>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-secondary-400 hover:text-secondary-700 dark:text-dark-text-muted dark:hover:text-dark-text"
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
};

export default Toast;