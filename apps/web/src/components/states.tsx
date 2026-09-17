import type { ReactNode } from "react";
import { AlertTriangle, Inbox, Loader2 } from "lucide-react";

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-12 font-mono text-sm text-ink-500">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span>{label}...</span>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 border border-red-900/70 bg-red-950/40 p-4 text-red-300">
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
      <div>
        <p className="font-medium">Something went wrong</p>
        <p className="text-sm text-red-200/80">{message}</p>
      </div>
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center border border-dashed border-ink-200 py-12 text-center text-ink-500">
      <Inbox className="mb-3 h-7 w-7" />
      <p className="font-medium text-ink-700">{title}</p>
      {children && <p className="mt-1 text-sm">{children}</p>}
    </div>
  );
}
