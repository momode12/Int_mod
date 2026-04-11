import { useToastContext } from "../providers/ToastProvider";

export const useToast = () => {
  return useToastContext();
};