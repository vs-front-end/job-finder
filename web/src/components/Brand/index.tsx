import { Text } from '@stellar-ui-kit/web';

import { Radar } from 'lucide-react';

export function Brand() {
  return (
    <div className="flex shrink-0 items-center gap-3">
      <div className="relative flex size-10 items-center justify-center rounded-xl bg-primary text-surface shadow-sm">
        <Radar className="size-5" />
        <span className="absolute right-1.5 top-1.5 size-1 rounded-full bg-surface" />
      </div>
      <div className="hidden sm:block">
        <Text as="p" className="font-display text-base font-bold leading-none tracking-tight">
          Job Finder
        </Text>
        <Text as="p" styleVariant="muted" className="mt-1 text-[11px] leading-none">
          Seu radar de oportunidades
        </Text>
      </div>
    </div>
  );
}
