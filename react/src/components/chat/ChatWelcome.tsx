import { useChat } from "../../hooks/useChat";
import { MessageSquare } from "lucide-react";

const ChatWelcome = () => {
  const { newConversation } = useChat();

  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 p-8">
      <div className="w-16 h-16 rounded-full bg-primary-500 flex items-center justify-center">
        <MessageSquare size={32} className="text-white" />
      </div>
      <div className="text-center">
        <h2 className="text-xl font-bold text-secondary-800 dark:text-dark-text mb-2">
          Tonga soa ao amin'ny ChatBot IA
        </h2>
        <p className="text-sm text-secondary-500 dark:text-dark-text-muted max-w-sm">
          Atombohy resaka vaovao hifandraisan'ny amin'ny AI.
        </p>
      </div>
      <button
        onClick={newConversation}
        className="
          px-6 py-2 rounded-xl bg-primary-500 hover:bg-primary-600
          text-white text-sm font-medium transition-colors
        "
      >
        Resaka vaovao
      </button>
    </div>
  );
};

export default ChatWelcome;