import ChatAvatar from "./ChatAvatar";
import { formatDate } from "../../utils/formatDate";

interface ChatBubbleProps {
  content: string;
  role: "user" | "bot";
  createdAt: Date;
  name?: string;
}

const ChatBubble = ({ content, role, createdAt, name }: ChatBubbleProps) => {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <ChatAvatar role={role} name={name} />

      <div className={`flex flex-col gap-1 max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`
            px-4 py-2 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
            ${isUser
              ? "bg-chat-user-bubble text-chat-user-text rounded-tr-sm dark:bg-dark-user-bubble"
              : "bg-chat-bot-bubble text-chat-bot-text rounded-tl-sm dark:bg-dark-bot-bubble dark:text-dark-text"}
          `}
        >
          {content}
        </div>
        <span className="text-xs text-secondary-400 dark:text-dark-text-muted">
          {formatDate(createdAt)}
        </span>
      </div>
    </div>
  );
};

export default ChatBubble;
