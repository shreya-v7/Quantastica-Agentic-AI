import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { Card } from "../../components/Card";
import { Chart } from "../../components/Chart";
import { Metric } from "../../components/Metric";
import { fetchDashboardPayload } from "../../lib/api";
import { useSystemConfig } from "../../providers/SystemConfigProvider";

function formatMoney(n: number) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

export default function DashboardPage() {
  const config = useSystemConfig();
  const { data, isPending, isError, refetch, isFetching } = useQuery({
    queryKey: ["dashboard", "snapshot", config.demo.enabled],
    queryFn: fetchDashboardPayload,
    staleTime: 60_000,
    enabled: config.flags.insights && config.demo.enabled,
  });

  const showDebtCta = data?.showRefinanceCta ?? false;

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <motion.header
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"
      >
        <div>
          <p className="text-sm font-medium text-muted-foreground">Intelligence</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
            Overview
          </h1>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">
            Calm, high-signal financial context — no clutter, no noise.
          </p>
        </div>
        {config.flags.ai && (
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 self-start rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-md transition hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
          >
            <Sparkles className="h-4 w-4" aria-hidden />
            Ask AI
          </Link>
        )}
      </motion.header>

      {(!config.flags.insights || !config.demo.enabled) && (
        <Card className="border-amber-500/40">
          <p className="text-sm text-foreground">
            {!config.flags.insights
              ? "Insights are disabled by the server."
              : "Demo data is disabled. Enable FI_DEMO or connect an authenticated data source."}
          </p>
        </Card>
      )}

      {isPending && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-36 rounded-2xl fi-shimmer" aria-hidden />
          ))}
        </div>
      )}

      {isError && (
        <Card className="border-destructive/40">
          <p className="text-sm text-destructive">Could not load snapshot.</p>
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
        <>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <Card variant="gradient" className="md:col-span-2">
              <Metric
                label="Net worth"
                value={formatMoney(data.summary.netWorth)}
                sublabel="Across cash, investments, minus debt (from insight engine)"
                delay={0}
              />
            </Card>
            <Card>
              <Metric label="Cash & equivalents" value={formatMoney(data.cash)} sublabel="Liquid" delay={0.05} />
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <div className="mb-4 flex items-center justify-between gap-2">
                <div>
                  <h3 className="text-base font-semibold text-foreground">Investments</h3>
                  <p className="text-xs text-muted-foreground">Trend — total portfolio value</p>
                </div>
                {isFetching && (
                  <span className="text-xs text-muted-foreground" aria-live="polite">
                    Refreshing…
                  </span>
                )}
              </div>
              <Chart data={data.chart} gradientId="fi-dash-area" />
            </Card>

            <div className="flex flex-col gap-6">
              <Card>
                <Metric
                  label="Total debt"
                  value={formatMoney(data.debtTotal)}
                  trend="down"
                  trendLabel="On track (demo)"
                  delay={0.08}
                />
                {showDebtCta && (
                  <button
                    type="button"
                    className="mt-4 w-full rounded-xl border border-primary/30 bg-primary/5 py-2.5 text-sm font-semibold text-primary transition hover:bg-primary/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                  >
                    Refinance high-rate debt
                  </button>
                )}
              </Card>

              <Card variant="gradient">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
                    <Sparkles className="h-4 w-4" aria-hidden />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">AI insight</h3>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{data.insightSummary}</p>
                    <Link
                      to="/insights"
                      className="mt-3 inline-block text-sm font-medium text-primary hover:underline"
                    >
                      See all insights
                    </Link>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
