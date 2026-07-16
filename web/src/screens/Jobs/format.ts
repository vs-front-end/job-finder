import { format, formatDistanceToNowStrict } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import type { Job } from '@/api/schema';

export const workflowLabels: Record<Job['workflow_status'], string> = {
  new: 'Nova',
  saved: 'Salva',
  dismissed: 'Descartada',
  applied: 'Candidatei',
  interview_hr: 'Entrevista RH',
  code_test: 'Teste técnico',
  interview_technical: 'Entrevista técnica',
  offer: 'Oferta',
  rejected: 'Rejeitada',
  withdrawn: 'Desisti',
  closed: 'Encerrada',
};

export function formatSalary(job: Job): string | null {
  if (job.salary_min === null && job.salary_max === null) return null;
  const formatter = new Intl.NumberFormat('pt-BR', {
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
    locale: ptBR,
  });
}

export function formatPostedDate(job: Job): string {
  return format(new Date(job.date_posted ?? job.first_seen_at), "d 'de' MMMM", { locale: ptBR });
}
