import { InputText } from '@stellar-ui-kit/web';

import { Search } from 'lucide-react';

type JobsToolbarProps = {
  query: string;
  onQueryChange: (value: string) => void;
};

export function JobsToolbar({ query, onQueryChange }: JobsToolbarProps) {
  return (
    <InputText
      placeholder="Busque por cargo, empresa ou tecnologia"
      value={query}
      onChange={onQueryChange}
      startIcon={Search}
      containerClassName="max-w-none"
      className="h-11 rounded-xl bg-surface"
    />
  );
}
