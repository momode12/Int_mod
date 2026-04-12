import { useAuthContext } from "../providers/authContext";

export const useAuth = () => {
  return useAuthContext();
};