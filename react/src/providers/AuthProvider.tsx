import { useState } from "react";
import { AuthContext } from "./authContext";
import type { ReactNode } from "react";
import type { AuthContextType } from "./authContext";
import { api } from "../utils/api";

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

const getInitialUser = (): User | null => {
  try {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  } catch {
    return null;
  }
};

const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(getInitialUser);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // ✅ Utilise api.ts — URL centralisée
      const data = await api.post<{ token: string; user: User }>(
        "/auth/login",
        { email, password }
      );

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);

    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      // ✅ Utilise api.ts — URL centralisée
      const data = await api.post<{ token: string; user: User }>(
        "/auth/register",
        { name, email, password }
      );

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);

    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;