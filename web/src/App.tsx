import { useState } from 'react';

import { toast } from 'sonner';

import { cn } from '@stellar-ui-kit/shared';
import { Button } from '@stellar-ui-kit/web';

import { Activity, Link2, Play } from 'lucide-react';

import { useImportJob, useRunNow, useRunStatus, useSources } from '@/api/hooks';
import { AddJobDialog, Brand, SourceHealthDialog } from '@/components';
import { JobsScreen } from '@/screens/Jobs';
import { PlatformsScreen } from '@/screens/Platforms';

type View = 'jobs' | 'platforms';

export function App() {
  const [view, setView] = useState<View>('jobs');
  const [addOpen, setAddOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const importer = useImportJob();
  const runner = useRunNow();
  const runStatus = useRunStatus();
  const sources = useSources(sourcesOpen);
  const running = runStatus.data?.running ?? false;

  const handleImport = (url: string) => {
    importer.mutate(url, {
      onSuccess: () => {
        toast.success('Vaga adicionada ao radar');
        setAddOpen(false);
      },
      onError: (error) => toast.error(error.message),
    });
  };

  const handleRun = () => {
    runner.mutate(undefined, {
      onSuccess: () => toast.success('Coleta iniciada'),
      onError: (error) => toast.error(error.message),
    });
  };

  return (
    <div className="h-screen overflow-hidden bg-background p-0 shadow-none drop-shadow-none lg:p-5">
      <div className="paper-elevation mx-auto flex h-full max-w-[1540px] flex-col overflow-hidden bg-surface lg:rounded-3xl lg:border lg:border-border">
        <header className="relative z-30 shrink-0 border-b border-border bg-surface">
          {running && (
            <div className="absolute inset-x-0 bottom-0 h-px overflow-hidden">
              <div className="animate-scan h-full w-1/4 bg-primary" />
            </div>
          )}
          <div className="flex h-16 items-center gap-3 px-4 md:gap-6 md:px-6">
            <Brand />
            <nav className="ml-2 hidden items-center gap-1 sm:flex">
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  'rounded-lg px-3',
                  view === 'jobs' && 'bg-primary-soft font-semibold text-primary-text',
                )}
                onClick={() => setView('jobs')}
              >
                Vagas
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  'rounded-lg px-3',
                  view === 'platforms' && 'bg-primary-soft font-semibold text-primary-text',
                )}
                onClick={() => setView('platforms')}
              >
                Plataformas
              </Button>
            </nav>
            <div className="ml-auto flex items-center gap-1.5 md:gap-2">
              <Button variant="ghost" size="sm" onClick={() => setSourcesOpen(true)}>
                <Activity /> <span className="hidden lg:inline">Fontes</span>
              </Button>
              <Button variant="outline" size="sm" onClick={() => setAddOpen(true)}>
                <Link2 /> <span className="hidden lg:inline">Adicionar URL</span>
              </Button>
              <Button size="sm" disabled={runner.isPending || running} onClick={handleRun}>
                <Play className={running ? 'animate-pulse' : undefined} />
                <span className="hidden sm:inline">{running ? 'Coletando…' : 'Rodar agora'}</span>
              </Button>
            </div>
          </div>
        </header>

        <div
          className={cn(
            'min-h-0 flex-1',
            view === 'jobs' ? 'overflow-hidden' : 'overflow-y-auto',
          )}
        >
          {view === 'jobs' ? <JobsScreen running={running} onRun={handleRun} /> : <PlatformsScreen />}
        </div>
      </div>

      <AddJobDialog
        open={addOpen}
        busy={importer.isPending}
        error={importer.error?.message ?? null}
        onOpenChange={setAddOpen}
        onSubmit={handleImport}
      />
      <SourceHealthDialog
        open={sourcesOpen}
        loading={sources.isLoading}
        sources={sources.data ?? []}
        onOpenChange={setSourcesOpen}
      />
    </div>
  );
}
