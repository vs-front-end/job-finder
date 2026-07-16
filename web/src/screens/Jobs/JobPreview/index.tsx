import { Badge, Button, Text } from '@stellar-ui-kit/web';

import { ArrowUpRight, Bookmark, Check, MousePointerClick, Settings2, X } from 'lucide-react';

import type { EventType } from '@/api/client';
import type { Eligibility, Job } from '@/api/schema';
import { InitialsAvatar } from '@/components';

import { EligibilityNotice } from '../EligibilityNotice';
import { JobFacts } from '../JobFacts';
import { RichDescription } from '../RichDescription';
import { workflowLabels } from '../format';

type JobPreviewProps = {
  job: Job | null;
  busy: boolean;
  onAction: (jobId: number, event: EventType) => void;
  onEligibility: (jobId: number, value: Eligibility) => void;
  onDetails: (job: Job) => void;
};

export function JobPreview({ job, busy, onAction, onEligibility, onDetails }: JobPreviewProps) {
  if (!job) {
    return (
      <div className="flex h-full min-h-0 flex-col items-center justify-center gap-3 px-8 text-center">
        <div className="flex size-11 items-center justify-center rounded-xl bg-secondary-soft text-muted">
          <MousePointerClick className="size-5" />
        </div>
        <Text as="p" styleVariant="muted" className="text-sm">
          Select a job from the list to see its details here.
        </Text>
      </div>
    );
  }

  const isNew = job.workflow_status === 'new';

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-surface">
      <div className="space-y-3 border-b border-border px-5 py-4">
        <div className="flex items-center gap-3">
          <InitialsAvatar name={job.company} />
          <div className="min-w-0 flex-1">
            <Text as="p" className="truncate text-sm font-bold">
              {job.company}
            </Text>
            <Text as="p" styleVariant="muted" className="mt-1 truncate text-xs">
              {job.sources[0]?.source ?? 'Remote opportunity'}
            </Text>
          </div>
          {isNew && (
            <div className="flex shrink-0 overflow-hidden rounded-lg border border-border bg-secondary-soft">
              <Button
                variant="ghost"
                size="icon-sm"
                className="h-8 w-10 rounded-none border-r border-border hover:bg-primary-soft hover:text-primary-text"
                title="Save"
                aria-label="Save job"
                disabled={busy}
                onClick={() => onAction(job.id, 'saved')}
              >
                <Bookmark />
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                className="h-8 w-10 rounded-none border-r border-border hover:bg-primary-soft hover:text-primary-text"
                title="Process"
                aria-label="Open process"
                onClick={() => onDetails(job)}
              >
                <Settings2 />
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                className="h-8 w-10 rounded-none hover:bg-error-soft hover:text-error-text"
                title="Dismiss"
                aria-label="Dismiss job"
                disabled={busy}
                onClick={() => onAction(job.id, 'dismissed')}
              >
                <X />
              </Button>
            </div>
          )}
        </div>
        <div>
          <Text as="h3" className="text-sm font-semibold leading-snug">
            {job.title}
          </Text>
        </div>
        <div className="flex flex-wrap justify-start gap-1.5">
          {!isNew && <Badge>{workflowLabels[job.workflow_status]}</Badge>}
          <Badge variant="outline">{job.location_text || job.remote_scope || 'Remote'}</Badge>
          {job.relevant_technologies.map((technology) => (
            <Badge key={technology} variant="outline">
              {technology}
            </Badge>
          ))}
        </div>
      </div>

      <div className="min-h-0 flex-1 space-y-6 overflow-y-auto px-6 py-5">
        <EligibilityNotice job={job} busy={busy} onEligibility={onEligibility} />
        <JobFacts job={job} />
        <div className="space-y-2">
          <Text as="h4" className="text-sm font-semibold">
            Description
          </Text>
          <RichDescription html={job.description_html} text={job.description} />
        </div>
        {job.sources.length > 0 && (
          <Text as="p" styleVariant="muted" className="text-xs">
            Source: {job.sources.map((source) => source.source).join(', ')}
          </Text>
        )}
      </div>

      <div className="border-t border-border px-5 py-2.5">
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" asChild>
            <a href={job.apply_url} target="_blank" rel="noreferrer">
              Open job <ArrowUpRight />
            </a>
          </Button>
          {isNew ? (
            <Button disabled={busy} onClick={() => onAction(job.id, 'applied_manual')}>
              <Check /> Applied
            </Button>
          ) : (
            <Button variant="secondary" onClick={() => onDetails(job)}>
              <Settings2 /> Process
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
