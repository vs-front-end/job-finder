import { useState, type KeyboardEvent } from 'react';

import { cn } from '@stellar-ui-kit/shared';
import { Text } from '@stellar-ui-kit/web';

import { Plus, X } from 'lucide-react';

type ChipListFieldProps = {
  label: string;
  description?: string;
  values: string[];
  suggestions?: string[];
  placeholder?: string;
  onChange: (values: string[]) => void;
};

export function ChipListField({
  label,
  description,
  values,
  suggestions = [],
  placeholder,
  onChange,
}: ChipListFieldProps) {
  const [draft, setDraft] = useState('');
  const available = suggestions.filter((suggestion) => !values.includes(suggestion));

  const add = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || values.includes(trimmed)) return;
    onChange([...values, trimmed]);
    setDraft('');
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== 'Enter') return;
    event.preventDefault();
    add(draft);
  };

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
      <div className="flex flex-wrap items-center gap-1.5">
        {values.map((value) => (
          <span
            key={value}
            className="flex items-center gap-1 rounded-lg bg-primary-soft py-1 pl-2.5 pr-1 text-xs font-medium text-primary-text"
          >
            {value}
            <button
              type="button"
              aria-label={`Remove ${value}`}
              className="rounded p-0.5 hover:bg-surface"
              onClick={() => onChange(values.filter((item) => item !== value))}
            >
              <X className="size-3" />
            </button>
          </span>
        ))}
        <input
          value={draft}
          placeholder={placeholder ?? 'Add and press Enter'}
          className={cn(
            'h-7 min-w-40 flex-1 rounded-lg border border-dashed border-border bg-transparent px-2.5 text-xs',
            'placeholder:text-muted focus:border-primary focus:outline-none',
          )}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => add(draft)}
        />
      </div>
      {available.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {available.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              className="flex items-center gap-1 rounded-lg border border-border px-2 py-1 text-xs text-muted transition-colors hover:border-primary hover:text-primary-text"
              onClick={() => add(suggestion)}
            >
              <Plus className="size-3" /> {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
