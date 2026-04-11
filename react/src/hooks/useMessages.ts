import { useState } from "react";
import { useChat } from "./useChat";

export const useMessages = () => {
  const { messages, sendMessage, isTyping } = useChat();
  const [inputValue, setInputValue] = useState("");

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    await sendMessage(inputValue);
    setInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return {
    messages,
    inputValue,
    isTyping,
    setInputValue,
    handleSend,
    handleKeyDown,
  };
};