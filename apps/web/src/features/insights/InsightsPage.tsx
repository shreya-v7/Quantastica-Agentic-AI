import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  AlertCircle,
  ArrowUpRight,
  BrainCircuit,
  Info,
  RefreshCw,
  Sparkles,
  Zap,
} from "lucide-react";
import { Card } from "../../components/Card";
import { fetchInsightHighlights, type InsightHighlight } from "../../lib/api";
import { useSystemConfig } from "../../providers/SystemConfigProvider";

const severityConfig: Record<
  InsightHighlight["severity"],
  {
    icon: typeof Info;
    accent: string;
    iconBg: string;
    iconColor: string;
    badge: string;
    label: string;
    glow: string;
  }
> = {
  info: {
    icon: Info,
    accent: "from-sky-500/80 via-blue-500/70 to-indigo-500/60",
    iconBg: "bg-sky-500/10 dark:bg-sky-400/15",
    iconColor: "text-sky-600 dark:text-sky-400",
    badge: "border-sky-500/25 bg-sky-500/5 text-sky-700 dark:text-sky-300",
    label: "Context",
    glow: "shadow-[0_0_24px_-4px_rgba(14,165,233,0.35)]",
  },
  watch: {
    icon: AlertCircle,
    accent: "from-amber-500/90 via-orange-500/70 to-amber-600/50",
    iconBg: "bg-amber-500/10 dark:bg-amber-400/15",
    iconColor: "text-amber-600 dark:text-amber-400",
    badge: "border-amber-500/25 bg-amber-500/5 text-amber-800 dark:text-amber-200",
    label: "Watch",
    glow: "shadow-[0_0_24px_-4px_rgba(245,158,11,0.3)]",
  },
  action: {
    icon: Zap,
    accent: "from-emerald-500/85 via-teal-500/65 to-cyan-500/55",
    iconBg: "bg-emerald-500/10 dark:bg-emerald-400/15",
    iconColor: "text-emerald-600 dark:text-emerald-400",
    badge: "border-emerald-500/25 bg-emerald-500/5 text-emerald-800 dark:text-emerald-200",
    label: "Action",
    glow: "shadow-[0_0_24px_-4px_rgba(16,185,129,0.3)]",
  },
};

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.07, delayChildren: 0.05 },
  },
};

const item = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

