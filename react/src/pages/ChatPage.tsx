import ChatLayout from "../components/layout/ChatLayout";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";

const ChatPage = () => {
  return (
    <ChatLayout>
      {/* Faritra hafatra */}
      <ChatWindow />

      {/* Faritra fanoratana */}
      <ChatInput />
    </ChatLayout>
  );
};

export default ChatPage;