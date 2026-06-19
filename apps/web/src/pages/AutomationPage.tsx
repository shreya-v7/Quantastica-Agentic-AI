import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { usePortfolios } from "../hooks/useApi";
import { Card, PageHeader, Badge } from "../components/ui";
import { EmptyState, ErrorState, Loading } from "../components/states";
import { formatInr } from "../lib/format";

export function AutomationPage() {
  const portfolios = usePortfolios();
  const queryClient = useQueryClient();
  const rules = useQuery({ queryKey: ["rules"], queryFn: api.listRules });
  const [master, setMaster] = useState(false);

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["rules"] });
  const create = useMutation({ mutationFn: api.createRule, onSuccess: invalidate });
  const toggle = useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      api.toggleRule(id, enabled),
    onSuccess: invalidate,
  });
  const remove = useMutation({ mutationFn: api.deleteRule, onSuccess: invalidate });
  const setMasterSwitch = useMutation({
    mutationFn: api.automationMaster,
    onSuccess: (_d, enabled) => setMaster(enabled),
  });

  const n = (v: FormDataEntryValue | null) => Number(v ?? 0);

  return (
    <div>
      <PageHeader
        title="Automation"
        subtitle="Rules fire only when the master switch is on and stay within server-enforced hard caps you cannot raise."
      />

      <div className="mb-6 flex items-center justify-between rounded-xl border border-ink-200 bg-white px-4 py-3">
        <span className="text-sm text-ink-600">
          Account automation {master ? "enabled" : "disabled"}
        </span>
        <button
          onClick={() => setMasterSwitch.mutate(!master)}
          className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white"
        >
          {master ? "Disable" : "Enable"} automation
        </button>
      </div>

      <Card className="mb-6">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            create.mutate({
              name: f.get("name"),
              portfolioId: f.get("portfolioId"),
              trigger: {
                symbol: String(f.get("symbol")).toUpperCase(),
                operator: f.get("operator"),
                price: n(f.get("price")),
              },
              action: { side: f.get("side"), quantity: n(f.get("quantity")), orderType: "market" },
              maxNotionalInr: n(f.get("maxNotionalInr")),
            });
          }}
          className="grid gap-3 md:grid-cols-2"
        >
          <input name="name" placeholder="Rule name" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <select name="portfolioId" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            {(portfolios.data ?? []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <input name="symbol" placeholder="RELIANCE.NS" className="rounded-lg border border-ink-200 px-3 py-2 text-sm uppercase" />
          <select name="operator" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            <option value="below">Price below</option>
            <option value="above">Price above</option>
          </select>
          <input name="price" type="number" step="any" placeholder="Trigger price" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <select name="side" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          <input name="quantity" type="number" step="any" placeholder="Quantity" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="maxNotionalInr" type="number" step="any" placeholder="Max notional (INR)" defaultValue={100000} className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white md:col-span-2">
            Create rule
          </button>
        </form>
        {create.error && (
          <p className="mt-3">
            <ErrorState message={(create.error as Error).message} />
          </p>
        )}
      </Card>

      {rules.isLoading && <Loading label="Loading rules" />}
      {rules.data && rules.data.length === 0 && (
        <EmptyState title="No automation rules">Create one above.</EmptyState>
      )}

      <div className="space-y-3">
        {(rules.data ?? []).map((r) => (
          <Card key={r.id}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{r.name}</span>
              <Badge tone={r.enabled ? "low" : "neutral"}>{r.enabled ? "enabled" : "paused"}</Badge>
            </div>
            <p className="mt-1 text-sm text-ink-500">
              When {r.trigger.symbol} is {r.trigger.operator} {formatInr(r.trigger.price)}, {r.action.side}{" "}
              {r.action.quantity}. Cap {formatInr(r.maxNotionalInr)}.
            </p>
            <p className="mt-1 text-xs text-ink-400">
              Fired {r.executionsToday} times today ({formatInr(r.dayNotionalInr)}).
            </p>
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => toggle.mutate({ id: r.id, enabled: !r.enabled })}
                className="rounded-lg border border-ink-200 px-3 py-1.5 text-sm text-ink-600"
              >
                {r.enabled ? "Pause" : "Resume"}
              </button>
              <button
                onClick={() => remove.mutate(r.id)}
                className="rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-600"
              >
                Delete
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
