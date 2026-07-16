import { format, formatDistanceToNowStrict } from 'date-fns';

import type { Job } from '@/api/schema';

export const workflowLabels: Record<Job['workflow_status'], string> = {
  new: 'New',
  saved: 'Saved',
  dismissed: 'Dismissed',
  applied: 'Applied',
  interview_hr: 'HR interview',
  code_test: 'Code test',
  interview_technical: 'Technical interview',
  offer: 'Offer',
  rejected: 'Rejected',
  withdrawn: 'Withdrawn',
  closed: 'Closed',
};

export function formatSalary(job: Job): string | null {
  if (job.salary_min === null && job.salary_max === null) return null;
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: job.salary_currency ?? 'USD',
    maximumFractionDigits: 0,
  });
  const min = job.salary_min === null ? null : formatter.format(job.salary_min);
  const max = job.salary_max === null ? null : formatter.format(job.salary_max);
  if (min && max) return `${min} – ${max}`;
  return min ?? max;
}

export function formatAge(job: Job): string {
  return formatDistanceToNowStrict(new Date(job.date_posted ?? job.first_seen_at), {
    addSuffix: true,
  });
}

export function formatPostedDate(job: Job): string {
  return format(new Date(job.date_posted ?? job.first_seen_at), 'MMMM d');
}
