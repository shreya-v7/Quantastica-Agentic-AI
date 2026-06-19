import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { usePortfolios } from "../hooks/useApi";
import { Card, PageHeader, Badge } from "../components/ui";
import { EmptyState, ErrorState, Loading } from "../components/states";
import { formatInr, formatDate } from "../lib/format";
import type { OrderStatus } from "../lib/domain";

const STATUS_TONE: Record<OrderStatus, string> = {
  pending_approval: "medium",
  approved: "info",
  submitted: "info",
  filled: "low",
  rejected: "high",
  cancelled: "neutral",
};

export function TradesPage() {
  const portfolios = usePortfolios();
  const queryClient = useQueryClient();
  const intents = useQuery({ queryKey: ["intents"], queryFn: api.listIntents });
  const [killed, setKilled] = useState(false);

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["intents"] });
  const create = useMutation({ mutationFn: api.createIntent, onSuccess: invalidate });
  const execute = useMutation({ mutationFn: api.executeIntent, onSuccess: invalidate });
  const cancel = useMutation({ mutationFn: api.cancelIntent, onSuccess: invalidate });
  const kill = useMutation({
    mutationFn: api.killSwitch,
    onSuccess: (r) => setKilled(r.tradingDisabled),
  });

  const n = (v: FormDataEntryValue | null) => Number(v ?? 0);

  return (
    <div>
      <PageHeader
        title="Trades"
        subtitle="Every order is an intent first. Approve to execute. Paper mode fills against live quotes; live trading is gated."
      />

      <div className="mb-6 flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
        <span className="text-sm text-amber-800">
          Kill switch {killed ? "is ON, trading blocked" : "is off"}
        </span>
        <button
          onClick={() => kill.mutate(!killed)}
          className="rounded-lg bg-amber-600 px-3 py-1.5 text-sm font-medium text-white"
        >
          {killed ? "Re-enable trading" : "Disable trading"}
        </button>
      </div>

      <Card className="mb-6">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            create.mutate({
              portfolioId: f.get("portfolioId"),
              symbol: String(f.get("symbol")).toUpperCase(),
              side: f.get("side"),
              quantity: n(f.get("quantity")),
              orderType: "market",
            });
          }}
          className="grid gap-3 md:grid-cols-5"
        >
          <select name="portfolioId" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            {(portfolios.data ?? []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <input
            name="symbol"
            placeholder="RELIANCE.NS"
            defaultValue="RELIANCE.NS"
            className="rounded-lg border border-ink-200 px-3 py-2 text-sm uppercase"
          />
          <select name="side" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          <input
            name="quantity"
            type="number"
            step="any"
            defaultValue={10}
            className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
          />
          <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Create intent
          </button>
        </form>
        {create.error && (
          <p className="mt-3">
            <ErrorState message={(create.error as Error).message} />
          </p>
        )}
      </Card>

      {intents.isLoading && <Loading label="Loading intents" />}
      {intents.error && <ErrorState message={(intents.error as Error).message} />}
      {intents.data && intents.data.length === 0 && (
        <EmptyState title="No intents yet">Create one above to get started.</EmptyState>
      )}

      <div className="space-y-3">
        {(intents.data ?? []).map((it) => (
          <Card key={it.id}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">
                {it.side.toUpperCase()} {it.quantity} {it.symbol}
              </span>
              <Badge tone={STATUS_TONE[it.status]}>{it.status.replace("_", " ")}</Badge>
            </div>
            <div className="mt-1 flex flex-wrap gap-4 text-sm text-ink-500">
              <span>{it.mode} mode</span>
              <span>Notional {formatInr(it.notionalInr)}</span>
              {it.fillPrice != null && <span>Filled at {formatInr(it.fillPrice)}</span>}
              <span>{formatDate(it.updatedAt)}</span>
            </div>
            {it.reason && <p className="mt-1 text-xs text-red-600">{it.reason}</p>}
            {it.status === "pending_approval" && (
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => execute.mutate(it.id)}
                  className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white"
                >
                  Approve &amp; execute
                </button>
                <button
                  onClick={() => cancel.mutate(it.id)}
                  className="rounded-lg border border-ink-200 px-3 py-1.5 text-sm text-ink-600"
                >
                  Cancel
                </button>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
