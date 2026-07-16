import { cn } from '@stellar-ui-kit/shared';
import { Text } from '@stellar-ui-kit/web';

import { Check } from 'lucide-react';

import type { TitlePreset } from '../presets';

type PresetChipsProps = {
  label: string;
  description?: string;
  presets: TitlePreset[];
  selected: string[];
  onToggle: (id: string) => void;
};

export function PresetChips({ label, description, presets, selected, onToggle }: PresetChipsProps) {
  return (
    <div className="space-y-2">
      <div>
        <Text as="p" className="text-sm font-semibold">
          {label}
        </Text>
        {description && (
          <Text as="p" styleVariant="muted" className="mt-0.5 text-xs">
            {description}
          </Text>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {presets.map((preset) => {
          const active = selected.includes(preset.id);
          return (
            <button
              key={preset.id}
              type="button"
              className={cn(
                'flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors',
                active
                  ? 'border-primary bg-primary-soft text-primary-text'
                  : 'border-border text-muted hover:border-primary hover:text-primary-text',
              )}
              onClick={() => onToggle(preset.id)}
            >
              {active && <Check className="size-3" />}
              {preset.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
