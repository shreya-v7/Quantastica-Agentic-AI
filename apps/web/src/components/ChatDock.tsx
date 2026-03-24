import { lazy, Suspense, useMemo, useState, type ComponentType } from "react";
import {
  MessageCircle,
  X,
  Maximize2,
  Minimize2,
  Sparkles,
  LineChart,
  Newspaper,
  Wallet,
  Scale,
  PiggyBank,
} from "lucide-react";

const ChatInterface = lazy(() => import("./ChatInterface"));

const CHAT_TOPICS: {
  id: string;
  label: string;
  hint: string;
  Icon: ComponentType<{ className?: string }>;
  defaultAgentName: string;
}[] = [
  {
    id: "general",
    label: "General",
    hint: "Everyday finance",
    Icon: MessageCircle,
    defaultAgentName: "Wealth Manager Agent",
  },
  {
    id: "investments",
    label: "Investments",
    hint: "Portfolios & analysis",
    Icon: LineChart,
    defaultAgentName: "Investment Analysis Agent",
  },
  {
    id: "markets",
    label: "Markets & news",
    hint: "Headlines & context",
    Icon: Newspaper,
    defaultAgentName: "News Analyzer Agent",
  },
  {
    id: "loans",
    label: "Loans & insurance",
    hint: "Policies & coverage",
    Icon: Wallet,
    defaultAgentName: "Loan Insurance Agent",
  },
  {
    id: "tax",
    label: "Tax planning",
    hint: "Rules & optimization",
    Icon: Scale,
    defaultAgentName: "Wealth Manager Agent",
  },
  {
    id: "budget",
    label: "Budget & goals",
    hint: "Saving & planning",
    Icon: PiggyBank,
    defaultAgentName: "Wealth Manager Agent",
  },
];

function DockFallback() {
  return (
    <div className="flex h-full min-h-[200px] flex-col justify-center gap-3 p-6">
      <div className="h-9 rounded-lg fi-shimmer" />
      <div className="h-32 rounded-xl fi-shimmer" />
      <div className="h-10 rounded-lg fi-shimmer" />
    </div>
  );
}

/**
 * Bottom-right assistant: icon → floating panel → expanded mode with topic rail.
 * No separate browser window; stays on the same screen.
 */
export function ChatDock() {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [activeTopicId, setActiveTopicId] = useState(CHAT_TOPICS[0].id);

  const activeTopic = useMemo(
    () => CHAT_TOPICS.find((t) => t.id === activeTopicId) ?? CHAT_TOPICS[0],
    [activeTopicId]
  );

  const close = () => {
    setOpen(false);
    setExpanded(false);
  };

  return (
    <div className="pointer-events-none fixed bottom-0 right-0 z-50 flex flex-col items-end">
      {/* Panel — clear step up from the page: card + ring + shadow */}
      {open && (
        <div
          className={`
            pointer-events-auto mb-2 mr-3 flex overflow-hidden rounded-2xl border border-border bg-card shadow-2xl ring-1 ring-foreground/5 transition-[width,height] duration-300 ease-out dark:bg-card dark:ring-white/10
            md:mr-6 md:mb-3
            ${
              expanded
                ? "h-[min(640px,calc(100dvh-5.5rem))] w-[min(720px,calc(100vw-1.25rem))] flex-row"
                : "h-[min(520px,calc(100dvh-7rem))] w-[min(400px,calc(100vw-1.25rem))] flex-col"
            }
          `}
        >
          {/* Topic index — only when expanded */}
          {expanded && (
            <nav
              className="flex w-[10.5rem] shrink-0 flex-col border-r border-border bg-muted/50 p-2 dark:bg-muted/25"
              aria-label="Chat topics"
            >
              <div className="flex items-center gap-1.5 border-b border-border/60 px-2 pb-2 pt-1">
                <Sparkles className="h-3.5 w-3.5 text-primary" aria-hidden />
                <span className="text-[0.65rem] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Topics
                </span>
              </div>
              <ul className="mt-2 flex min-h-0 flex-1 flex-col gap-0.5 overflow-y-auto py-1 [scrollbar-width:thin]">
                {CHAT_TOPICS.map((t) => {
                  const isOn = t.id === activeTopicId;
                  return (
                    <li key={t.id}>
                      <button
                        type="button"
                        onClick={() => setActiveTopicId(t.id)}
                        className={`
                          flex w-full items-start gap-2 rounded-lg px-2 py-2 text-left text-sm transition-colors
                          ${
                            isOn
                              ? "bg-background font-medium text-foreground shadow-sm ring-1 ring-border dark:bg-background/80"
                              : "text-muted-foreground hover:bg-muted/80 hover:text-foreground"
                          }
                        `}
                      >
                        <t.Icon className={`mt-0.5 h-4 w-4 shrink-0 ${isOn ? "text-primary" : ""}`} aria-hidden />
                        <span className="min-w-0 leading-tight">
                          <span className="block">{t.label}</span>
                          <span className="mt-0.5 block text-[0.65rem] font-normal text-muted-foreground">{t.hint}</span>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>
          )}

          {/* Main chat column */}
          <div className="flex min-h-0 min-w-0 flex-1 flex-col">
            <header className="flex shrink-0 items-center justify-between gap-2 border-b border-border bg-muted/40 px-3 py-2.5 dark:bg-muted/20">
              <div className="min-w-0">
                <p className="text-[0.6rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">Assistant</p>
                <p className="truncate text-sm font-semibold text-foreground">FinGPT</p>
                {expanded && (
                  <p className="mt-0.5 truncate text-[0.7rem] text-muted-foreground">
                    Topic: <span className="font-medium text-foreground">{activeTopic.label}</span>
                  </p>
                )}
              </div>
              <div className="flex shrink-0 items-center gap-0.5">
                <button
                  type="button"
                  onClick={() => setExpanded((e) => !e)}
                  className="rounded-lg p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
                  aria-expanded={expanded}
                  aria-label={expanded ? "Show compact assistant" : "Expand topics"}
                  title={expanded ? "Compact view" : "Expand — more topics"}
                >
                  {expanded ? <Minimize2 className="h-4 w-4" strokeWidth={2} /> : <Maximize2 className="h-4 w-4" strokeWidth={2} />}
                </button>
                <button
                  type="button"
                  onClick={close}
                  className="rounded-lg p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
                  aria-label="Close assistant"
                  title="Close"
                >
                  <X className="h-4 w-4" strokeWidth={2} />
                </button>
              </div>
            </header>

            <div className="min-h-0 flex-1 overflow-hidden bg-background">
              <Suspense fallback={<DockFallback />}>
                <ChatInterface
                  key={activeTopicId}
                  docked
                  defaultAgentName={activeTopic.defaultAgentName}
                />
              </Suspense>
            </div>
          </div>
        </div>
      )}

      {/* Launcher — only when panel closed; visually separate from page content */}
      {!open && (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="pointer-events-auto m-3 flex h-14 w-14 items-center justify-center rounded-full border border-border bg-card text-foreground shadow-[0_10px_40px_-10px_rgba(0,0,0,0.25)] ring-2 ring-background transition hover:bg-muted/90 hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring md:m-6 dark:shadow-[0_12px_40px_-12px_rgba(0,0,0,0.5)] dark:ring-background"
          aria-label="Open assistant"
          title="Open assistant"
        >
          <MessageCircle className="h-6 w-6" strokeWidth={1.75} aria-hidden />
        </button>
      )}
    </div>
  );
}
