interface AvatarProps {
  name?: string;
  src?: string;
  size?: "sm" | "md" | "lg";
  role?: "user" | "bot";
}

const Avatar = ({ name, src, size = "md", role = "user" }: AvatarProps) => {
  const sizes = {
    sm: "w-7 h-7 text-xs",
    md: "w-9 h-9 text-sm",
    lg: "w-12 h-12 text-base",
  };

  const initial = name ? name[0].toUpperCase() : role === "bot" ? "B" : "U";

  return (
    <div
      className={`
        rounded-full flex items-center justify-center font-bold shrink-0
        ${sizes[size]}
        ${role === "bot"
          ? "bg-primary-500 text-white"
          : "bg-secondary-200 dark:bg-dark-surface text-secondary-700 dark:text-dark-text"}
      `}
    >
      {src ? (
        <img
          src={src}
          alt={name}
          className="w-full h-full rounded-full object-cover"
        />
      ) : (
        initial
      )}
    </div>
  );
};

export default Avatar;