import { useState, useCallback } from "react";
import type { ReactNode } from "react";
import { ToastContext } from "./toastContext";
import type { ToastContextType, Toast, ToastType } from "./toastContext";
const generateId = () => Math.random().toString(36).substring(2, 9);

const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = generateId();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => removeToast(id), 3000);
  }, [removeToast]);

  const value: ToastContextType = { toasts, showToast, removeToast };

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
};

export default ToastProvider;