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
    label: 'Triagem',
    items: [
      { value: 'new', label: 'Novas', icon: Inbox },
      { value: 'uncertain', label: 'Revisar região', icon: CircleHelp },
      { value: 'saved', label: 'Salvas', icon: Bookmark },
    ],
  },
  {
    label: 'Pipeline',
    items: [
      { value: 'applied', label: 'Candidatei', icon: Send },
      { value: 'in_process', label: 'Em processo', icon: Activity },
    ],
  },
  {
    label: 'Arquivo',
    items: [
      { value: 'closed', label: 'Encerradas', icon: Archive },
      { value: 'dismissed', label: 'Descartadas', icon: CircleX },
      { value: 'all', label: 'Todas as vagas', icon: Layers },
    ],
  },
];

export const queueItems = queueGroups.flatMap((group) => group.items);
