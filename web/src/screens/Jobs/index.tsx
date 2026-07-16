import { useDeferredValue, useState } from 'react';

import { toast } from 'sonner';

import { cn } from '@stellar-ui-kit/shared';
import {
  Badge,
  Button,
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
  Skeleton,
  Tabs,
  TabsList,
  TabsTrigger,
  Text,
} from '@stellar-ui-kit/web';

import { Play, RadioTower, Sparkles } from 'lucide-react';

import type { EventType } from '@/api/client';
import type { Eligibility, Job } from '@/api/schema';
import { useJobActions, useJobs } from '@/api/hooks';

import { JobDetailsDialog } from './JobDetailsDialog';
import { JobPreview } from './JobPreview';
import { JobRow } from './JobRow';
import { JobsToolbar } from './JobsToolbar';
import { queueItems, type QueueTab } from './queue';
import { QueueSidebar } from './QueueSidebar';

const actionToasts: Partial<Record<EventType, string>> = {
  saved: 'Vaga salva',
  dismissed: 'Vaga descartada',
  applied_manual: 'Candidatura registrada',
};

const emptyCopy: Record<QueueTab, string> = {
  new: 'Rode as fontes para buscar novas oportunidades.',
  uncertain: 'Nenhuma vaga aguardando revisão de região.',
  saved: 'Vagas salvas aparecem aqui para você decidir depois.',
  applied: 'Registre uma candidatura para acompanhá-la aqui.',
  in_process: 'Quando uma candidatura avançar de etapa, ela aparece aqui.',
  closed: 'Nenhuma vaga encerrada por enquanto.',
  dismissed: 'Nenhuma vaga descartada.',
  all: 'Rode as fontes para começar a preencher o radar.',
};

const skeletonKeys = ['one', 'two', 'three', 'four', 'five', 'six'];

type JobsScreenProps = {
  running: boolean;
  onRun: () => void;
};

