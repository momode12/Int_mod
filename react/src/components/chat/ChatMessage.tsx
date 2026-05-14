import ChatBubble from "./ChatBubble";

interface Message {
  id: string;
  content: string;
  role: "user" | "bot";
  createdAt: Date;
}

interface ChatMessageProps {
  message: Message;
  userName?: string;
}

const ChatMessage = ({ message, userName }: ChatMessageProps) => {
  return (
    <div className="px-4 py-1">
      <ChatBubble
        content={message.content}
        role={message.role}
        createdAt={message.createdAt}
        name={message.role === "user" ? userName : "Bot"}
      />
    </div>
  );
};

export default ChatMessage;