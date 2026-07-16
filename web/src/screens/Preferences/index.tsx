import { useState } from 'react';

import { toast } from 'sonner';

import {
  Button,
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Separator,
  Skeleton,
  Switch,
  Text,
  TextArea,
} from '@stellar-ui-kit/web';

import { RadioTower, Save } from 'lucide-react';

import type { Preferences } from '@/api/schema';
import { usePreferences, useUpdatePreferences } from '@/api/hooks';

import { ChipListField } from './ChipListField';
import { PresetChips } from './PresetChips';
import { joinPresets, splitPresets, type TitleSelection } from './mapping';
import {
  countryOptions,
  currencySuggestions,
  exclusionPresets,
  languageOptions,
  maxAgeOptions,
  rolePresets,
  technologySuggestions,
  timezoneOptions,
} from './presets';

export function PreferencesScreen() {
  const query = usePreferences();

  if (query.isLoading) {
    return (
      <main className="mx-auto max-w-3xl space-y-4 px-4 py-8 md:px-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-40 rounded-xl" />
        <Skeleton className="h-40 rounded-xl" />
      </main>
    );
  }

  if (query.isError || !query.data) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8 md:px-6">
        <Empty className="border-border-strong">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <RadioTower />
            </EmptyMedia>
            <EmptyTitle>Could not load preferences</EmptyTitle>
            <EmptyDescription>{query.error?.message}</EmptyDescription>
          </EmptyHeader>
        </Empty>
      </main>
    );
  }

  return <PreferencesForm initial={query.data} />;
}

type FormState = {
  roles: TitleSelection;
  exclusions: TitleSelection;
  technologies: string[];
  requireTechnologyMatch: boolean;
  rejectedKeywords: string[];
  acceptedLanguages: string[];
  residenceCountry: string;
  acceptedTimezones: string[];
  rejectedCurrencies: string[];
  maxAgeDays: number;
  searchTerms: string[];
  profileSummary: string;
};

function buildFormState(preferences: Preferences): FormState {
  return {
    roles: splitPresets(preferences.accepted_titles, rolePresets),
    exclusions: splitPresets(preferences.rejected_titles, exclusionPresets),
    technologies: preferences.technologies,
    requireTechnologyMatch: preferences.require_technology_match,
    rejectedKeywords: preferences.rejected_keywords,
    acceptedLanguages: preferences.accepted_languages,
    residenceCountry: preferences.residence_country,
    acceptedTimezones: preferences.accepted_timezones,
    rejectedCurrencies: preferences.rejected_currencies,
    maxAgeDays: preferences.max_age_days,
    searchTerms: preferences.search_terms,
    profileSummary: preferences.profile_summary,
  };
}

function buildPreferences(state: FormState): Preferences {
  return {
    profile_summary: state.profileSummary,
    residence_country: state.residenceCountry,
    accepted_timezones: state.acceptedTimezones,
    accepted_titles: joinPresets(state.roles, rolePresets),
    rejected_titles: joinPresets(state.exclusions, exclusionPresets),
    technologies: state.technologies,
    require_technology_match: state.requireTechnologyMatch,
    rejected_keywords: state.rejectedKeywords,
    accepted_languages: state.acceptedLanguages,
    rejected_currencies: state.rejectedCurrencies,
    max_age_days: state.maxAgeDays,
    search_terms: state.searchTerms,
  };
}

function toggleValue(values: string[], value: string): string[] {
  return values.includes(value)
    ? values.filter((item) => item !== value)
    : [...values, value];
}

type PreferencesFormProps = {
  initial: Preferences;
};

