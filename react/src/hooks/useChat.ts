import { useChatContext } from "../providers/chatContext";

export const useChat = () => {
  return useChatContext();
};