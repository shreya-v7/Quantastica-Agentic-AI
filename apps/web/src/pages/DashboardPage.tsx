import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, type DeskQueue, type DeskException } from "../lib/api";
import { Badge, Card, PageHeader, PrimaryButton, Stat } from "../components/ui";
import { ErrorState, Loading } from "../components/states";
import { formatInr } from "../lib/format";
import { IngestPanel } from "../components/IngestPanel";
import { VoiceBar } from "../components/VoiceBar";

function Trace({ row }: { row: DeskException }) {
  return (
    <div className="mt-4 space-y-3 border-t border-ink-200 pt-4">
      <p className="font-mono text-[10px] uppercase tracking-label text-pine-500">trace</p>
      <p className="text-xs text-ink-500">
        {row.calculator} {row.calculatorVersion} · metrics {row.metricIds.join(", ")}
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <pre className="overflow-auto bg-ink-50 p-3 font-mono text-[11px] text-ink-700">
          {JSON.stringify(row.inputs, null, 2)}
        </pre>
        <pre className="overflow-auto bg-ink-50 p-3 font-mono text-[11px] text-ink-700">
          {JSON.stringify(row.outputs, null, 2)}
        </pre>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const queryClient = useQueryClient();
  const households = useQuery({ queryKey: ["desk-households"], queryFn: api.listHouseholds });
  const [householdId, setHouseholdId] = useState("hh_mehta");
  const [openId, setOpenId] = useState<string | null>(null);
  const queue = useQuery({
    queryKey: ["desk-queue", householdId],
    queryFn: () => api.deskQueue(householdId),
    enabled: Boolean(householdId),
  });

  const setQty = useMutation({
    mutationFn: ({ lotId, quantity }: { lotId: string; quantity: number }) =>
      api.setLotQuantity(householdId, lotId, quantity),
    onSuccess: (data) => {
      queryClient.setQueryData(["desk-queue", householdId], data);
    },
  });

  if (households.isLoading) return <Loading label="Loading households" />;
  if (households.error) return <ErrorState message={(households.error as Error).message} />;

  const data: DeskQueue | undefined = queue.data;
  const rows = data?.exceptions ?? [];

  return (
    <div>
      <PageHeader
        title="Desk"
        subtitle="Exceptions on the live book. Every rupee is from a calculator. Not advice."
      />
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <label className="font-mono text-[11px] uppercase tracking-label text-ink-400">
          Household
        </label>
        <select
          className="border border-ink-200 bg-paper-50 px-3 py-2 text-sm"
          value={householdId}
          onChange={(e) => {
            setHouseholdId(e.target.value);
            setOpenId(null);
          }}
        >
          {(households.data ?? []).map((h) => (
            <option key={h.id} value={h.id}>
              {h.name}
            </option>
          ))}
        </select>
      </div>

      {queue.isLoading && <Loading label="Computing queue" />}
      {queue.error && <ErrorState message={(queue.error as Error).message} />}

      {data && (
        <>
          <VoiceBar
            householdId={householdId}
            onQueue={() => queryClient.invalidateQueries({ queryKey: ["desk-queue", householdId] })}
          />
          <IngestPanel
            householdId={householdId}
            onQueue={(next) => queryClient.setQueryData(["desk-queue", householdId], next)}
          />
          <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Stat label="Book" value={formatInr(data.household.totalMarket)} />
            <Stat label="Open exceptions" value={String(rows.length)} />
            <Stat label="As of" value={data.household.asOf} />
          </div>

          <Card className="mb-6">
            <h2 className="mb-4 font-semibold text-ink-900">Exception queue</h2>
            {rows.length === 0 ? (
              <p className="text-sm text-ink-500">No exceptions on this book.</p>
            ) : (
              <ul className="divide-y divide-ink-200">
                {rows.map((row) => (
                  <li key={row.id} className="py-4">
                    <button
                      type="button"
                      className="flex w-full items-start justify-between gap-4 text-left"
                      onClick={() => setOpenId(openId === row.id ? null : row.id)}
                    >
                      <div>
                        <div className="mb-1 flex items-center gap-2">
                          <Badge tone={row.severity}>{row.ruleId}</Badge>
                          {row.dueDate && (
                            <span className="font-mono text-[10px] text-ink-400">
                              due {row.dueDate}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-ink-800">{row.title}</p>
                      </div>
                      <p className="shrink-0 font-mono text-sm tabular-nums text-pine-500">
                        {formatInr(row.rupeeDelta)}
                      </p>
                    </button>
                    {openId === row.id && <Trace row={row} />}
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card>
            <h2 className="mb-4 font-semibold text-ink-900">Lots</h2>
            <p className="mb-4 text-xs text-ink-500">
              Change a quantity. The book appends an event and the queue recomputes.
            </p>
            <ul className="space-y-3">
              {data.lots.map((lot) => (
                <li
                  key={lot.id}
                  className="flex flex-wrap items-center justify-between gap-3 border-b border-ink-200 pb-3 text-sm"
                >
                  <div>
                    <p className="font-medium">{lot.symbol}</p>
                    <p className="text-xs text-ink-400">
                      {lot.sector} · {formatInr(lot.marketValue)}
                    </p>
                  </div>
                  <form
                    className="flex items-center gap-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      const form = new FormData(e.currentTarget);
                      const quantity = Number(form.get("quantity"));
                      setQty.mutate({ lotId: lot.id, quantity });
                    }}
                  >
                    <input
                      name="quantity"
                      defaultValue={lot.quantity}
                      type="number"
                      min={0}
                      step="any"
                      className="w-28 border border-ink-200 bg-paper-50 px-2 py-1 font-mono text-sm"
                    />
                    <PrimaryButton type="submit" className="px-3 py-1.5 text-xs" disabled={setQty.isPending}>
                      Apply
                    </PrimaryButton>
                  </form>
                </li>
              ))}
            </ul>
          </Card>
        </>
      )}
    </div>
  );
}
