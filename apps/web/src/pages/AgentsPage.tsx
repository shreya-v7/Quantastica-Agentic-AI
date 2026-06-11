import { useState } from "react";
import { useExportRun, usePortfolios, useRun, useRunAgents } from "../hooks/useApi";
import { Badge, Card, PageHeader, RatingBadge, SeverityBadge } from "../components/ui";
import { ErrorState, Loading } from "../components/states";
import { AgentTrace } from "../components/AgentTrace";

export function AgentsPage() {
  const portfolios = usePortfolios();
  const runAgents = useRunAgents();
  const exportRun = useExportRun();

  const [portfolioId, setPortfolioId] = useState("");
  const [query, setQuery] = useState("How concentrated is my AI portfolio?");
  const [runId, setRunId] = useState<string | null>(null);

  const run = useRun(runId, true);
  const activePortfolio = portfolioId || portfolios.data?.[0]?.id || "";

  function submit(event: React.FormEvent) {
    event.preventDefault();
    runAgents.mutate(
      { query, portfolioId: activePortfolio },
      { onSuccess: (created) => setRunId(created.id) },
    );
  }

  const current = run.data;

  return (
    <div>
      <PageHeader title="Agents" subtitle="Run the analysis pipeline and watch the live trace." />

      <Card className="mb-6">
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Portfolio</label>
            <select
              value={activePortfolio}
              onChange={(e) => setPortfolioId(e.target.value)}
              className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm"
            >
              {(portfolios.data ?? []).map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Question</label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={2}
              className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={runAgents.isPending || !activePortfolio || !query.trim()}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            {runAgents.isPending ? "Running..." : "Run analysis"}
          </button>
        </form>
        {runAgents.error && (
          <div className="mt-4">
            <ErrorState message={(runAgents.error as Error).message} />
          </div>
        )}
      </Card>

      {runId && run.isLoading && <Loading label="Starting run" />}
      {current && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-semibold">Execution trace</h2>
              <Badge tone={current.status === "failed" ? "high" : current.status === "completed" ? "low" : "info"}>
                {current.status}
              </Badge>
            </div>
            <AgentTrace steps={current.steps} />
            {current.error && <p className="mt-3 text-sm text-red-600">{current.error}</p>}
          </Card>

          <div className="space-y-6">
            {current.answer && (
              <Card>
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="font-semibold">Answer</h2>
                  <button
                    onClick={() => exportRun.mutate(current.id)}
                    className="text-sm text-brand-600"
                  >
                    {exportRun.isPending ? "Exporting..." : "Export JSON"}
                  </button>
                </div>
                <p className="whitespace-pre-line text-sm text-ink-700">{current.answer}</p>
                {exportRun.data && (
                  <p className="mt-2 text-xs text-ink-400">Saved to {exportRun.data.location}</p>
                )}
              </Card>
            )}

            {current.metrics.length > 0 && (
              <Card>
                <h2 className="mb-3 font-semibold">Risk metrics</h2>
                <ul className="space-y-2 text-sm">
                  {current.metrics.map((m) => (
                    <li key={m.id} className="flex items-center justify-between">
                      <span className="text-ink-700">{m.label}</span>
                      <span className="flex items-center gap-2">
                        <span className="font-medium">{m.value.toFixed(3)}</span>
                        <RatingBadge rating={m.rating} />
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {current.findings.length > 0 && (
              <Card>
                <h2 className="mb-3 font-semibold">Findings</h2>
                <ul className="space-y-3">
                  {current.findings.map((f) => (
                    <li key={f.id} className="border-t border-ink-100 pt-3 first:border-0 first:pt-0">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{f.title}</span>
                        <SeverityBadge severity={f.severity} />
                      </div>
                      <p className="mt-1 text-sm text-ink-500">{f.body}</p>
                      <p className="mt-1 text-xs text-ink-400">Cites: {f.metricIds.join(", ") || "none"}</p>
                    </li>
                  ))}
                </ul>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
