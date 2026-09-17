import { useState } from "react";
import type { Severity } from "@quantastica/types";
import { useInsights, usePortfolios } from "../hooks/useApi";
import { Card, PageHeader, SeverityBadge } from "../components/ui";
import { EmptyState, ErrorState, Loading } from "../components/states";
import { formatDate } from "../lib/format";

const SEVERITIES: Severity[] = ["info", "low", "medium", "high"];

export function InsightsPage() {
  const portfolios = usePortfolios();
  const [portfolioId, setPortfolioId] = useState("");
  const [severity, setSeverity] = useState<Severity | "">("");

  const insights = useInsights(portfolioId || undefined, severity || undefined);

  return (
    <div>
      <PageHeader title="Insights" subtitle="Findings produced by completed agent runs." />

      <div className="mb-6 flex flex-wrap gap-3">
        <select
          value={portfolioId}
          onChange={(e) => setPortfolioId(e.target.value)}
          className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
        >
          <option value="">All portfolios</option>
          {(portfolios.data ?? []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value as Severity | "")}
          className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
        >
          <option value="">All severities</option>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {insights.isLoading && <Loading label="Loading insights" />}
      {insights.error && <ErrorState message={(insights.error as Error).message} />}
      {insights.data && insights.data.length === 0 && (
        <EmptyState title="No insights yet">Run an analysis on the Agents page.</EmptyState>
      )}
      {insights.data && insights.data.length > 0 && (
        <div className="space-y-3">
          {insights.data.map((f) => (
            <Card key={f.id}>
              <div className="flex items-center justify-between">
                <span className="font-semibold">{f.title}</span>
                <SeverityBadge severity={f.severity} />
              </div>
              <p className="mt-1 text-sm text-ink-500">{f.body}</p>
              <p className="mt-2 text-xs text-ink-400">
                Confidence {Math.round(f.confidence * 100)}% · cites {f.metricIds.join(", ") || "none"} ·{" "}
                {formatDate(f.createdAt)}
              </p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
