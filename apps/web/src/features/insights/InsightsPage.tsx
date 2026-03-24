import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { AlertCircle, Info, Zap } from "lucide-react";
import { Card } from "../../components/Card";
import { fetchInsightHighlights, type InsightHighlight } from "../../lib/api";
import { useSystemConfig } from "../../providers/SystemConfigProvider";

const severityStyles: Record<InsightHighlight["severity"], { icon: typeof Info; bar: string; label: string }> =
  {
    info: {
      icon: Info,
      bar: "bg-primary/80",
      label: "Context",
    },
    watch: {
      icon: AlertCircle,
      bar: "bg-amber-500/90",
      label: "Watch",
    },
    action: {
      icon: Zap,
      bar: "bg-emerald-500/90",
      label: "Healthy",
    },
  };

export default function InsightsPage() {
  const config = useSystemConfig();
  const { data, isPending, isError, refetch } = useQuery({
    queryKey: ["insights", "highlights", config.demo.enabled],
    queryFn: fetchInsightHighlights,
    enabled: config.flags.insights && config.demo.enabled,
  });

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <motion.header initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <p className="text-sm font-medium text-muted-foreground">Insights</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">What matters now</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Highlights, not dashboards — progressive disclosure keeps complexity out of the way.
        </p>
      </motion.header>

      {(!config.flags.insights || !config.demo.enabled) && (
        <Card className="border-amber-500/40">
          <p className="text-sm text-foreground">
            {!config.flags.insights
              ? "Insights are disabled by the server."
              : "Demo insight highlights require FI_DEMO enabled."}
          </p>
        </Card>
      )}

      {isPending && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 rounded-2xl fi-shimmer" aria-hidden />
          ))}
        </div>
      )}

      {isError && (
        <Card className="border-destructive/40">
          <p className="text-sm text-destructive">Could not load insights.</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-3 text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            Retry
          </button>
        </Card>
      )}

      {data && (
        <ul className="space-y-4" role="list">
          {data.map((item, index) => {
            const cfg = severityStyles[item.severity];
            const Icon = cfg.icon;
            return (
              <motion.li
                key={item.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.06 }}
              >
                <Card className="overflow-hidden p-0">
                  <div className={`h-1 w-full ${cfg.bar}`} aria-hidden />
                  <div className="p-5">
                    <div className="flex items-start gap-3">
                      <Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" aria-hidden />
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h2 className="text-base font-semibold text-foreground">{item.title}</h2>
                          <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                            {cfg.label}
                          </span>
                        </div>
                        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
                        {item.actionLabel && (
                          <button
                            type="button"
                            className="mt-4 text-sm font-semibold text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 rounded-md"
                          >
                            {item.actionLabel}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
