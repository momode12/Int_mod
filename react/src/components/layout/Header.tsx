import { useAuth } from "../../hooks/useAuth";
import { useUIStore } from "../../store/uiStore";
import { Menu, Moon, Sun, LogOut, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast, confirm } from "../../utils/sweetalert";
import { useThemeContext } from "../../providers/themeContext";

const Header = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useThemeContext();
  const { toggleSidebar, toggleSidebarCollapsed } = useUIStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    const ok = await confirm(
      "Hivoaka ve ianao ?",
      "Hiverina amin'ny pejy hiditra ianao"
    );
    if (ok) {
      logout();
      toast("Nivoaka soa aman-tsara", "success");
      navigate("/login");
    }
  };

  return (
    <header className="
      h-14 border-b border-header-border dark:border-dark-border
      bg-header-bg dark:bg-dark-surface
      flex items-center justify-between px-4 shrink-0 z-10
    ">
      <div className="flex items-center gap-3">
        <button
          onClick={() => {
            if (typeof window !== "undefined" && window.innerWidth >= 1024) {
              toggleSidebarCollapsed();
              return;
            }
            toggleSidebar();
          }}
          title="Asehoy/Afeno ny sisiny"
          className="text-secondary-500 cursor-pointer hover:text-secondary-800 dark:text-dark-text-muted dark:hover:text-dark-text transition-colors"
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

      <div className="flex items-center gap-2">
        {/* ✅ Lune / Soleil */}
        <button
          onClick={toggleTheme}
          title={theme === "light" ? "Alefa ny alina" : "Alefa ny andro"}
          className="
            p-2 rounded-lg transition-colors
            text-secondary-500 hover:text-secondary-800
            dark:text-dark-text-muted dark:hover:text-dark-text
            hover:bg-secondary-100 dark:hover:bg-dark-border cursor-pointer
          "
        >
          {theme === "light"
            ? <Moon size={18} />
            : <Sun size={18} className="text-yellow-400" />
          }
        </button>

        {/* Profil */}
        <button
          onClick={() => navigate("/profile")}
          title="Ny mombamombako"
          className="
            p-2 rounded-lg transition-colors cursor-pointer
            text-secondary-500 hover:text-secondary-800
            dark:text-dark-text-muted dark:hover:text-dark-text
            hover:bg-secondary-100 dark:hover:bg-dark-border
          "
        >
          <User size={18} />
        </button>

        {/* Avatar + anarana */}
        <div className="flex items-center gap-2 pl-2 border-l border-secondary-200 dark:border-dark-border">
          <div className="w-7 h-7 rounded-full bg-primary-500 flex items-center justify-center text-white text-xs font-bold">
            {user?.name?.[0]?.toUpperCase() ?? "U"}
          </div>
          <span className="text-sm text-header-text dark:text-dark-text hidden sm:block">
            {user?.name}
          </span>
        </div>

        {/* Hivoaka */}
        <button
          onClick={handleLogout}
          title="Hivoaka"
          className="
            p-2 rounded-lg transition-colors cursor-pointer
            text-secondary-500 hover:text-error
            dark:text-dark-text-muted dark:hover:text-error
          "
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
};

export default Header;
