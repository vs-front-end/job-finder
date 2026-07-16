import {
  Activity,
  Archive,
  Bookmark,
  CircleHelp,
  CircleX,
  Inbox,
  Layers,
  Send,
  type LucideIcon,
} from 'lucide-react';

export type QueueTab =
  | 'new'
  | 'uncertain'
  | 'saved'
  | 'applied'
  | 'in_process'
  | 'closed'
  | 'dismissed'
  | 'all';

type QueueItem = {
  value: QueueTab;
  label: string;
  icon: LucideIcon;
};

export const queueGroups: { label: string; items: QueueItem[] }[] = [
  {
    label: 'Triage',
    items: [
      { value: 'new', label: 'New', icon: Inbox },
      { value: 'uncertain', label: 'Region review', icon: CircleHelp },
      { value: 'saved', label: 'Saved', icon: Bookmark },
    ],
  },
  {
    label: 'Pipeline',
    items: [
      { value: 'applied', label: 'Applied', icon: Send },
      { value: 'in_process', label: 'In process', icon: Activity },
    ],
  },
  {
    label: 'Archive',
    items: [
      { value: 'closed', label: 'Closed', icon: Archive },
      { value: 'dismissed', label: 'Dismissed', icon: CircleX },
      { value: 'all', label: 'All jobs', icon: Layers },
    ],
  },
];

export const queueItems = queueGroups.flatMap((group) => group.items);
