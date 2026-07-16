import { useEffect, useRef } from 'react';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api, type EventType } from './client';
import type { Eligibility, PlatformTrackingStatus, Preferences } from './schema';

const keys = {
  jobs: (tab: string, query: string) => ['jobs', tab, query] as const,
  sources: ['sources'] as const,
  platforms: ['platforms'] as const,
  runStatus: ['run-status'] as const,
  preferences: ['preferences'] as const,
};

export function useJobs(tab: string, query: string, enabled = true) {
  return useQuery({
    queryKey: keys.jobs(tab, query),
    queryFn: () => api.jobs(tab, query),
    enabled,
    refetchInterval: 5_000,
  });
}

export function useSources(enabled: boolean) {
  return useQuery({ queryKey: keys.sources, queryFn: api.sources, enabled });
}

export function usePlatforms(enabled: boolean) {
  return useQuery({ queryKey: keys.platforms, queryFn: api.platforms, enabled });
}

export function usePlatformUpdate() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      trackingStatus,
      notes,
    }: {
      id: string;
      trackingStatus: PlatformTrackingStatus;
      notes: string;
    }) => api.updatePlatform(id, trackingStatus, notes),
    onSuccess: async () => client.invalidateQueries({ queryKey: keys.platforms }),
  });
}

export function useRunStatus() {
  const client = useQueryClient();
  const wasRunning = useRef(false);
  const status = useQuery({
    queryKey: keys.runStatus,
    queryFn: api.runStatus,
    refetchInterval: (query) => (query.state.data?.running ? 2_000 : 15_000),
  });
  const running = status.data?.running;

  useEffect(() => {
    const runFinished = wasRunning.current && running === false;
    wasRunning.current = running ?? false;
    if (!runFinished) return;

    async function refreshCollectedData() {
      await Promise.all([
        client.invalidateQueries({ queryKey: ['jobs'] }),
        client.invalidateQueries({ queryKey: keys.sources }),
      ]);
    }

    refreshCollectedData().catch(() => undefined);
  }, [client, running]);

  return status;
}

export function useJobActions() {
  const client = useQueryClient();
  const invalidate = async () => {
    await client.invalidateQueries({ queryKey: ['jobs'] });
  };
  const event = useMutation({
    mutationFn: ({ jobId, type, notes }: { jobId: number; type: EventType; notes?: string }) =>
      api.addEvent(jobId, type, notes),
    onSuccess: invalidate,
  });
  const eligibility = useMutation({
    mutationFn: ({ jobId, value, reason }: { jobId: number; value: Eligibility; reason: string }) =>
      api.correctEligibility(jobId, value, reason),
    onSuccess: invalidate,
  });
  const verify = useMutation({
    mutationFn: api.verifyJob,
    onSuccess: invalidate,
  });
  return { event, eligibility, verify };
}

export function useImportJob() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: api.importUrl,
    onSuccess: async () => client.invalidateQueries({ queryKey: ['jobs'] }),
  });
}

export function usePreferences() {
  return useQuery({ queryKey: keys.preferences, queryFn: api.preferences });
}

export function useUpdatePreferences() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (preferences: Preferences) => api.updatePreferences(preferences),
    onSuccess: async () => client.invalidateQueries({ queryKey: keys.preferences }),
  });
}

export function useRunNow() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: api.runNow,
    onSuccess: async () => client.invalidateQueries({ queryKey: keys.runStatus }),
  });
}
