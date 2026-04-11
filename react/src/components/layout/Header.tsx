import { useAuth } from "../../hooks/useAuth";
import { useUIStore } from "../../store/uiStore";
import { Menu, Moon, Sun, LogOut, User } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme, toggleSidebar } = useUIStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="
      h-14 border-b border-header-border dark:border-dark-border
      bg-header-bg dark:bg-dark-surface
      flex items-center justify-between px-4 shrink-0 z-10
    ">
      {/* Gauche */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="text-secondary-500 hover:text-secondary-800 dark:text-dark-text-muted dark:hover:text-dark-text transition-colors"
        >
          <Menu size={20} />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-primary-500 flex items-center justify-center">
            <span className="text-white font-bold text-xs">AI</span>
          </div>
          <span className="font-semibold text-header-text dark:text-dark-text text-sm">
            ChatBot IA
          </span>
        </div>
      </div>

      {/* Droite */}
      <div className="flex items-center gap-2">
        {/* Toggle theme */}
        <button
          onClick={toggleTheme}
          className="
            p-2 rounded-lg text-secondary-500 hover:text-secondary-800
            dark:text-dark-text-muted dark:hover:text-dark-text
            hover:bg-secondary-100 dark:hover:bg-dark-surface transition-colors
          "
        >
          {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        {/* Profile */}
        <button
          onClick={() => navigate("/profile")}
          className="
            p-2 rounded-lg text-secondary-500 hover:text-secondary-800
            dark:text-dark-text-muted dark:hover:text-dark-text
            hover:bg-secondary-100 dark:hover:bg-dark-surface transition-colors
          "
        >
          <User size={18} />
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-secondary-200 dark:border-dark-border">
          <div className="w-7 h-7 rounded-full bg-primary-500 flex items-center justify-center text-white text-xs font-bold">
            {user?.name?.[0]?.toUpperCase() ?? "U"}
          </div>
          <span className="text-sm text-header-text dark:text-dark-text hidden sm:block">
            {user?.name}
          </span>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="
            p-2 rounded-lg text-secondary-500 hover:text-error
            dark:text-dark-text-muted dark:hover:text-error transition-colors
          "
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
};

export default Header;