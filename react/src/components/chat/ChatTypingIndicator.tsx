import ChatAvatar from "./ChatAvatar";
import { useTypingIndicator } from "../../hooks/useTypingIndicator";

interface ChatTypingIndicatorProps {
  isTyping: boolean;
}

const ChatTypingIndicator = ({ isTyping }: ChatTypingIndicatorProps) => {
  useTypingIndicator(isTyping);

  if (!isTyping) return null;

  return (
    <div className="flex gap-3 flex-row">
      <ChatAvatar role="bot" />
      <div className="bg-chat-bot-bubble dark:bg-dark-bot-bubble px-4 py-2 rounded-2xl rounded-tl-sm">
        <div className="flex gap-1 items-center h-5">
          <span className="w-2 h-2 rounded-full bg-secondary-400 dark:bg-dark-text-muted animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 rounded-full bg-secondary-400 dark:bg-dark-text-muted animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 rounded-full bg-secondary-400 dark:bg-dark-text-muted animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
};

export default ChatTypingIndicator;