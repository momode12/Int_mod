import { useChat } from "../../hooks/useChat";
import { useUIStore } from "../../store/uiStore";
import ChatHistory from "./ChatHistory";
import { Plus, X } from "lucide-react";

const ChatSidebar = () => {
  const { newConversation } = useChat();
  const { isSidebarOpen, setSidebarOpen } = useUIStore();

  return (
    <>
      {/* Overlay mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed lg:relative z-30 top-0 left-0 h-full
          w-64 bg-sidebar-bg border-r border-sidebar-border
          flex flex-col transition-transform duration-300
          ${isSidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        {/* Header sidebar */}
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          <h2 className="text-sidebar-text font-semibold text-sm">Conversations</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-sidebar-text hover:text-white lg:hidden"
          >
            <X size={18} />
          </button>
        </div>

        {/* Nouvelle conversation */}
        <div className="p-3">
          <button
            onClick={newConversation}
            className="
              w-full flex items-center gap-2 px-3 py-2 rounded-lg
              bg-primary-500 hover:bg-primary-600 text-white
              text-sm font-medium transition-colors
            "
          >
            <Plus size={16} />
            Nouvelle conversation
          </button>
        </div>

        {/* Historique */}
        <div className="flex-1 overflow-y-auto">
          <ChatHistory />
        </div>
      </aside>
    </>
  );
};

export default ChatSidebar;