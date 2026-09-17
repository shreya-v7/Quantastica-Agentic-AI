export function Disclaimer({ className = "" }: { className?: string }) {
  return (
    <p className={`text-xs leading-5 text-ink-400 ${className}`}>
      Informational only. Not investment advice, not a SEBI-registered advisory service, and not a
      solicitation to buy or sell any security.
    </p>
  );
}

export function BrandMark() {
  return (
    <span className="inline-flex items-center gap-2.5">
      <svg width="24" height="24" viewBox="0 0 32 32" aria-hidden="true">
        <path
          d="M22.8 19.8A9.4 9.4 0 1 0 19.8 22.8"
          fill="none"
          stroke="currentColor"
          className="text-pine-500"
          strokeWidth="2.3"
          strokeLinecap="square"
        />
        <path
          d="M9.2 19.4h10.8L28.2 28"
          fill="none"
          stroke="currentColor"
          className="text-pine-600"
          strokeWidth="1.8"
          strokeLinecap="square"
          strokeLinejoin="miter"
        />
        <path d="M11.2 19.4v-3.1" stroke="currentColor" className="text-pine-500" strokeWidth="1.7" strokeLinecap="square" />
        <path d="M14.3 19.4v-5.3" stroke="currentColor" className="text-pine-500" strokeWidth="1.7" strokeLinecap="square" />
        <path d="M17.4 19.4v-7.5" stroke="currentColor" className="text-pine-600" strokeWidth="1.7" strokeLinecap="square" />
      </svg>
      <span className="font-display text-[15px] font-medium tracking-[0.22em] text-ink-900">
        QUANTASTICA
      </span>
    </span>
  );
}
