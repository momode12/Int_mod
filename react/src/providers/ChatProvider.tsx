import { useState, useCallback, useEffect, useMemo } from "react";
import { ChatContext } from "./chatContext";
import type { ReactNode } from "react";
import type { ChatContextType, Conversation, Message } from "./chatContext";
import { api } from "../utils/api";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { generateConversationTitle, trimMessage } from "../utils/formatMessage";
import { useUIStore } from "../store/uiStore";

const generateId = () => Math.random().toString(36).substring(2, 9);

type ApiConversation = {
  id: string;
  nom_conversation: string;
  created_at: string;
  updated_at?: string;
};

type ApiMessage = {
  id: string;
  texte?: string | null;
  categorie?: string | null;
  label_fr?: string | null;
  icon?: string | null;
  confidence?: number | null;
  indicator?: "green" | "yellow" | "red" | null;
  tfidf_sim?: number | null;
  medicament1?: string | null;
  medicament2?: string | null;
  astuce?: string | null;
  generated?: string | null;
  top3?: Array<{ categorie: string; icon?: string; score: number }> | null;
  alerte?: string | null;
  fallback?: string | null;
  ood?: boolean | null;
  created_at: string;
};

type ApiConversationDetails = ApiConversation & { messages: ApiMessage[] };

type ApiChatResponse =
  | (ApiMessage & {
      message_id: string;
      type?: string;
      created_at: string;
    })
  | { type: "salutation"; response: string };

