import { describe, expect, it } from 'vitest';

import { joinPresets, splitPresets } from './mapping';
import { exclusionPresets, rolePresets } from './presets';

describe('splitPresets', () => {
  it('detects presets whose patterns are all present', () => {
    const values = ['front.?end', 'full.?stack', 'embedded.*engineer'];

    const selection = splitPresets(values, rolePresets);

    expect(selection.selected).toEqual(['frontend', 'fullstack']);
    expect(selection.custom).toEqual(['embedded.*engineer']);
  });

  it('keeps partially matched preset patterns as custom values', () => {
    const selection = splitPresets(['software.*engineer'], rolePresets);

    expect(selection.selected).toEqual([]);
    expect(selection.custom).toEqual(['software.*engineer']);
  });
});

describe('joinPresets', () => {
  it('expands selected presets and appends custom values', () => {
    const values = joinPresets(
      { selected: ['senior', 'management'], custom: ['\\bweb3\\b'] },
      exclusionPresets,
    );

    expect(values).toEqual([
      '\\b(?:senior|sr)\\b\\.?',
      '\\bmanager\\b',
      '\\bdirector\\b',
      '\\bvp\\b',
      '\\bweb3\\b',
    ]);
  });

  it('round-trips with splitPresets', () => {
    const original = ['front.?end', 'mobile.*(?:developer|engineer)', 'custom.*pattern'];

    const roundTripped = joinPresets(splitPresets(original, rolePresets), rolePresets);

    expect([...roundTripped].sort()).toEqual([...original].sort());
  });
});
