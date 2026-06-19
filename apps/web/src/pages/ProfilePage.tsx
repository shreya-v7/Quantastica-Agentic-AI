import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Card, PageHeader, Badge } from "../components/ui";
import { ErrorState, Loading } from "../components/states";
import { formatInr } from "../lib/format";

export function ProfilePage() {
  const queryClient = useQueryClient();
  const profile = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["profile"] });
  const saveIncome = useMutation({ mutationFn: api.setIncome, onSuccess: invalidate });
  const addGoal = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.addProfileItem("goals", payload),
    onSuccess: invalidate,
  });
  const removeGoal = useMutation({
    mutationFn: (id: string) => api.deleteProfileItem("goals", id),
    onSuccess: invalidate,
  });

  const n = (v: FormDataEntryValue | null) => Number(v ?? 0);

  if (profile.isLoading) return <Loading label="Loading profile" />;
  if (profile.error) return <ErrorState message={(profile.error as Error).message} />;
  const p = profile.data;
  if (!p) return null;

  return (
    <div>
      <PageHeader
        title="Financial profile"
        subtitle="Your complete picture: income, assets, debts, and goals. Drives tax and planning answers."
      />

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Card>
          <p className="text-sm text-ink-500">Net worth</p>
          <p className="mt-1 text-2xl font-semibold">{p.netWorth.netWorthDisplay}</p>
        </Card>
        <Card>
          <p className="text-sm text-ink-500">Assets</p>
          <p className="mt-1 text-2xl font-semibold">{formatInr(p.netWorth.assetsInr)}</p>
        </Card>
        <Card>
          <p className="text-sm text-ink-500">Liabilities</p>
          <p className="mt-1 text-2xl font-semibold">{formatInr(p.netWorth.liabilitiesInr)}</p>
        </Card>
      </div>

      <Card className="mb-6">
        <h3 className="mb-3 font-semibold">Income</h3>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            saveIncome.mutate({
              basicSalary: n(f.get("basicSalary")),
              hraReceived: n(f.get("hraReceived")),
              specialAllowance: n(f.get("specialAllowance")),
              otherIncome: n(f.get("otherIncome")),
              rentPaid: n(f.get("rentPaid")),
              metro: f.get("metro") === "on",
            });
          }}
          className="grid gap-3 md:grid-cols-3"
        >
          <input name="basicSalary" type="number" defaultValue={p.income.basicSalary} placeholder="Basic salary" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="hraReceived" type="number" defaultValue={p.income.hraReceived} placeholder="HRA received" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="specialAllowance" type="number" defaultValue={p.income.specialAllowance} placeholder="Special allowance" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="otherIncome" type="number" defaultValue={p.income.otherIncome} placeholder="Other income" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="rentPaid" type="number" defaultValue={p.income.rentPaid} placeholder="Annual rent paid" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <label className="flex items-center gap-2 text-sm">
            <input name="metro" type="checkbox" defaultChecked={p.income.metro} /> Metro city
          </label>
          <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white md:col-span-3">
            Save income
          </button>
        </form>
      </Card>

      <Card className="mb-6">
        <h3 className="mb-3 font-semibold">Goals</h3>
        <div className="space-y-3">
          {p.goals.map((g) => (
            <div key={g.id} className="rounded-lg border border-ink-100 p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">{g.name}</span>
                <Badge tone={g.priority === "high" ? "high" : "neutral"}>{g.priority}</Badge>
              </div>
              <p className="mt-1 text-sm text-ink-500">
                {formatInr(g.savedInr)} of {formatInr(g.targetInr)} by {g.targetDate}
              </p>
              <div className="mt-2 h-2 w-full rounded-full bg-ink-100">
                <div
                  className="h-2 rounded-full bg-brand-600"
                  style={{ width: `${Math.round(g.progress * 100)}%` }}
                />
              </div>
              <button
                onClick={() => removeGoal.mutate(g.id)}
                className="mt-2 text-xs text-red-600"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            addGoal.mutate({
              name: f.get("name"),
              targetInr: n(f.get("targetInr")),
              targetDate: String(f.get("targetDate")),
              priority: f.get("priority"),
              savedInr: n(f.get("savedInr")),
            });
            e.currentTarget.reset();
          }}
          className="mt-4 grid gap-3 md:grid-cols-5"
        >
          <input name="name" placeholder="Goal name" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="targetInr" type="number" placeholder="Target" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <input name="targetDate" type="date" className="rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          <select name="priority" className="rounded-lg border border-ink-200 px-3 py-2 text-sm">
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Add goal
          </button>
        </form>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h3 className="mb-3 font-semibold">Retirement and savings</h3>
          {p.retirementAccounts.map((r) => (
            <p key={r.id} className="text-sm text-ink-500">
              {r.kind.toUpperCase()}: {formatInr(r.balanceInr)}
            </p>
          ))}
          {p.deposits.map((d) => (
            <p key={d.id} className="text-sm text-ink-500">
              {d.kind.toUpperCase()} {d.institution}: {formatInr(d.principalInr)}
            </p>
          ))}
        </Card>
        <Card>
          <h3 className="mb-3 font-semibold">Debts</h3>
          {p.debts.length === 0 && <p className="text-sm text-ink-400">No debts.</p>}
          {p.debts.map((d) => (
            <p key={d.id} className="text-sm text-ink-500">
              {d.loanType} ({d.lender}): {formatInr(d.principalOutstandingInr)} at{" "}
              {(d.rate * 100).toFixed(2)}%
            </p>
          ))}
        </Card>
      </div>
    </div>
  );
}
