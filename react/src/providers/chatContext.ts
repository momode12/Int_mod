import { createContext, useContext } from "react";

export interface Message {
  id: string;
  content: string;
  role: "user" | "bot";
  createdAt: Date;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
}

export interface ChatContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isTyping: boolean;
  sendMessage: (content: string) => Promise<void>;
  newConversation: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChatContext must be used within ChatProvider");
  return context;
};
