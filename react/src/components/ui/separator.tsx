interface SeparatorProps {
  label?: string;
  orientation?: "horizontal" | "vertical";
}

const Separator = ({ label, orientation = "horizontal" }: SeparatorProps) => {
  if (orientation === "vertical") {
    return (
      <div className="w-px bg-secondary-200 dark:bg-dark-border self-stretch" />
    );
  }

  if (label) {
    return (
      <div className="flex items-center gap-3">
        <div className="flex-1 h-px bg-secondary-200 dark:bg-dark-border" />
        <span className="text-xs text-secondary-400 dark:text-dark-text-muted whitespace-nowrap">
          {label}
        </span>
        <div className="flex-1 h-px bg-secondary-200 dark:bg-dark-border" />
      </div>
    );
  }

  return (
    <div className="h-px w-full bg-secondary-200 dark:bg-dark-border" />
  );
};

export default Separator;