export const formatDate = (date: Date): string => {
  const now = new Date();
  const diff = now.getTime() - new Date(date).getTime();

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours   = Math.floor(minutes / 60);
  const days    = Math.floor(hours / 24);

  if (seconds < 60)  return "À l'instant";
  if (minutes < 60)  return `Il y a ${minutes} min`;
  if (hours < 24)    return `Il y a ${hours}h`;
  if (days < 7)      return `Il y a ${days}j`;

  return new Intl.DateTimeFormat("fr-FR", {
    day:   "2-digit",
    month: "2-digit",
    year:  "numeric",
  }).format(new Date(date));
};

export const formatTime = (date: Date): string => {
  return new Intl.DateTimeFormat("fr-FR", {
    hour:   "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
};

export const formatFullDate = (date: Date): string => {
  return new Intl.DateTimeFormat("fr-FR", {
    day:    "2-digit",
    month:  "long",
    year:   "numeric",
    hour:   "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
};