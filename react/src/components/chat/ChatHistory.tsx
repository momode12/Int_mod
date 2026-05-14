import { useChat } from "../../hooks/useChat";
import { MessageSquare, Trash2 } from "lucide-react";
import { confirm, toast } from "../../utils/sweetalert";
const ChatHistory = () => {
  const {
    conversations,
    currentConversation,
    selectConversation,
    deleteConversation,
  } = useChat();

  if (conversations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-32 text-secondary-400 dark:text-dark-text-muted text-sm gap-2">
        <MessageSquare size={24} />
        <span>Tsy misy resaka</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1 p-2">
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          onClick={() => selectConversation(conversation.id)}
          className={`
            group flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left
            transition-colors w-full cursor-pointer
            ${currentConversation?.id === conversation.id
              ? "bg-sidebar-active text-white"
              : "text-sidebar-text hover:bg-sidebar-hover"}
          `}
        >
          <MessageSquare size={16} className="shrink-0" />
          <div className="flex-1 min-w-0">
              <span className="truncate block">{conversation.title}</span>         
          </div>
          <button
            type="button"
            onClick={async (e) => {
              e.stopPropagation();
              const ok = await confirm(
                "Hamafa ny resaka tokoa ve ianao?",
                `Hamafa ny resaka "${conversation.title}" ?`,
              );
              if (!ok) return;
              const deleted = await deleteConversation(conversation.id);
              if (deleted) toast("Voafafa tsara ilay resaka nofafanao teo", "success");
            }}
            className={`
              p-1 rounded transition-opacity
              opacity 10 group-hover:opacity 100 cursor-pointer
              ${currentConversation?.id === conversation.id ? "hover:bg-white/10" : "hover:bg-black/10"}
            `}
            title="Fafao"
          >
            <Trash2 size={14} className="text-error" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default ChatHistory;
