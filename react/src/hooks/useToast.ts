import { useToastContext } from "../providers/toastContext";

export const useToast = () => {
  return useToastContext();
};