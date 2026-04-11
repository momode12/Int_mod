import { useChat } from "../../hooks/useChat";
import { useAuth } from "../../hooks/useAuth";
import { useScrollBottom } from "../../hooks/useScrollBottom";
import ChatMessage from "./ChatMessage";
import ChatTypingIndicator from "./ChatTypingIndicator";
import ChatWelcome from "./ChatWelcome";

const ChatWindow = () => {
  const { messages, isTyping, currentConversation } = useChat();
  const { user } = useAuth();
  const { bottomRef } = useScrollBottom(messages);

  if (!currentConversation) {
    return <ChatWelcome />;
  }

  return (
    <div className="flex-1 overflow-y-auto bg-chat-background dark:bg-dark-background py-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-secondary-400 dark:text-dark-text-muted text-sm">
          Envoyez un message pour commencer
        </div>
      ) : (
        <div className="flex flex-col gap-2 max-w-4xl mx-auto">
          {messages.map((message: typeof messages[0]) => (
            <ChatMessage
              key={message.id}
              message={message}
              userName={user?.name}
            />
          ))}
          <ChatTypingIndicator isTyping={isTyping} />
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
};

export default ChatWindow;