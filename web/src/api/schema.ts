import { z } from 'zod';

const eligibilitySchema = z.enum([
  'compatible',
  'uncertain',
  'incompatible',
  'pending',
  'error',
]);

const workflowSchema = z.enum([
  'new',
  'saved',
  'dismissed',
  'applied',
  'interview_hr',
  'code_test',
  'interview_technical',
  'offer',
  'rejected',
  'withdrawn',
  'closed',
]);

const jobSourceSchema = z.object({
  source: z.string(),
  source_job_id: z.string().nullable(),
  source_url: z.string(),
  first_seen_at: z.string(),
  last_seen_at: z.string(),
});

export const jobSchema = z.object({
  id: z.number(),
  canonical_url: z.string(),
  apply_url: z.string(),
  ats: z.string().nullable(),
  ats_board: z.string().nullable(),
  ats_job_id: z.string().nullable(),
  title: z.string(),
  company: z.string(),
  description: z.string(),
  description_html: z
    .string()
    .nullish()
    .transform((value) => value ?? null),
  location_text: z.string(),
  remote_scope: z.string().nullable(),
  geo_json: z.record(z.string(), z.unknown()),
  employment_type: z.string().nullable(),
  salary_min: z.number().nullable(),
  salary_max: z.number().nullable(),
  salary_currency: z.string().nullable(),
  salary_period: z.string().nullable(),
  date_posted: z.string().nullable(),
  valid_through: z.string().nullable(),
  eligibility: eligibilitySchema,
  eligibility_reason: z.string(),
  geo_evidence: z.string().nullable(),
  workflow_status: workflowSchema,
  relevant_technologies: z.array(z.string()),
  first_seen_at: z.string(),
  last_seen_at: z.string(),
  last_verified_at: z.string().nullable(),
  closed_at: z.string().nullable(),
  sources: z.array(jobSourceSchema),
});

export const jobListSchema = z.object({
  items: z.array(jobSchema),
  total: z.number(),
  counts: z.record(z.string(), z.number()),
});

export const sourceHealthSchema = z.object({
  source: z.string(),
  started_at: z.string(),
  finished_at: z.string().nullable(),
  status: z.string(),
  fetched: z.number(),
  inserted: z.number(),
  updated: z.number(),
  duplicates: z.number(),
  errors: z.number(),
  error_message: z.string().nullable(),
});

export const runStatusSchema = z.object({ running: z.boolean() });

export const platformAvailabilitySchema = z.enum([
  'active',
  'needs_key',
  'manual',
  'planned',
]);

export const platformTrackingStatusSchema = z.enum([
  'pending',
  'done',
  'review_due',
  'skipped',
]);

export const platformSchema = z.object({
  id: z.string(),
  name: z.string(),
  url: z.string(),
  category: z.string(),
  availability: platformAvailabilitySchema,
  description: z.string(),
  tracking_status: platformTrackingStatusSchema,
  last_reviewed_at: z.string().nullable(),
  notes: z.string(),
});

export const preferencesSchema = z.object({
  profile_summary: z.string(),
  residence_country: z.string(),
  accepted_timezones: z.array(z.string()),
  accepted_titles: z.array(z.string()),
  rejected_titles: z.array(z.string()),
  technologies: z.array(z.string()),
  require_technology_match: z.boolean(),
  rejected_keywords: z.array(z.string()),
  accepted_languages: z.array(z.string()),
  rejected_currencies: z.array(z.string()),
  max_age_days: z.number(),
  search_terms: z.array(z.string()),
});

export type Job = z.infer<typeof jobSchema>;
export type Preferences = z.infer<typeof preferencesSchema>;
export type JobList = z.infer<typeof jobListSchema>;
export type SourceHealth = z.infer<typeof sourceHealthSchema>;
export type Eligibility = z.infer<typeof eligibilitySchema>;
export type Platform = z.infer<typeof platformSchema>;
export type PlatformTrackingStatus = z.infer<typeof platformTrackingStatusSchema>;
