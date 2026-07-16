import { InputText } from '@stellar-ui-kit/web';

import { Search } from 'lucide-react';

type JobsToolbarProps = {
  query: string;
  onQueryChange: (value: string) => void;
};

export function JobsToolbar({ query, onQueryChange }: JobsToolbarProps) {
  return (
    <InputText
      placeholder="Search by role, company or technology"
      value={query}
      onChange={onQueryChange}
      startIcon={Search}
      containerClassName="max-w-none"
      className="h-11 rounded-xl bg-surface"
    />
  );
}
