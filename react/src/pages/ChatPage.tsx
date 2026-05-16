import ChatLayout from "../components/layout/ChatLayout";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";

const ChatPage = () => {
  return (
    <ChatLayout>
      <ChatWindow />

      <ChatInput />
    </ChatLayout>
  );
};

export default ChatPage;