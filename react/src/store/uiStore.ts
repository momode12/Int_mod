import { create } from "zustand";

type Theme = "light" | "dark";

interface UIStore {
  theme: Theme;
  isSidebarOpen: boolean;
  isLoading: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (value: boolean) => void;
  setLoading: (value: boolean) => void;
}

const getInitialTheme = (): Theme => {
  if (typeof window === "undefined") return "light";
  return (localStorage.getItem("theme") as Theme) || "light";
};

export const useUIStore = create<UIStore>((set) => ({
  theme: getInitialTheme(),
  isSidebarOpen: false, // mobile-first
  isLoading: false,

  toggleTheme: () =>
    set((state) => {
      const next = state.theme === "light" ? "dark" : "light";
      localStorage.setItem("theme", next);
      return { theme: next };
    }),

  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  setSidebarOpen: (value) =>
    set({ isSidebarOpen: value }),

  setLoading: (value) =>
    set({ isLoading: value }),
}));