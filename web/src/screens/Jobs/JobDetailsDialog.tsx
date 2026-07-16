import { useState } from 'react';

import { cn } from '@stellar-ui-kit/shared';
import {
  Badge,
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Separator,
  Text,
  TextArea,
} from '@stellar-ui-kit/web';

import { ArrowUpRight, RefreshCw } from 'lucide-react';

import type { EventType } from '@/api/client';
import type { Eligibility, Job } from '@/api/schema';
import { InitialsAvatar } from '@/components';

import { EligibilityNotice } from './EligibilityNotice';
import { JobFacts } from './JobFacts';
import { RichDescription } from './RichDescription';
import { workflowLabels } from './format';

type JobDetailsDialogProps = {
  job: Job | null;
  busy: boolean;
  onOpenChange: (open: boolean) => void;
  onEvent: (jobId: number, event: EventType, notes?: string) => void;
  onEligibility: (jobId: number, value: Eligibility) => void;
  onVerify: (jobId: number) => void;
};

const stages: { value: EventType; label: string }[] = [
  { value: 'applied_manual', label: 'Candidatei' },
  { value: 'interview_hr', label: 'Entrevista RH' },
  { value: 'code_test', label: 'Teste técnico' },
  { value: 'interview_technical', label: 'Entrevista técnica' },
  { value: 'offer', label: 'Oferta' },
  { value: 'rejected', label: 'Rejeitada' },
  { value: 'withdrawn', label: 'Desisti' },
];

const eligibilityOptions: { value: Eligibility; label: string }[] = [
  { value: 'compatible', label: 'Compatível' },
  { value: 'uncertain', label: 'Incerta' },
  { value: 'incompatible', label: 'Incompatível' },
];

export function JobDetailsDialog({
  job,
  busy,
  onOpenChange,
  onEvent,
  onEligibility,
  onVerify,
}: JobDetailsDialogProps) {
  const [notes, setNotes] = useState('');

  const handleOpenChange = (open: boolean) => {
    if (!open) setNotes('');
    onOpenChange(open);
  };

  return (
    <Dialog open={job !== null} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[92vh] overflow-y-auto sm:max-w-3xl">
        {job && (
          <>
            <DialogHeader className="space-y-3 text-left">
              <div className="flex items-start gap-3 pr-8">
                <InitialsAvatar name={job.company} size="lg" />
                <div className="min-w-0 flex-1">
                  <DialogTitle className="text-base font-semibold leading-snug">
                    {job.title}
                  </DialogTitle>
                  <DialogDescription className="mt-1 text-sm font-medium text-foreground">
                    {job.company}
                  </DialogDescription>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5">
                <Badge>{workflowLabels[job.workflow_status]}</Badge>
                {job.remote_scope && <Badge variant="success">{job.remote_scope}</Badge>}
                {job.employment_type && <Badge variant="outline">{job.employment_type}</Badge>}
                {job.relevant_technologies.map((technology) => (
                  <Badge key={technology} variant="secondary">
                    {technology}
                  </Badge>
                ))}
              </div>
            </DialogHeader>

            <EligibilityNotice job={job} busy={busy} onEligibility={onEligibility} />
            <JobFacts job={job} className="sm:grid-cols-2" />

            <div className="space-y-2">
              <Text as="h3" className="text-sm font-semibold">
                Sobre a vaga
              </Text>
              <RichDescription
                html={job.description_html}
                text={job.description}
                className="max-h-[32vh] overflow-y-auto pr-3"
              />
            </div>

            <Separator />

            <div className="space-y-3">
              <div>
                <Text as="h3" className="text-sm font-semibold">
                  Acompanhar processo
                </Text>
                <Text as="p" styleVariant="muted" className="mt-0.5 text-sm">
                  Registre a próxima etapa sem perder o histórico.
                </Text>
              </div>
              <TextArea
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                placeholder="Nota opcional"
                containerClassName="max-w-none"
              />
              <div className="flex flex-wrap gap-2">
                {stages.map((stage) => (
                  <Button
                    key={stage.value}
                    variant="outline"
                    size="sm"
                    disabled={busy}
                    onClick={() => onEvent(job.id, stage.value, notes)}
                  >
                    {stage.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="grid gap-6 border-t border-border pt-5 md:grid-cols-2">
              <div className="space-y-2">
                <Text as="h3" className="text-sm font-semibold">
                  Fontes
                </Text>
                <div className="flex flex-wrap gap-2">
                  {job.sources.map((source) => (
                    <Button
                      key={`${source.source}-${source.source_url}`}
                      variant="outline"
                      size="sm"
                      asChild
                    >
                      <a href={source.source_url} target="_blank" rel="noreferrer">
                        {source.source} <ArrowUpRight />
                      </a>
                    </Button>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <Text as="h3" className="text-sm font-semibold">
                  Classificação
                </Text>
                <div className="flex flex-wrap gap-2">
                  {eligibilityOptions.map((option) => (
                    <Button
                      key={option.value}
                      variant={job.eligibility === option.value ? 'secondary' : 'ghost'}
                      size="sm"
                      disabled={busy}
                      className={cn(job.eligibility === option.value && 'pointer-events-none')}
                      onClick={() => onEligibility(job.id, option.value)}
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="ghost" disabled={busy} onClick={() => onVerify(job.id)}>
                <RefreshCw /> Revalidar link
              </Button>
              <Button asChild>
                <a href={job.apply_url} target="_blank" rel="noreferrer">
                  Abrir candidatura <ArrowUpRight />
                </a>
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
