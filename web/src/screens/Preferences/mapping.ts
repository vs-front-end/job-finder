import type { TitlePreset } from './presets';

export type TitleSelection = {
  selected: string[];
  custom: string[];
};

export function splitPresets(values: string[], presets: TitlePreset[]): TitleSelection {
  const selected = presets
    .filter((preset) => preset.patterns.every((pattern) => values.includes(pattern)))
    .map((preset) => preset.id);
  const covered = new Set(
    presets
      .filter((preset) => selected.includes(preset.id))
      .flatMap((preset) => preset.patterns),
  );
  const custom = values.filter((value) => !covered.has(value));
  return { selected, custom };
}

export function joinPresets(selection: TitleSelection, presets: TitlePreset[]): string[] {
  const patterns = presets
    .filter((preset) => selection.selected.includes(preset.id))
    .flatMap((preset) => preset.patterns);
  const unique = new Set(patterns);
  return [...patterns, ...selection.custom.filter((value) => !unique.has(value))];
}
