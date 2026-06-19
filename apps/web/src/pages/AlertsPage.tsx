import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Card, PageHeader, Badge } from "../components/ui";
import { EmptyState, ErrorState, Loading } from "../components/states";
import { formatInr, formatDate } from "../lib/format";

export function AlertsPage() {
  const queryClient = useQueryClient();
  const alerts = useQuery({ queryKey: ["alerts"], queryFn: api.listAlerts });
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["alerts"] });
  const create = useMutation({ mutationFn: api.createAlert, onSuccess: invalidate });
  const remove = useMutation({ mutationFn: api.deleteAlert, onSuccess: invalidate });

  const n = (v: FormDataEntryValue | null) => Number(v ?? 0);

  return (
    <div>
      <PageHeader
        title="Alerts"
        subtitle="Price alerts evaluated by the background worker and delivered over WhatsApp."
      />

      <Card className="mb-6">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            create.mutate({
              name: f.get("name"),
              symbol: String(f.get("symbol")).toUpperCase(),
              operator: f.get("operator"),
              threshold: n(f.get("threshold")),
            });
            e.currentTarget.reset();
          }}
          className="grid gap-3 md:grid-cols-5"
        >
          <input name="name" placeholder="Alert name" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="symbol" placeholder="RELIANCE.NS" className="rounded-lg border border-ink-200 px-3 py-2 text-sm uppercase" />
          <select name="operator" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            <option value="below">Below</option>
            <option value="above">Above</option>
          </select>
          <input name="threshold" type="number" step="any" placeholder="Price" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Add alert
          </button>
        </form>
        {create.error && (
          <p className="mt-3">
            <ErrorState message={(create.error as Error).message} />
          </p>
        )}
      </Card>

      {alerts.isLoading && <Loading label="Loading alerts" />}
      {alerts.data && alerts.data.length === 0 && (
        <EmptyState title="No alerts yet">Create one above.</EmptyState>
      )}

      <div className="space-y-3">
        {(alerts.data ?? []).map((a) => (
          <Card key={a.id}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{a.name}</span>
              <Badge tone={a.enabled ? "low" : "neutral"}>{a.enabled ? "active" : "paused"}</Badge>
            </div>
            <p className="mt-1 text-sm text-ink-500">
              {a.symbol} {a.operator} {formatInr(a.threshold)} via {a.channel}
            </p>
            {a.lastTriggeredAt && (
              <p className="mt-1 text-xs text-ink-400">Last triggered {formatDate(a.lastTriggeredAt)}</p>
            )}
            <button
              onClick={() => remove.mutate(a.id)}
              className="mt-3 rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-600"
            >
              Delete
            </button>
          </Card>
        ))}
      </div>
    </div>
  );
}