export function JobsScreen({ running, onRun }: JobsScreenProps) {
  const [tab, setTab] = useState<QueueTab>('new');
  const [query, setQuery] = useState('');
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [dialogJob, setDialogJob] = useState<Job | null>(null);
  const deferredQuery = useDeferredValue(query);
  const jobs = useJobs(tab, deferredQuery);
  const actions = useJobActions();
  const busy =
    actions.event.isPending || actions.eligibility.isPending || actions.verify.isPending;

  const counts = jobs.data?.counts ?? {};
  const visibleJobs = jobs.data?.items ?? [];
  const activeJob = visibleJobs.find((job) => job.id === selectedJobId) ?? visibleJobs[0] ?? null;
  const hasSearch = query !== '';
  const activeQueue = queueItems.find((item) => item.value === tab);

  const countFor = (value: QueueTab) => {
    if (value === 'all') return jobs.data?.total ?? 0;
    if (value === 'new') return counts.new_compatible ?? 0;
    if (value === 'uncertain') return counts.new_uncertain ?? 0;
    if (value === 'closed') return counts.closed_total ?? 0;
    return counts[value] ?? 0;
  };

  const handleSelect = (job: Job) => {
    setSelectedJobId(job.id);
    if (!window.matchMedia('(min-width: 1280px)').matches) setDialogJob(job);
  };

  const handleAction = (jobId: number, event: EventType, notes?: string) => {
    actions.event.mutate(
      { jobId, type: event, notes },
      {
        onSuccess: () => {
          toast.success(actionToasts[event] ?? 'Etapa atualizada');
          setDialogJob(null);
        },
        onError: (error) => toast.error(error.message),
      },
    );
  };

  const handleEligibility = (jobId: number, value: Eligibility) => {
    actions.eligibility.mutate(
      { jobId, value, reason: 'Correção manual do usuário' },
      {
        onSuccess: () => toast.success('Elegibilidade corrigida'),
        onError: (error) => toast.error(error.message),
      },
    );
  };

  const handleVerify = (jobId: number) => {
    actions.verify.mutate(jobId, {
      onSuccess: (result) => toast.success(result.open ? 'Link ativo' : 'Vaga encerrada'),
      onError: (error) => toast.error(error.message),
    });
  };

  return (
    <main className="h-full min-h-0">
      <div className="grid h-full min-h-0 items-stretch lg:grid-cols-[190px_minmax(0,1fr)_330px] xl:grid-cols-[220px_minmax(0,1fr)_390px] 2xl:grid-cols-[240px_minmax(0,1fr)_430px]">
        <QueueSidebar tab={tab} countFor={countFor} onChange={setTab} />

        <section className="flex h-full min-h-0 min-w-0 flex-col overflow-hidden bg-background p-4 md:p-6 lg:border-x lg:border-border">
          <div className="mb-5 flex shrink-0 flex-wrap items-end justify-between gap-3">
            <div>
              <Text as="h2" className="font-display text-2xl font-bold tracking-tight md:text-3xl">
                Encontre sua próxima vaga
              </Text>
              <Text as="p" styleVariant="muted" className="mt-1 text-sm">
                Oportunidades remotas selecionadas para o seu perfil.
              </Text>
            </div>
            <div
              className={cn(
                'flex items-center gap-2 text-xs font-medium',
                running ? 'text-primary-text' : 'text-error-text',
              )}
            >
              <span
                className={cn(
                  'size-1.5 rounded-full',
                  running ? 'animate-pulse bg-primary' : 'bg-error',
                )}
              />
              {running ? 'Busca ativa' : 'Busca desligada'}
            </div>
          </div>

          <Tabs
            value={tab}
            onValueChange={(value) => {
              const item = queueItems.find((queue) => queue.value === value);
              if (item) setTab(item.value);
            }}
            className="mb-4 lg:hidden"
          >
            <div className="overflow-x-auto pb-1">
              <TabsList>
                {queueItems.map((item) => (
                  <TabsTrigger key={item.value} value={item.value}>
                    {item.label}
                    {countFor(item.value) > 0 && (
                      <Badge variant="outline">{countFor(item.value)}</Badge>
                    )}
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>
          </Tabs>

          <div className="shrink-0">
            <JobsToolbar query={query} onQueryChange={setQuery} />
          </div>

          <div className="flex h-11 shrink-0 items-center justify-between gap-3 px-1">
            <Text as="p" styleVariant="muted" className="text-xs font-medium">
              {activeQueue?.label} · {visibleJobs.length}{' '}
              {visibleJobs.length === 1 ? 'resultado' : 'resultados'}
            </Text>
            {hasSearch && (
              <Button variant="ghost" size="sm" onClick={() => setQuery('')}>
                Limpar busca
              </Button>
            )}
          </div>

          <div className="min-h-0 flex-1 space-y-2.5 overflow-y-auto p-1">
            {jobs.isLoading &&
              skeletonKeys.map((key) => (
                <div key={key} className="flex gap-3 rounded-xl border border-border bg-surface p-4">
                  <Skeleton className="size-10 rounded-xl" />
                  <div className="flex-1 space-y-2.5">
                    <Skeleton className="h-4 w-2/3" />
                    <Skeleton className="h-3 w-1/3" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))}

            {jobs.isError && (
              <Empty className="border-border-strong">
                <EmptyHeader>
                  <EmptyMedia variant="icon">
                    <RadioTower />
                  </EmptyMedia>
                  <EmptyTitle>Não foi possível falar com o radar</EmptyTitle>
                  <EmptyDescription>{jobs.error.message}</EmptyDescription>
                </EmptyHeader>
              </Empty>
            )}

            {jobs.data && visibleJobs.length === 0 && (
              <Empty className="border-border-strong">
                <EmptyHeader>
                  <EmptyMedia variant="icon">
                    <Sparkles />
                  </EmptyMedia>
                  <EmptyTitle>Nenhuma vaga nesta fila</EmptyTitle>
                  <EmptyDescription>
                    {hasSearch
                      ? 'Tente buscar por outro cargo, empresa ou tecnologia.'
                      : emptyCopy[tab]}
                  </EmptyDescription>
                </EmptyHeader>
                {hasSearch ? (
                  <Button variant="outline" onClick={() => setQuery('')}>
                    Limpar busca
                  </Button>
                ) : (
                  (tab === 'new' || tab === 'all') && (
                    <Button disabled={running} onClick={onRun}>
                      <Play /> Rodar fontes
                    </Button>
                  )
                )}
              </Empty>
            )}

            {visibleJobs.map((job) => (
              <JobRow
                key={job.id}
                job={job}
                active={activeJob?.id === job.id}
                onSelect={handleSelect}
              />
            ))}
          </div>
        </section>

        <div className="hidden h-full min-h-0 bg-surface lg:block">
          <JobPreview
            job={activeJob}
            busy={busy}
            onAction={handleAction}
            onEligibility={handleEligibility}
            onDetails={setDialogJob}
          />
        </div>
      </div>

      <JobDetailsDialog
        job={dialogJob}
        busy={busy}
        onOpenChange={(open) => !open && setDialogJob(null)}
        onEvent={handleAction}
        onEligibility={handleEligibility}
        onVerify={handleVerify}
      />
    </main>
  );
}
