import { useEffect, useState, type ButtonHTMLAttributes, type ReactNode } from "react";
import type { Rating, Severity } from "@quantastica/types";

export function Frame({
  children,
  className = "",
  label,
}: {
  children: ReactNode;
  className?: string;
  label?: string;
}) {
  return (
    <div className={`frame ${label ? "pt-3" : ""} ${className}`}>
      <span className="frame-c frame-c-tl" />
      <span className="frame-c frame-c-tr" />
      <span className="frame-c frame-c-bl" />
      <span className="frame-c frame-c-br" />
      {label ? <span className="frame-k">{label}</span> : null}
      {children}
    </div>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <Frame className={`p-5 ${className}`}>{children}</Frame>;
}

export function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-8">
      <p className="mb-2 font-mono text-[10px] uppercase tracking-label text-pine-500">// {title}</p>
      <h1 className="font-display text-3xl font-light tracking-tight text-ink-900 md:text-4xl">{title}</h1>
      {subtitle && <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-500">{subtitle}</p>}
    </div>
  );
}

export function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card>
      <p className="font-mono text-[10px] uppercase tracking-label text-ink-400">{label}</p>
      <p className="mt-2 font-mono text-2xl font-medium tabular-nums tracking-tight text-ink-900">
        {value}
      </p>
      {hint && <p className="mt-1 text-xs text-ink-500">{hint}</p>}
    </Card>
  );
}

const TONE: Record<string, string> = {
  high: "border-red-500/50 bg-red-950/40 text-red-300",
  medium: "border-ink-200 bg-ink-50 text-ink-700",
  low: "border-pine-600/40 bg-pine-50 text-pine-500",
  info: "border-ink-200 bg-ink-50 text-ink-700",
  neutral: "border-ink-200 bg-ink-50 text-ink-700",
};

export function Badge({ tone = "neutral", children }: { tone?: string; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center border px-1.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-label ${TONE[tone] ?? TONE.neutral}`}
    >
      {children}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return <Badge tone={severity}>{severity}</Badge>;
}

export function RatingBadge({ rating }: { rating: Rating }) {
  return <Badge tone={rating}>{rating} risk</Badge>;
}

export function PrimaryButton({
  children,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`btn-cut bg-pine-600 px-5 py-2.5 text-sm font-medium transition hover:bg-pine-500 disabled:opacity-50 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function GhostButton({
  children,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`border border-ink-200 bg-transparent px-4 py-2 text-sm font-medium text-ink-700 transition hover:border-pine-500 hover:text-ink-900 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function IstClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);
  const stamp = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Kolkata",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(now);
  return (
    <span className="font-mono text-[11px] tabular-nums tracking-wider text-pine-500">
      {stamp} IST
    </span>
  );
}

export function LiveDot() {
  return <span className="inline-block h-1.5 w-1.5 bg-pine-500 animate-pulseDot" />;
}
