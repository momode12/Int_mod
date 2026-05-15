import { useChat } from "../../hooks/useChat";
import { useUIStore } from "../../store/uiStore";
import ChatHistory from "../chat/ChatHistory";
import { Plus, X, MessageSquare } from "lucide-react";
import Tooltip from "../ui/tooltip";

const Sidebar = () => {
  const { newConversation } = useChat();
  const {
    isSidebarOpen,
    isSidebarCollapsed,
    setSidebarCollapsed,
    setSidebarOpen,
  } = useUIStore();

  return (
    <>
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden cursor-pointer"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside
        className={`
          fixed lg:relative z-30 top-0 left-0 h-full
          ${isSidebarCollapsed ? "w-16" : "w-64"} bg-sidebar-bg border-r border-sidebar-border
          flex flex-col transition-transform duration-300
          ${isSidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSidebarCollapsed(false)}
              className="cursor-pointer"
              title="Conversations"
            >
              <MessageSquare size={16} className="text-sidebar-text" />
            </button>
            {!isSidebarCollapsed && (
              <h2 className="text-sidebar-text font-semibold text-sm">Resaka</h2>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-sidebar-text hover:text-white transition-colors lg:hidden cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-3">
          {isSidebarCollapsed ? (
            <Tooltip content="Resaka vaovao">
              <button
                onClick={newConversation}
                className="
                  w-full flex items-center justify-center
                  px-3 py-2 rounded-lg bg-primary-500 hover:bg-primary-600
                  text-white text-sm font-medium transition-colors cursor-pointer
                "
              >
                <Plus size={16} />
              </button>
            </Tooltip>
          ) : (
            <button
              onClick={newConversation}
              className="
                w-full flex items-center justify-center gap-2
                px-3 py-2 rounded-lg bg-primary-500 hover:bg-primary-600
                text-white text-sm font-medium transition-colors cursor-pointer
              "
            >
              <Plus size={16} />
              Resaka vaovao
            </button>
          )}
        </div>

        {!isSidebarCollapsed && (
          <div className="flex-1 overflow-y-auto">
            <ChatHistory />
          </div>
        )}

        {!isSidebarCollapsed && (
          <div className="p-3 border-t border-sidebar-border">
            <p className="text-xs text-center text-sidebar-text opacity-50">
              ChatBot IA v1.0
            </p>
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;