function PreferencesForm({ initial }: PreferencesFormProps) {
  const [state, setState] = useState<FormState>(() => buildFormState(initial));
  const update = useUpdatePreferences();

  const patch = (changes: Partial<FormState>) =>
    setState((current) => ({ ...current, ...changes }));

  const toggleSelection = (field: 'roles' | 'exclusions', id: string) =>
    setState((current) => ({
      ...current,
      [field]: { ...current[field], selected: toggleValue(current[field].selected, id) },
    }));

  const handleSave = () => {
    update.mutate(buildPreferences(state), {
      onSuccess: (saved) => {
        setState(buildFormState(saved));
        toast.success('Preferences saved — they apply to the next scan');
      },
      onError: (error) => toast.error(error.message),
    });
  };

  return (
    <main className="mx-auto max-w-3xl space-y-8 px-4 py-8 md:px-6">
      <section className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <Text as="h2" className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            Preferences
          </Text>
          <Text as="p" styleVariant="muted" className="mt-1 max-w-2xl text-sm">
            Tune the deterministic filters that decide which jobs enter your radar.
          </Text>
        </div>
        <Button disabled={update.isPending} onClick={handleSave}>
          <Save /> {update.isPending ? 'Saving…' : 'Save preferences'}
        </Button>
      </section>

      <section className="space-y-6 rounded-xl border border-border bg-surface p-5">
        <PresetChips
          label="Roles you want"
          description="Job titles must match at least one selected role. Custom entries accept regular expressions."
          presets={rolePresets}
          selected={state.roles.selected}
          onToggle={(id) => toggleSelection('roles', id)}
        />
        <ChipListField
          label="Custom role patterns"
          values={state.roles.custom}
          placeholder="e.g. embedded.*engineer"
          onChange={(custom) => patch({ roles: { ...state.roles, custom } })}
        />
        <Separator />
        <PresetChips
          label="Titles to exclude"
          description="Jobs whose titles match any selected item are dropped."
          presets={exclusionPresets}
          selected={state.exclusions.selected}
          onToggle={(id) => toggleSelection('exclusions', id)}
        />
        <ChipListField
          label="Custom exclusion patterns"
          values={state.exclusions.custom}
          placeholder="e.g. \bweb3\b"
          onChange={(custom) => patch({ exclusions: { ...state.exclusions, custom } })}
        />
      </section>

      <section className="space-y-6 rounded-xl border border-border bg-surface p-5">
        <ChipListField
          label="Tech stack"
          description="Technologies highlighted on each job and used for stack matching."
          values={state.technologies}
          suggestions={technologySuggestions}
          onChange={(technologies) => patch({ technologies })}
        />
        <label className="flex items-center justify-between gap-4">
          <div>
            <Text as="p" className="text-sm font-semibold">
              Require a stack match
            </Text>
            <Text as="p" styleVariant="muted" className="mt-0.5 text-xs">
              Drop jobs that do not mention any of your technologies.
            </Text>
          </div>
          <Switch
            checked={state.requireTechnologyMatch}
            onCheckedChange={(requireTechnologyMatch) => patch({ requireTechnologyMatch })}
          />
        </label>
        <ChipListField
          label="Rejected keywords"
          description="Jobs mentioning any of these words are dropped. Regular expressions allowed."
          values={state.rejectedKeywords}
          placeholder="e.g. blockchain"
          onChange={(rejectedKeywords) => patch({ rejectedKeywords })}
        />
        <ChipListField
          label="Search terms"
          description="Terms sent to sources that support keyword search."
          values={state.searchTerms}
          placeholder="e.g. React"
          onChange={(searchTerms) => patch({ searchTerms })}
        />
      </section>

      <section className="space-y-6 rounded-xl border border-border bg-surface p-5">
        <div className="grid gap-5 sm:grid-cols-2">
          <div className="space-y-2">
            <Text as="p" className="text-sm font-semibold">
              Country of residence
            </Text>
            <Select
              value={state.residenceCountry}
              onValueChange={(residenceCountry) => patch({ residenceCountry })}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {countryOptions.map((option) => (
                  <SelectItem key={option.code} value={option.code}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Text as="p" className="text-sm font-semibold">
              Maximum job age
            </Text>
            <Select
              value={String(state.maxAgeDays)}
              onValueChange={(value) => patch({ maxAgeDays: Number(value) })}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {maxAgeOptions.map((days) => (
                  <SelectItem key={days} value={String(days)}>
                    {days === 1 ? '1 day' : `${days} days`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <PresetChips
          label="Accepted timezones"
          description="Used when a job restricts candidates by timezone instead of country."
          presets={timezoneOptions.map((timezone) => ({
            id: timezone,
            label: timezone,
            patterns: [],
          }))}
          selected={state.acceptedTimezones}
          onToggle={(timezone) =>
            patch({ acceptedTimezones: toggleValue(state.acceptedTimezones, timezone) })
          }
        />
        <PresetChips
          label="Accepted posting languages"
          presets={languageOptions.map((language) => ({
            id: language.code,
            label: language.label,
            patterns: [],
          }))}
          selected={state.acceptedLanguages}
          onToggle={(code) =>
            patch({ acceptedLanguages: toggleValue(state.acceptedLanguages, code) })
          }
        />
        <ChipListField
          label="Rejected currencies"
          description="Jobs that explicitly pay in these currencies are dropped."
          values={state.rejectedCurrencies}
          suggestions={currencySuggestions}
          onChange={(rejectedCurrencies) => patch({ rejectedCurrencies })}
        />
      </section>

      <section className="space-y-3 rounded-xl border border-border bg-surface p-5">
        <div>
          <Text as="p" className="text-sm font-semibold">
            Profile summary
          </Text>
          <Text as="p" styleVariant="muted" className="mt-0.5 text-xs">
            Only used by the optional AI second opinion via Claude CLI.
          </Text>
        </div>
        <TextArea
          value={state.profileSummary}
          placeholder="Frontend developer experienced with React and TypeScript…"
          containerClassName="max-w-none"
          onChange={(event) => patch({ profileSummary: event.target.value })}
        />
      </section>

      <div className="flex justify-end">
        <Button disabled={update.isPending} onClick={handleSave}>
          <Save /> {update.isPending ? 'Saving…' : 'Save preferences'}
        </Button>
      </div>
    </main>
  );
}