export default function InsightsPage() {
  const config = useSystemConfig();
  const { data, isPending, isError, refetch, isFetching } = useQuery({
    queryKey: ["insights", "highlights", config.demo.enabled],
    queryFn: fetchInsightHighlights,
    enabled: config.flags.insights && config.demo.enabled,
  });

  const count = data?.length ?? 0;

  return (
    <div className="relative min-h-[calc(100vh-8rem)]">
      {/* Ambient header wash */}
      <div
        className="pointer-events-none absolute -top-8 left-1/2 h-72 w-[min(100%,56rem)] -translate-x-1/2 rounded-full opacity-40 blur-3xl dark:opacity-30"
        style={{
          background:
            "radial-gradient(ellipse at center, hsl(var(--primary) / 0.22), transparent 65%)",
        }}
      />

      <div className="relative mx-auto max-w-4xl space-y-10 px-0">
        {/* Hero */}
        <motion.header
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="flex flex-col gap-6 border-b border-border/60 pb-10 sm:flex-row sm:items-end sm:justify-between"
        >
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-muted/35 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              <BrainCircuit className="h-3.5 w-3.5 text-primary" aria-hidden />
              Intelligence layer
            </div>
            <h1 className="fi-heading-xl mt-4 md:leading-tight">
              Insights{" "}
              <span className="bg-gradient-to-r from-primary via-sky-500 to-violet-500 bg-clip-text text-transparent">
                that compound
              </span>
            </h1>
            <p className="fi-body mt-3 max-w-xl">
              Curated signals from your portfolio context. Fewer tiles, clearer next steps.
            </p>
          </div>

          {data && data.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex shrink-0 items-center gap-3 rounded-2xl border border-border/80 bg-card/80 px-5 py-4 shadow-sm backdrop-blur-sm dark:bg-card/50"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Sparkles className="h-5 w-5" aria-hidden />
              </div>
              <div>
                <p className="text-2xl font-semibold tabular-nums tracking-tight text-foreground">
                  {count}
                </p>
                <p className="text-xs font-medium text-muted-foreground">Active highlights</p>
              </div>
            </motion.div>
          )}
        </motion.header>

        {(!config.flags.insights || !config.demo.enabled) && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-amber-500/35 bg-gradient-to-br from-amber-500/5 to-transparent p-6 dark:from-amber-500/10"
          >
            <div className="flex gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 text-amber-700 dark:text-amber-400">
                <Info className="h-5 w-5" />
              </div>
              <div>
                <p className="font-medium text-foreground">Insights unavailable</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {!config.flags.insights
                    ? "The server has disabled the insights feature flag."
                    : "Enable demo mode (FI_DEMO) to load sample insight highlights."}
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {isPending && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-36 rounded-2xl border border-border/50 bg-muted/20 fi-shimmer"
                aria-hidden
              />
            ))}
          </div>
        )}

        {isError && (
          <Card className="border-destructive/35 bg-destructive/5 p-6 dark:bg-destructive/10">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium text-destructive">Could not load insights</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Check the API and try again.
                </p>
              </div>
              <button
                type="button"
                onClick={() => refetch()}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-background px-4 py-2.5 text-sm font-semibold text-foreground transition hover:bg-muted/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
              >
                <RefreshCw className="h-4 w-4" aria-hidden />
                Retry
              </button>
            </div>
          </Card>
        )}

        {data && data.length === 0 && !isPending && (
          <div className="rounded-2xl border border-dashed border-border/80 bg-muted/20 px-8 py-16 text-center">
            <Sparkles className="mx-auto h-10 w-10 text-muted-foreground/50" aria-hidden />
            <p className="mt-4 text-sm font-medium text-foreground">No highlights yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              When new signals arrive, they will appear here.
            </p>
          </div>
        )}

        {data && data.length > 0 && (
          <motion.ul
            className="space-y-5"
            role="list"
            variants={container}
            initial="hidden"
            animate="show"
          >
            {data.map((highlight) => {
              const cfg = severityConfig[highlight.severity];
              const Icon = cfg.icon;
              return (
                <motion.li key={highlight.id} variants={item} layout="position">
                  <article
                    className={`group relative overflow-hidden rounded-2xl border border-border/80 bg-card/50 shadow-sm backdrop-blur-[2px] transition-all duration-300 hover:border-border hover:shadow-md dark:bg-card/30 dark:hover:border-primary/20 ${cfg.glow}`}
                  >
                    <div
                      className={`absolute left-0 top-0 h-full w-1 bg-gradient-to-b ${cfg.accent}`}
                      aria-hidden
                    />
                    <div className="relative pl-6 pr-5 py-6 sm:pl-7 sm:pr-7">
                      <div className="flex flex-col gap-5 sm:flex-row sm:gap-6">
                        <div
                          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${cfg.iconBg} ${cfg.iconColor}`}
                        >
                          <Icon className="h-6 w-6" strokeWidth={1.5} aria-hidden />
                        </div>
                        <div className="min-w-0 flex-1 space-y-3">
                          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                            <h2 className="text-lg font-semibold tracking-tight text-foreground">
                              {highlight.title}
                            </h2>
                            <span
                              className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider ${cfg.badge}`}
                            >
                              {cfg.label}
                            </span>
                            {isFetching && (
                              <span className="text-xs text-muted-foreground" aria-live="polite">
                                Updating…
                              </span>
                            )}
                          </div>
                          <p className="text-[15px] leading-relaxed text-muted-foreground">
                            {highlight.body}
                          </p>
                          {highlight.actionLabel && (
                            <button
                              type="button"
                              className="group/btn inline-flex items-center gap-1.5 text-sm font-semibold text-primary transition hover:text-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 rounded-lg -ml-1 px-1 py-1"
                            >
                              {highlight.actionLabel}
                              <ArrowUpRight className="h-4 w-4 transition group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5" aria-hidden />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </article>
                </motion.li>
              );
            })}
          </motion.ul>
        )}
      </div>
    </div>
  );
}
