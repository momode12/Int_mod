import { useState, useCallback } from "react";
import { ChatContext } from "./chatContext";
import type {  ReactNode } from "react";
import type { ChatContextType, Conversation, Message } from "./chatContext";

const generateId = () => Math.random().toString(36).substring(2, 9);

const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isTyping, setIsTyping] = useState(false);

  const newConversation = useCallback(() => {
    const conversation: Conversation = {
      id: generateId(),
      title: "Nouvelle conversation",
      messages: [],
    };
    setConversations((prev) => [conversation, ...prev]);
    setCurrentConversation(conversation);
  }, []);

  const selectConversation = useCallback((id: string) => {
    setConversations((prev) => {
      const found = prev.find((c) => c.id === id);
      if (found) setCurrentConversation(found);
      return prev;
    });
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!currentConversation) return;

    const userMessage: Message = {
      id: generateId(),
      content,
      role: "user",
      createdAt: new Date(),
    };

    const updated: Conversation = {
      ...currentConversation,
      messages: [...currentConversation.messages, userMessage],
    };

    setCurrentConversation(updated);
    setConversations((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
    setIsTyping(true);

    await new Promise((resolve) => setTimeout(resolve, 1500));

    const botMessage: Message = {
      id: generateId(),
      content: "Je suis le bot, je traite votre message...",
      role: "bot",
      createdAt: new Date(),
    };

    const withBot: Conversation = {
      ...updated,
      messages: [...updated.messages, botMessage],
    };

    setCurrentConversation(withBot);
    setConversations((prev) => prev.map((c) => (c.id === withBot.id ? withBot : c)));
    setIsTyping(false);
  }, [currentConversation]);

  const value: ChatContextType = {
    conversations,
    currentConversation,
    messages: currentConversation?.messages ?? [],
    isTyping,
    sendMessage,
    newConversation,
    selectConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export default ChatProvider;