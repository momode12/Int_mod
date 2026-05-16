import { useMessages } from "../../hooks/useMessages";
import { Send } from "lucide-react";

const ChatInput = () => {
  const { inputValue, setInputValue, handleSend, handleKeyDown } = useMessages();

  return (
    <div className="border-t border-chat-input-border dark:border-dark-border bg-chat-input-bg dark:bg-dark-surface p-4">
      <div className="flex gap-2 items-end max-w-4xl mx-auto">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Soraty ny hafatra..."
          rows={1}
          className="
            flex-1 resize-none rounded-xl border border-chat-input-border
            dark:border-dark-border bg-white dark:bg-dark-background
            text-secondary-800 dark:text-dark-text
            placeholder:text-secondary-400 dark:placeholder:text-dark-text-muted
            px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-primary-500
            max-h-40 overflow-y-auto transition-colors
          "
        />
        <button
          onClick={handleSend}
          disabled={!inputValue.trim()}
          title="Handefa hafatra"
          className="
            p-2 rounded-xl bg-primary-500 hover:bg-primary-600
            disabled:opacity-50 disabled:cursor-not-allowed
            text-white transition-colors shrink-0 cursor-pointer
          "
        >
          <Send size={18} />
        </button>
      </div>
      <p className="text-xs text-center text-secondary-400 dark:text-dark-text-muted mt-2">
        Afaka manao hadisoana ny {" "}
        <kbd className="px-1 py-0.5 rounded bg-secondary-100 dark:bg-dark-surface text-xs">
          Chat bot médical Malagasy 
        </kbd>{" "}
        fa manantona ihany dokotera.
      </p>
    </div>
  );
};

export default ChatInput;