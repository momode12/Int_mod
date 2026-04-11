import { useState, useEffect } from "react";

export const useTypingIndicator = (isTyping: boolean) => {
  const [dots, setDots] = useState(".");

  useEffect(() => {
    if (!isTyping) return;

    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "." : prev + "."));
    }, 500);

    return () => clearInterval(interval);
  }, [isTyping]);

  return { dots };
};