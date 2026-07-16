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
          <DialogTitle>Add job from URL</DialogTitle>
          <DialogDescription>
            The radar reads the page's structured JobPosting and applies the same collection
            filters.
          </DialogDescription>
        </DialogHeader>
        <InputText
          label="Public job link"
          placeholder="https://company.com/careers/job"
          value={url}
          onChange={setUrl}
          startIcon={Link}
          error={error ?? undefined}
        />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button disabled={!valid || busy} onClick={() => onSubmit(url)}>
            {busy ? 'Reading page…' : 'Add job'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
