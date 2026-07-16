import { cn } from '@stellar-ui-kit/shared';

const sizes = {
  sm: 'size-9 rounded-lg text-[11px]',
  lg: 'size-12 rounded-xl text-sm',
} as const;

type InitialsAvatarProps = {
  name: string;
  size?: keyof typeof sizes;
  className?: string;
};

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();
}

export function InitialsAvatar({ name, size = 'sm', className }: InitialsAvatarProps) {
  return (
    <div
      aria-hidden
      className={cn(
        'flex shrink-0 select-none items-center justify-center bg-secondary-soft font-semibold uppercase text-secondary-text ring-1 ring-border',
        sizes[size],
        className,
      )}
    >
      {initials(name)}
    </div>
  );
}
