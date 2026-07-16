import { formatDistanceToNowStrict } from 'date-fns';

import {
  Badge,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  ScrollArea,
  Text,
} from '@stellar-ui-kit/web';

import type { SourceHealth } from '@/api/schema';

type SourceHealthDialogProps = {
  open: boolean;
  loading: boolean;
  sources: SourceHealth[];
  onOpenChange: (open: boolean) => void;
};

const statusLabels: Record<string, string> = {
  success: 'Success',
  error: 'Error',
  running: 'Running',
  partial: 'Partial',
};

function statusVariant(status: string): 'success' | 'destructive' | 'warning' | 'outline' {
  if (status === 'success') return 'success';
  if (status === 'error') return 'destructive';
  if (status === 'running') return 'outline';
  return 'warning';
}

export function SourceHealthDialog({
  open,
  loading,
  sources,
  onOpenChange,
}: SourceHealthDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Source health</DialogTitle>
          <DialogDescription>Latest recorded result for each collector.</DialogDescription>
        </DialogHeader>
        <ScrollArea className="max-h-[65vh] pr-3">
          <div className="space-y-2">
            {loading && (
              <Text as="p" styleVariant="muted">
                Loading sources…
              </Text>
            )}
            {!loading && sources.length === 0 && (
              <Text as="p" styleVariant="muted">
                No source has run yet.
              </Text>
            )}
            {sources.map((source) => (
              <div key={source.source} className="rounded-xl border border-border bg-background p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <Text as="p" className="text-sm font-semibold">
                      {source.source}
                    </Text>
                    <Text as="p" styleVariant="muted" className="mt-0.5 text-xs">
                      {formatDistanceToNowStrict(new Date(source.started_at), {
                        addSuffix: true,
                      })}
                    </Text>
                  </div>
                  <Badge variant={statusVariant(source.status)}>
                    {statusLabels[source.status] ?? source.status}
                  </Badge>
                </div>
                <dl className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
                  <SourceStat label="Fetched" value={source.fetched} />
                  <SourceStat label="New" value={source.inserted} />
                  <SourceStat label="Duplicates" value={source.duplicates} />
                  <SourceStat label="Errors" value={source.errors} />
                </dl>
                {source.error_message && (
                  <Text as="p" className="mt-3 text-xs text-error-text">
                    {source.error_message}
                  </Text>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}

type SourceStatProps = {
  label: string;
  value: number;
};

function SourceStat({ label, value }: SourceStatProps) {
  return (
    <div className="rounded-lg bg-surface px-3 py-2">
      <dt className="font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted">
        {label}
      </dt>
      <dd className="m-0 font-mono text-sm font-semibold">{value}</dd>
    </div>
  );
}
