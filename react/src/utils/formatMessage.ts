// Nettoie les espaces inutiles
export const trimMessage = (content: string): string => {
  return content.trim().replace(/\s+/g, " ");
};

// Tronque un message trop long
export const truncateMessage = (content: string, maxLength = 100): string => {
  if (content.length <= maxLength) return content;
  return content.slice(0, maxLength).trimEnd() + "...";
};

// Titre d'une conversation à partir du premier message
export const generateConversationTitle = (firstMessage: string): string => {
  return truncateMessage(firstMessage, 40);
};

// Vérifie si le message est vide
export const isEmptyMessage = (content: string): boolean => {
  return content.trim().length === 0;
};

// Compte les mots d'un message
export const countWords = (content: string): number => {
  return content.trim().split(/\s+/).filter(Boolean).length;
};