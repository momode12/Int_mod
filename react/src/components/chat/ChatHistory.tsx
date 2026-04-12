import { useChat } from "../../hooks/useChat";
import { MessageSquare } from "lucide-react";

const ChatHistory = () => {
  const { conversations, currentConversation, selectConversation } = useChat();

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
        <button
          key={conversation.id}
          onClick={() => selectConversation(conversation.id)}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left
            transition-colors w-full cursor-pointer
            ${currentConversation?.id === conversation.id
              ? "bg-sidebar-active text-white"
              : "text-sidebar-text hover:bg-sidebar-hover"}
          `}
        >
          <MessageSquare size={16} className="shrink-0" />
          <span className="flex-1 truncate">{conversation.title}</span>
        </button>
      ))}
    </div>
  );
};

export default ChatHistory;