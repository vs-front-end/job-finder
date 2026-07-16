import { Button, Text } from '@stellar-ui-kit/web';

import { CircleHelp } from 'lucide-react';

import type { Eligibility, Job } from '@/api/schema';

type EligibilityNoticeProps = {
  job: Job;
  busy: boolean;
  onEligibility: (jobId: number, value: Eligibility) => void;
};

export function EligibilityNotice({ job, busy, onEligibility }: EligibilityNoticeProps) {
  if (job.eligibility !== 'uncertain') return null;

  return (
    <div className="space-y-2 rounded-xl border border-border bg-secondary-soft p-4">
      <div className="flex items-center gap-2 text-sm font-semibold text-secondary-text">
        <CircleHelp className="size-4 shrink-0" /> Região incerta
      </div>
      <Text as="p" styleVariant="muted" className="text-sm leading-relaxed">
        {job.geo_evidence ||
          job.eligibility_reason ||
          'Não foi possível confirmar se a vaga aceita candidatos da sua região.'}
      </Text>
      <div className="flex flex-wrap gap-2 pt-1">
        <Button
          variant="outline"
          size="sm"
          disabled={busy}
          onClick={() => onEligibility(job.id, 'compatible')}
        >
          Aceita minha região
        </Button>
        <Button
          variant="ghost"
          size="sm"
          disabled={busy}
          onClick={() => onEligibility(job.id, 'incompatible')}
        >
          Não aceita
        </Button>
      </div>
    </div>
  );
}
