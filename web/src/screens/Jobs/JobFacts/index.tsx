import { cn } from '@stellar-ui-kit/shared';

import { BriefcaseBusiness, CalendarDays, MapPin, Wallet, type LucideIcon } from 'lucide-react';

import type { Job } from '@/api/schema';

import { formatPostedDate, formatSalary } from '../format';

type JobFactsProps = {
  job: Job;
  className?: string;
};

export function JobFacts({ job, className }: JobFactsProps) {
  const facts: { icon: LucideIcon; label: string; value: string }[] = [
    { icon: MapPin, label: 'Location', value: job.location_text || job.remote_scope || 'Remote' },
    { icon: Wallet, label: 'Compensation', value: formatSalary(job) ?? 'Not disclosed' },
    { icon: CalendarDays, label: 'Posted', value: formatPostedDate(job) },
  ];
  if (job.employment_type) {
    facts.push({ icon: BriefcaseBusiness, label: 'Contract', value: job.employment_type });
  }

  return (
    <dl className={cn('grid grid-cols-2 gap-2', className)}>
      {facts.map((fact) => {
        const Icon = fact.icon;
        return (
          <div
            key={fact.label}
            className="flex min-w-0 items-center gap-2.5 px-3 py-2.5 border border-dashed border-border rounded-lg"
          >
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-secondary-soft text-muted">
              <Icon className="size-4" />
            </div>
            <div className="min-w-0">
              <dt className="text-[10px] font-semibold uppercase tracking-[0.1em] text-muted">
                {fact.label}
              </dt>
              <dd className="m-0 text-sm font-medium">{fact.value}</dd>
            </div>
          </div>
        );
      })}
    </dl>
  );
}
