import { create } from "zustand";

type Theme = "light" | "dark";

interface UIStore {
  theme: Theme;
  isSidebarOpen: boolean;
  isSidebarCollapsed: boolean;
  isLoading: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  toggleSidebarCollapsed: () => void;
  setSidebarOpen: (value: boolean) => void;
  setSidebarCollapsed: (value: boolean) => void;
  setLoading: (value: boolean) => void;
}

const getInitialTheme = (): Theme => {
  if (typeof window === "undefined") return "light";
  return (localStorage.getItem("theme") as Theme) || "light";
};

const getInitialSidebarCollapsed = (): boolean => {
  if (typeof window === "undefined") return false;
  return localStorage.getItem("sidebarCollapsed") === "1";
};

export const useUIStore = create<UIStore>((set) => ({
  theme: getInitialTheme(),
  isSidebarOpen: false, // mobile-first
  isSidebarCollapsed: getInitialSidebarCollapsed(),
  isLoading: false,

  toggleTheme: () =>
    set((state) => {
      const next = state.theme === "light" ? "dark" : "light";
      localStorage.setItem("theme", next);
      return { theme: next };
    }),

  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  toggleSidebarCollapsed: () =>
    set((state) => {
      const next = !state.isSidebarCollapsed;
      localStorage.setItem("sidebarCollapsed", next ? "1" : "0");
      return { isSidebarCollapsed: next };
    }),

  setSidebarOpen: (value) =>
    set({ isSidebarOpen: value }),

  setSidebarCollapsed: (value) =>
    set(() => {
      localStorage.setItem("sidebarCollapsed", value ? "1" : "0");
      return { isSidebarCollapsed: value };
    }),

  setLoading: (value) =>
    set({ isLoading: value }),
}));
