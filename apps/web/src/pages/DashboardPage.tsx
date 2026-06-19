import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { usePortfolios, useRuns } from "../hooks/useApi";
import { api } from "../lib/api";
import { Card, PageHeader, Stat } from "../components/ui";
import { ErrorState, Loading } from "../components/states";
import { formatDate, formatInr } from "../lib/format";

export function DashboardPage() {
  const portfolios = usePortfolios();
  const runs = useRuns();
  const profile = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });

  if (portfolios.isLoading || runs.isLoading) return <Loading label="Loading dashboard" />;
  if (portfolios.error) return <ErrorState message={(portfolios.error as Error).message} />;
  if (runs.error) return <ErrorState message={(runs.error as Error).message} />;

  const completed = (runs.data ?? []).filter((r) => r.status === "completed").length;
  const recent = (runs.data ?? []).slice(0, 5);
  const goals = (profile.data?.goals ?? []).slice(0, 3);

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Ask an agent pipeline grounded questions about your portfolios."
      />
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Stat
          label="Net worth"
          value={profile.data ? profile.data.netWorth.netWorthDisplay : "..."}
        />
        <Stat label="Portfolios" value={String(portfolios.data?.length ?? 0)} />
        <Stat label="Agent runs" value={String(runs.data?.length ?? 0)} />
        <Stat label="Completed runs" value={String(completed)} />
      </div>

      {goals.length > 0 && (
        <Card className="mb-6">
          <h2 className="mb-3 font-semibold text-ink-900">Goal progress</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {goals.map((g) => (
              <div key={g.id}>
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{g.name}</span>
                  <span className="text-ink-400">{Math.round(g.progress * 100)}%</span>
                </div>
                <p className="text-xs text-ink-400">
                  {formatInr(g.savedInr)} of {formatInr(g.targetInr)}
                </p>
                <div className="mt-1 h-2 w-full rounded-full bg-ink-100">
                  <div
                    className="h-2 rounded-full bg-brand-600"
                    style={{ width: `${Math.round(g.progress * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-semibold text-ink-900">Portfolios</h2>
          <ul className="space-y-2">
            {(portfolios.data ?? []).map((p) => (
              <li key={p.id}>
                <Link
                  to={`/portfolios/${p.id}`}
                  className="flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-ink-50"
                >
                  <span className="font-medium">{p.name}</span>
                  <span className="text-ink-400">{p.baseCurrency}</span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <h2 className="mb-3 font-semibold text-ink-900">Recent runs</h2>
          {recent.length === 0 ? (
            <p className="text-sm text-ink-500">
              No runs yet. Head to <Link className="text-brand-600" to="/agents">Agents</Link> to start one.
            </p>
          ) : (
            <ul className="space-y-2 text-sm">
              {recent.map((run) => (
                <li key={run.id} className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-ink-50">
                  <span className="truncate pr-3">{run.query}</span>
                  <span className="text-ink-400">{formatDate(run.createdAt)}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
