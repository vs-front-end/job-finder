import type { ReactNode } from 'react';

import { cn } from '@stellar-ui-kit/shared';

type RichDescriptionProps = {
  html: string | null;
  text: string;
  className?: string;
};

export function RichDescription({ html, text, className }: RichDescriptionProps) {
  if (!html) {
    return <p className={cn('whitespace-pre-wrap text-sm leading-6 text-muted', className)}>{text}</p>;
  }

  const document = new DOMParser().parseFromString(html, 'text/html');

  return (
    <div className={cn('space-y-3 text-sm leading-6 text-muted', className)}>
      {renderChildren(document.body, 'description')}
    </div>
  );
}

function renderChildren(element: Element, path: string): ReactNode[] {
  return Array.from(element.childNodes).map((node, index) => renderNode(node, `${path}-${index}`));
}

function renderNode(node: Node, key: string): ReactNode {
  if (node.nodeType === Node.TEXT_NODE) return node.textContent;
  if (!(node instanceof Element)) return null;

  const children = renderChildren(node, key);
  switch (node.tagName.toLowerCase()) {
    case 'p':
      return <p key={key}>{children}</p>;
    case 'strong':
    case 'b':
      return <strong key={key} className="font-semibold text-foreground">{children}</strong>;
    case 'em':
    case 'i':
      return <em key={key}>{children}</em>;
    case 'u':
      return <u key={key} className="underline underline-offset-2">{children}</u>;
    case 'a':
      return renderLink(node, children, key);
    case 'ul':
      return <ul key={key} className="list-disc space-y-1 pl-5">{children}</ul>;
    case 'ol':
      return <ol key={key} className="list-decimal space-y-1 pl-5">{children}</ol>;
    case 'li':
      return <li key={key} className="pl-0.5">{children}</li>;
    case 'h1':
    case 'h2':
    case 'h3':
    case 'h4':
    case 'h5':
    case 'h6':
      return <h5 key={key} className="pt-1 text-sm font-semibold text-foreground">{children}</h5>;
    case 'blockquote':
      return <blockquote key={key} className="border-l-2 border-primary pl-3 italic">{children}</blockquote>;
    case 'code':
      return <code key={key} className="rounded bg-secondary-soft px-1 py-0.5 text-xs text-foreground">{children}</code>;
    case 'pre':
      return <pre key={key} className="overflow-x-auto rounded-lg bg-secondary-soft p-3 text-xs text-foreground">{children}</pre>;
    case 'br':
      return <br key={key} />;
    default:
      return <span key={key}>{children}</span>;
  }
}

function renderLink(element: Element, children: ReactNode[], key: string): ReactNode {
  const href = element.getAttribute('href');
  if (!href || !isSafeHref(href)) return <span key={key}>{children}</span>;
  return (
    <a
      key={key}
      href={href}
      target="_blank"
      rel="noreferrer"
      className="font-medium text-primary-text underline underline-offset-2"
    >
      {children}
    </a>
  );
}

function isSafeHref(value: string): boolean {
  try {
    return ['http:', 'https:', 'mailto:'].includes(new URL(value).protocol);
  } catch {
    return false;
  }
}
