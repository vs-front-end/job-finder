import { cn } from '@stellar-ui-kit/shared';
import { Text } from '@stellar-ui-kit/web';

import { queueGroups, type QueueTab } from './queue';

type QueueSidebarProps = {
  tab: QueueTab;
  countFor: (tab: QueueTab) => number;
  onChange: (tab: QueueTab) => void;
};

export function QueueSidebar({ tab, countFor, onChange }: QueueSidebarProps) {
  return (
    <aside className="hidden h-full min-h-0 space-y-7 overflow-y-auto bg-surface px-4 py-6 lg:block">
      {queueGroups.map((group) => (
        <div key={group.label}>
          <Text
            as="p"
            styleVariant="muted"
            className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.14em]"
          >
            {group.label}
          </Text>
          <nav className="space-y-0.5">
            {group.items.map((item) => {
              const Icon = item.icon;
              const active = tab === item.value;
              return (
                <button
                  key={item.value}
                  type="button"
                  className={cn(
                    'relative flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm transition-colors',
                    active
                      ? 'bg-primary-soft font-semibold text-primary-text before:absolute before:-left-4 before:top-1/2 before:h-6 before:w-0.5 before:-translate-y-1/2 before:rounded-full before:bg-primary'
                      : 'text-muted hover:bg-secondary-soft hover:text-foreground',
                  )}
                  onClick={() => onChange(item.value)}
                >
                  <Icon className="size-4 shrink-0" />
                  <span className="min-w-0 flex-1 text-left">{item.label}</span>
                  <span
                    className={cn(
                      'min-w-6 rounded-md bg-secondary-soft px-1.5 py-0.5 text-center text-[10px]',
                      active && 'bg-surface text-primary-text',
                    )}
                  >
                    {countFor(item.value)}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      ))}
    </aside>
  );
}
