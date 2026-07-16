import { cn } from '@stellar-ui-kit/shared';
import { Text } from '@stellar-ui-kit/web';

import { MapPin } from 'lucide-react';

import type { Job } from '@/api/schema';
import { InitialsAvatar } from '@/components';

import { formatAge, formatSalary } from './format';

type JobRowProps = {
  job: Job;
  active: boolean;
  onSelect: (job: Job) => void;
};

export function JobRow({ job, active, onSelect }: JobRowProps) {
  const salary = formatSalary(job);

  return (
    <div
      className={cn(
        'flex overflow-hidden rounded-xl border bg-surface transition-colors',
        active
          ? 'border-primary'
          : 'border-border hover:border-secondary hover:bg-primary-soft',
      )}
    >
      <button
        type="button"
        className="grid min-w-0 flex-1 grid-cols-[auto_minmax(0,1fr)] items-center gap-3 px-4 py-3.5 text-left md:grid-cols-[auto_minmax(0,1.4fr)_minmax(130px,0.8fr)_minmax(140px,0.65fr)] md:gap-4"
        onClick={() => onSelect(job)}
      >
        <InitialsAvatar name={job.company} className="size-11 rounded-xl" />
        <div className="min-w-0">
          <Text
            as="p"
            className={cn(
              'truncate text-sm font-semibold leading-snug',
              active && 'text-primary-text',
            )}
          >
            {job.title}
          </Text>
          <Text as="p" styleVariant="muted" className="mt-1 truncate text-xs">
            {job.company}
          </Text>
        </div>
        <div className="col-start-2 flex w-full min-w-0 items-center justify-self-start gap-1.5 text-muted md:col-start-auto">
          <MapPin className="size-3.5 shrink-0" />
          <Text as="p" styleVariant="muted" className="truncate text-xs">
            {job.location_text || job.remote_scope || 'Remoto'}
          </Text>
        </div>
        <div className="col-start-2 flex items-center justify-between gap-3 md:col-start-auto md:block md:text-right">
          <Text as="p" className="truncate text-xs font-semibold">
            {salary ?? 'Salário não informado'}
          </Text>
          <Text as="span" styleVariant="muted" className="mt-1 whitespace-nowrap text-[11px]">
            {formatAge(job)}
          </Text>
        </div>
      </button>

    </div>
  );
}
