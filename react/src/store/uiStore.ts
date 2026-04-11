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

const applyTheme = (theme: Theme) => {
  document.documentElement.classList.remove("light", "dark");
  document.documentElement.classList.add(theme);
  localStorage.setItem("theme", theme);
};

const getInitialTheme = (): Theme => {
  return (localStorage.getItem("theme") as Theme) || "light";
};

export const useUIStore = create<UIStore>((set) => ({
  theme: (() => {
    const initial = getInitialTheme();
    applyTheme(initial);
    return initial;
  })(),
  isSidebarOpen: true,
  isLoading: false,

  toggleTheme: () =>
    set((state) => {
      const next = state.theme === "light" ? "dark" : "light";
      applyTheme(next);
      return { theme: next };
    }),

  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  setSidebarOpen: (value) =>
    set({ isSidebarOpen: value }),

  setLoading: (value) =>
    set({ isLoading: value }),
}));