import { useState } from 'react';

import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  InputText,
} from '@stellar-ui-kit/web';

import { Link } from 'lucide-react';

type AddJobDialogProps = {
  open: boolean;
  busy: boolean;
  error: string | null;
  onOpenChange: (open: boolean) => void;
  onSubmit: (url: string) => void;
};

export function AddJobDialog({ open, busy, error, onOpenChange, onSubmit }: AddJobDialogProps) {
  const [url, setUrl] = useState('');
  const valid = URL.canParse(url);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Adicionar vaga por URL</DialogTitle>
          <DialogDescription>
            O radar lê o JobPosting estruturado da página e aplica os mesmos filtros da coleta.
          </DialogDescription>
        </DialogHeader>
        <InputText
          label="Link público da vaga"
          placeholder="https://empresa.com/careers/vaga"
          value={url}
          onChange={setUrl}
          startIcon={Link}
          error={error ?? undefined}
        />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button disabled={!valid || busy} onClick={() => onSubmit(url)}>
            {busy ? 'Lendo página…' : 'Adicionar vaga'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

