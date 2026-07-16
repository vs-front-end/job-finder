import { z } from 'zod';

import {
  jobListSchema,
  platformSchema,
  preferencesSchema,
  runStatusSchema,
  sourceHealthSchema,
  type Eligibility,
  type PlatformTrackingStatus,
  type Preferences,
} from './schema';

export type EventType =
  | 'saved'
  | 'dismissed'
  | 'applied_manual'
  | 'interview_hr'
  | 'code_test'
  | 'interview_technical'
  | 'offer'
  | 'rejected'
  | 'withdrawn'
  | 'closed_without_application';

async function request(path: string, init?: RequestInit): Promise<unknown> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null);
    const detail = z.object({ detail: z.string() }).safeParse(payload);
    throw new Error(detail.success ? detail.data.detail : 'The request could not be completed');
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  async jobs(tab: string, query: string) {
    const params = new URLSearchParams({ tab, q: query, limit: '100' });
    return jobListSchema.parse(await request(`/api/jobs?${params}`));
  },
  async addEvent(jobId: number, event: EventType, notes = '') {
    await request(`/api/jobs/${jobId}/events`, {
      method: 'POST',
      body: JSON.stringify({ event, notes }),
    });
  },
  async correctEligibility(jobId: number, eligibility: Eligibility, reason: string) {
    await request(`/api/jobs/${jobId}/eligibility`, {
      method: 'PATCH',
      body: JSON.stringify({ eligibility, reason }),
    });
  },
  async importUrl(url: string) {
    await request('/api/jobs/import', { method: 'POST', body: JSON.stringify({ url }) });
  },
  async verifyJob(jobId: number) {
    const schema = z.object({ open: z.boolean() });
    return schema.parse(await request(`/api/jobs/${jobId}/verify`, { method: 'POST' }));
  },
  async runNow() {
    await request('/api/runs', { method: 'POST' });
  },
  async runStatus() {
    return runStatusSchema.parse(await request('/api/runs/status'));
  },
  async sources() {
    return z.array(sourceHealthSchema).parse(await request('/api/sources'));
  },
  async platforms() {
    return z.array(platformSchema).parse(await request('/api/platforms'));
  },
  async preferences() {
    return preferencesSchema.parse(await request('/api/preferences'));
  },
  async updatePreferences(preferences: Preferences) {
    return preferencesSchema.parse(
      await request('/api/preferences', { method: 'PUT', body: JSON.stringify(preferences) }),
    );
  },
  async updatePlatform(id: string, trackingStatus: PlatformTrackingStatus, notes: string) {
    return platformSchema.parse(
      await request(`/api/platforms/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ tracking_status: trackingStatus, notes }),
      }),
    );
  },
};
