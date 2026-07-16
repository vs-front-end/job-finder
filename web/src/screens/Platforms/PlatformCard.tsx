import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import {
  Badge,
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Text,
} from '@stellar-ui-kit/web';

import { ArrowUpRight, CheckCircle2 } from 'lucide-react';

import type { Platform, PlatformTrackingStatus } from '@/api/schema';
import { InitialsAvatar } from '@/components';

const availabilityLabel = {
  active: 'Automática',
  needs_key: 'Precisa de chave',
  manual: 'Manual',
  planned: 'Planejada',
} as const;

const trackingLabel: Record<PlatformTrackingStatus, string> = {
  pending: 'Pendente',
  done: 'Configurada / revisada',
  review_due: 'Revisar novamente',
  skipped: 'Ignorar',
};

type PlatformCardProps = {
  platform: Platform;
  busy: boolean;
  onUpdate: (platform: Platform, status: PlatformTrackingStatus) => void;
};

export function PlatformCard({ platform, busy, onUpdate }: PlatformCardProps) {
  const automatic = platform.availability === 'active';

  return (
    <div className="flex h-full flex-col gap-4 rounded-xl border border-border bg-surface p-5 transition-colors hover:border-primary">
      <div className="flex items-start gap-3">
        <InitialsAvatar name={platform.name} />
        <div className="min-w-0 flex-1">
          <Text as="h3" className="text-sm font-semibold leading-snug">
            {platform.name}
          </Text>
          <Text as="p" styleVariant="muted" className="mt-0.5 text-xs">
            {platform.category}
          </Text>
        </div>
        <Badge variant={availabilityVariant(platform.availability)}>
          {availabilityLabel[platform.availability]}
        </Badge>
      </div>

      <Text as="p" styleVariant="muted" className="flex-1 text-sm leading-relaxed">
        {platform.description}
      </Text>

      {automatic ? (
        <div className="flex items-center gap-2 rounded-lg bg-success-soft px-3 py-2 text-sm font-medium text-success-text">
          <CheckCircle2 className="size-4 shrink-0" /> Coleta integrada
        </div>
      ) : (
        <Select
          value={platform.tracking_status}
          disabled={busy}
          onValueChange={(value) => isTrackingStatus(value) && onUpdate(platform, value)}
        >
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(trackingLabel).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      <div className="flex items-center justify-between gap-3 border-t border-border pt-4">
        <Text as="p" styleVariant="muted" className="text-xs">
          {reviewLabel(platform)}
        </Text>
        <Button variant="outline" size="sm" asChild>
          <a href={platform.url} target="_blank" rel="noreferrer">
            Abrir <ArrowUpRight />
          </a>
        </Button>
      </div>
    </div>
  );
}

function availabilityVariant(availability: Platform['availability']) {
  if (availability === 'active') return 'success' as const;
  if (availability === 'needs_key') return 'warning' as const;
  if (availability === 'planned') return 'outline' as const;
  return 'secondary' as const;
}

function reviewLabel(platform: Platform) {
  if (platform.availability === 'needs_key') return 'Configure a chave gratuita';
  if (!platform.last_reviewed_at) return trackingLabel[platform.tracking_status];
  return `Revisada em ${format(new Date(platform.last_reviewed_at), "dd 'de' MMM", { locale: ptBR })}`;
}

function isTrackingStatus(value: string): value is PlatformTrackingStatus {
  return value in trackingLabel;
}
