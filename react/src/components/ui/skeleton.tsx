interface SkeletonProps {
  width?: string;
  height?: string;
  rounded?: string;
  className?: string;
}

const Skeleton = ({
  width = "w-full",
  height = "h-4",
  rounded = "rounded-lg",
  className = "",
}: SkeletonProps) => {
  return (
    <div
      className={`
        animate-pulse
        bg-secondary-200 dark:bg-dark-border
        ${width} ${height} ${rounded} ${className}
      `}
    />
  );
};

export const SkeletonMessage = () => (
  <div className="flex gap-3 px-4 py-2">
    <Skeleton width="w-8" height="h-8" rounded="rounded-full" />
    <div className="flex flex-col gap-2 flex-1">
      <Skeleton width="w-1/3" height="h-3" />
      <Skeleton width="w-2/3" height="h-3" />
      <Skeleton width="w-1/2" height="h-3" />
    </div>
  </div>
);

export default Skeleton;