const ChatProvider = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const { setSidebarOpen } = useUIStore();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] =
    useState<Conversation | null>(null);
  const [isTyping, setIsTyping] = useState(false);

  const buildBotContent = useCallback((m: ApiMessage) => {
    const generated = (m.generated ?? "").trim();
    if (generated) {
      const parts: string[] = [];
      if (m.alerte && !generated.includes(m.alerte)) parts.push(m.alerte);
      parts.push(generated);
      if (m.fallback && !generated.includes(m.fallback)) parts.push(m.fallback);
      return parts.filter(Boolean).join("\n\n");
    }

    const parts: string[] = [];
    const icon = m.icon ?? "";
    const label = m.label_fr ?? m.categorie ?? "Réponse";
    const confidence =
      typeof m.confidence === "number" ? `${Math.round(m.confidence)}%` : null;

    if (m.alerte) parts.push(m.alerte);

    const header = [icon, label, confidence ? `(${confidence})` : ""]
      .filter(Boolean)
      .join(" ");
    if (header) parts.push(header);

    const meds = [m.medicament1, m.medicament2].filter(Boolean);
    if (meds.length) parts.push(meds.join(" / "));
    if (m.astuce) parts.push(m.astuce);
    if (m.fallback) parts.push(m.fallback);

    return parts.filter(Boolean).join("\n");
  }, []);

  const mapApiMessages = useCallback(
    (apiMessages: ApiMessage[]): Message[] => {
      return apiMessages.flatMap((m) => {
        const createdAt = new Date(m.created_at);
        const user: Message = {
          id: `${m.id}-user`,
          content: m.texte ?? "",
          role: "user",
          createdAt,
        };
        const bot: Message = {
          id: `${m.id}-bot`,
          content: buildBotContent(m),
          role: "bot",
          createdAt,
        };
        return [user, bot];
      });
    },
    [buildBotContent],
  );

  const fetchConversations = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await api.get<ApiConversation[]>("/conversations");
      const mapped: Conversation[] = data.map((c) => ({
        id: c.id,
        title: c.nom_conversation,
        messages: [],
        createdAt: new Date(c.created_at),
        updatedAt: new Date(c.updated_at ?? c.created_at),
      }));
      setConversations(mapped);
    } catch (e) {
      showToast(
        e instanceof Error ? e.message : "Erreur chargement conversations",
        "error",
      );
    }
  }, [isAuthenticated, showToast]);

  useEffect(() => {
    if (!isAuthenticated) {
      setConversations([]);
      setCurrentConversation(null);
      setIsTyping(false);
      return;
    }
    fetchConversations();
  }, [isAuthenticated, fetchConversations]);

  const createConversation =
    useCallback(async (): Promise<Conversation | null> => {
      try {
        const created = await api.post<ApiConversation>("/conversations", {
          nom_conversation: "Nouvelle conversation",
        });
        const conversation: Conversation = {
          id: created.id,
          title: created.nom_conversation,
          messages: [],
          createdAt: new Date(created.created_at),
          updatedAt: new Date(created.updated_at ?? created.created_at),
        };
        setConversations((prev) => [conversation, ...prev]);
        setCurrentConversation(conversation);
        return conversation;
      } catch (e) {
        showToast(
          e instanceof Error ? e.message : "Erreur création conversation",
          "error",
        );
        return null;
      }
    }, [showToast]);

  const newConversation = useCallback(async () => {
    if (!isAuthenticated) return;
    await createConversation();
  }, [createConversation, isAuthenticated]);

  const selectConversation = useCallback(
    async (id: string) => {
      if (!isAuthenticated) return;
      try {
        const conv = await api.get<ApiConversationDetails>(
          `/conversations/${id}`,
        );
        const conversation: Conversation = {
          id: conv.id,
          title: conv.nom_conversation,
          messages: mapApiMessages(conv.messages ?? []),
          createdAt: new Date(conv.created_at),
          updatedAt: new Date(conv.updated_at ?? conv.created_at),
        };
        setCurrentConversation(conversation);
        setConversations((prev) =>
          prev.map((c) =>
            c.id === conversation.id
              ? {
                  ...c,
                  title: conversation.title,
                  createdAt: conversation.createdAt,
                  updatedAt: conversation.updatedAt,
                }
              : c,
          ),
        );
      } catch (e) {
        showToast(
          e instanceof Error ? e.message : "Erreur chargement conversation",
          "error",
        );
      }
    },
    [isAuthenticated, mapApiMessages, showToast],
  );

  const deleteConversation = useCallback(
    async (id: string): Promise<boolean> => {
      if (!isAuthenticated) return false;
      try {
        await api.delete(`/conversations/${id}`);
        setConversations((prev) => prev.filter((c) => c.id !== id));
        setCurrentConversation((prev) => (prev?.id === id ? null : prev));
        setSidebarOpen(false);
        return true;
      } catch (e) {
        showToast(
          e instanceof Error ? e.message : "Erreur suppression conversation",
          "error",
        );
        return false;
      }
    },
    [isAuthenticated, setSidebarOpen, showToast],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (!isAuthenticated) return;

      const cleaned = trimMessage(content);
      if (!cleaned) return;

      let activeConversation = currentConversation;
      if (!activeConversation) {
        activeConversation = await createConversation();
        if (!activeConversation) return;
      }

      const optimisticId = generateId();
      const userMessage: Message = {
        id: optimisticId,
        content: cleaned,
        role: "user",
        createdAt: new Date(),
      };

      const optimistic: Conversation = {
        ...activeConversation,
        messages: [...activeConversation.messages, userMessage],
      };

      setCurrentConversation(optimistic);
      setIsTyping(true);

      try {
        const res = await api.post<ApiChatResponse>(
          `/conversations/${activeConversation.id}/chat`,
          { texte: cleaned },
        );

        if ("response" in res && res.type === "salutation") {
          const serverDate = new Date();
          const botMessage: Message = {
            id: generateId(),
            content: res.response,
            role: "bot",
            createdAt: serverDate,
          };
          setCurrentConversation((prev) =>
            prev
              ? {
                  ...prev,
                  updatedAt: serverDate,
                  messages: [
                    ...prev.messages.map((m) =>
                      m.id === optimisticId ? { ...m, createdAt: serverDate } : m,
                    ),
                    botMessage,
                  ],
                }
              : prev,
          );
          setConversations((prev) =>
            prev.map((c) =>
              c.id === activeConversation.id ? { ...c, updatedAt: serverDate } : c,
            ),
          );
          return;
        }

        const serverDate = new Date(res.created_at);
        const apiMessage: ApiMessage = {
          id: res.message_id,
          texte: cleaned,
          categorie: res.categorie,
          label_fr: res.label_fr,
          icon: res.icon,
          confidence: res.confidence,
          indicator: res.indicator,
          tfidf_sim: res.tfidf_sim,
          medicament1: res.medicament1,
          medicament2: res.medicament2,
          astuce: res.astuce,
          generated: res.generated,
          top3: res.top3,
          alerte: res.alerte,
          fallback: res.fallback,
          ood: res.ood,
          created_at: res.created_at,
        };

        const botMessage: Message = {
          id: `${apiMessage.id}-bot-live`,
          content: buildBotContent(apiMessage),
          role: "bot",
          createdAt: serverDate,
        };

        setCurrentConversation((prev) =>
          prev
            ? {
                ...prev,
                updatedAt: serverDate,
                messages: [
                  ...prev.messages.map((m) =>
                    m.id === optimisticId ? { ...m, createdAt: serverDate } : m,
                  ),
                  botMessage,
                ],
              }
            : prev,
        );
        setConversations((prev) =>
          prev.map((c) =>
            c.id === activeConversation.id ? { ...c, updatedAt: serverDate } : c,
          ),
        );

        const title = activeConversation.title?.trim();
        if (!title || title === "Nouvelle conversation") {
          const conversationId = activeConversation.id;
          const newTitle = generateConversationTitle(cleaned);
          await api.put(`/conversations/${conversationId}`, {
            nom_conversation: newTitle,
          });
          setConversations((prev) =>
            prev.map((c) =>
              c.id === conversationId ? { ...c, title: newTitle } : c,
            ),
          );
          setCurrentConversation((prev) =>
            prev ? { ...prev, title: newTitle } : prev,
          );
        }
      } catch (e) {
        showToast(
          e instanceof Error ? e.message : "Erreur envoi message",
          "error",
        );
      } finally {
        setIsTyping(false);
      }
    },
    [
      buildBotContent,
      createConversation,
      currentConversation,
      isAuthenticated,
      showToast,
    ],
  );

  const value: ChatContextType = useMemo(
    () => ({
      conversations,
      currentConversation,
      messages: currentConversation?.messages ?? [],
      isTyping,
      sendMessage,
      newConversation,
      selectConversation,
      deleteConversation,
    }),
    [
      conversations,
      currentConversation,
      isTyping,
      sendMessage,
      newConversation,
      selectConversation,
      deleteConversation,
    ],
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export default ChatProvider;
