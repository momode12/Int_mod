import { useChatContext } from "../providers/ChatProvider";

export const useChat = () => {
  return useChatContext();
};