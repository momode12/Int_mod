import { create } from "zustand";

interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
}

interface ChatStore {
  conversations: Conversation[];
  currentConversationId: string | null;
  addConversation: (conversation: Conversation) => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  clearConversations: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  conversations: [],
  currentConversationId: null,

  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      currentConversationId: conversation.id,
    })),

  selectConversation: (id) =>
    set({ currentConversationId: id }),

  deleteConversation: (id) =>
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      currentConversationId:
        state.currentConversationId === id
          ? null
          : state.currentConversationId,
    })),

  clearConversations: () =>
    set({ conversations: [], currentConversationId: null }),
}));