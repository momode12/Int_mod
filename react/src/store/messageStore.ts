import { create } from "zustand";

export interface Message {
  id: string;
  conversationId: string;
  content: string;
  role: "user" | "bot";
  createdAt: Date;
}

interface MessageStore {
  messages: Message[];
  isTyping: boolean;
  addMessage: (message: Message) => void;
  setIsTyping: (value: boolean) => void;
  getMessagesByConversation: (conversationId: string) => Message[];
  clearMessages: (conversationId: string) => void;
}

export const useMessageStore = create<MessageStore>((set, get) => ({
  messages: [],
  isTyping: false,

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setIsTyping: (value) =>
    set({ isTyping: value }),

  getMessagesByConversation: (conversationId) =>
    get().messages.filter((m) => m.conversationId === conversationId),

  clearMessages: (conversationId) =>
    set((state) => ({
      messages: state.messages.filter(
        (m) => m.conversationId !== conversationId
      ),
    })),
}));