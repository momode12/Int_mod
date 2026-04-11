import { useAuth } from "../../hooks/useAuth";
import { useUIStore } from "../../store/uiStore";
import { Menu, Moon, Sun, LogOut } from "lucide-react";

const ChatHeader = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme, toggleSidebar } = useUIStore();

  return (
    <header className="
      h-14 border-b border-header-border bg-header-bg dark:bg-dark-surface
      dark:border-dark-border flex items-center justify-between px-4 shrink-0
    ">
      {/* Gauche */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="text-secondary-500 hover:text-secondary-800 dark:text-dark-text-muted dark:hover:text-dark-text"
        >
          <Menu size={20} />
        </button>
        <span className="font-semibold text-header-text dark:text-dark-text text-sm">
          ChatBot IA
        </span>
      </div>

      {/* Droite */}
      <div className="flex items-center gap-3">
        {/* Toggle theme */}
        <button
          onClick={toggleTheme}
          className="text-secondary-500 hover:text-secondary-800 dark:text-dark-text-muted dark:hover:text-dark-text"
        >
          {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        {/* User info */}
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-primary-500 flex items-center justify-center text-white text-xs font-bold">
            {user?.name?.[0]?.toUpperCase() ?? "U"}
          </div>
          <span className="text-sm text-header-text dark:text-dark-text hidden sm:block">
            {user?.name}
          </span>
        </div>

        {/* Logout */}
        <button
          onClick={logout}
          className="text-secondary-500 hover:text-error dark:text-dark-text-muted dark:hover:text-error"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
};

export default ChatHeader;