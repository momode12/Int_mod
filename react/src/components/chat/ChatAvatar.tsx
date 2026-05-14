interface ChatAvatarProps {
  role: "user" | "bot";
  name?: string;
}

const ChatAvatar = ({ role, name }: ChatAvatarProps) => {
  const initial = name ? name[0].toUpperCase() : role === "bot" ? "B" : "U";

  return (
    <div
      className={`
        w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0
        ${role === "bot"
          ? "bg-primary-500 text-white"
          : "bg-secondary-200 text-secondary-700 dark:bg-dark-surface dark:text-dark-text"}
      `}
    >
      {initial}
    </div>
  );
};

export default ChatAvatar;