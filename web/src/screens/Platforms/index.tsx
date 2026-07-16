import { useState } from 'react';

import { toast } from 'sonner';

import {
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

import { RadioTower } from 'lucide-react';

import type { Platform, PlatformTrackingStatus } from '@/api/schema';
import { usePlatforms, usePlatformUpdate } from '@/api/hooks';

import { PlatformCard } from './PlatformCard';

type PlatformFilter = 'all' | 'automatic' | 'manual' | 'planned';

const filters: { value: PlatformFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'automatic', label: 'Automatic' },
  { value: 'manual', label: 'Manual' },
  { value: 'planned', label: 'Planned' },
];

const skeletonKeys = ['one', 'two', 'three', 'four', 'five', 'six'];

export function PlatformsScreen() {
  const [filter, setFilter] = useState<PlatformFilter>('all');
  const query = usePlatforms(true);
  const update = usePlatformUpdate();
  const platforms = query.data ?? [];
  const visible = platforms.filter((platform) => matchesFilter(platform, filter));
  const automatic = platforms.filter((platform) => platform.availability === 'active').length;
  const manualPending = platforms.filter(
    (platform) => platform.availability === 'manual' && platform.tracking_status === 'pending',
  ).length;

  const handleUpdate = (platform: Platform, trackingStatus: PlatformTrackingStatus) => {
    update.mutate(
      { id: platform.id, trackingStatus, notes: platform.notes },
      {
        onSuccess: () => toast.success('Checklist updated'),
        onError: (error) => toast.error(error.message),
      },
    );
  };

  return (
    <main className="mx-auto max-w-[1600px] space-y-6 px-4 py-6 md:px-6">
      <section className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <Text as="h2" className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            Platforms & profiles
          </Text>
          <Text as="p" styleVariant="muted" className="mt-1 max-w-2xl text-sm">
            Automatic collectors, talent networks and manual searches in one place.
          </Text>
        </div>
        <Text as="p" styleVariant="muted" className="font-mono text-xs">
          {automatic} automatic · {manualPending} manual pending · {platforms.length} cataloged
        </Text>
      </section>

      <Tabs value={filter} onValueChange={(value) => isPlatformFilter(value) && setFilter(value)}>
        <TabsList>
          {filters.map((item) => (
            <TabsTrigger key={item.value} value={item.value}>
              {item.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {query.isLoading && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {skeletonKeys.map((key) => (
            <Skeleton key={key} className="h-56 rounded-xl" />
          ))}
        </div>
      )}

      {query.isError && (
        <Empty className="border-border-strong">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <RadioTower />
            </EmptyMedia>
            <EmptyTitle>Could not load platforms</EmptyTitle>
            <EmptyDescription>{query.error.message}</EmptyDescription>
          </EmptyHeader>
        </Empty>
      )}

      {query.data && (
        <div className="grid items-start gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {visible.map((platform) => (
            <PlatformCard
              key={platform.id}
              platform={platform}
              busy={update.isPending && update.variables.id === platform.id}
              onUpdate={handleUpdate}
            />
          ))}
        </div>
      )}
    </main>
  );
}

function matchesFilter(platform: Platform, filter: PlatformFilter) {
  if (filter === 'all') return true;
  if (filter === 'automatic') {
    return platform.availability === 'active' || platform.availability === 'needs_key';
  }
  return platform.availability === filter;
}

function isPlatformFilter(value: string): value is PlatformFilter {
  return filters.some((filter) => filter.value === value);
}
