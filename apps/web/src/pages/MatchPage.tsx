import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Card, PageHeader, Badge } from "../components/ui";
import { ErrorState } from "../components/states";
import { formatPercent } from "../lib/format";
import type { InsuranceMatch, LoanMatch } from "../lib/domain";

export function MatchPage() {
  const [kind, setKind] = useState<"loan" | "insurance">("loan");
  return (
    <div>
      <PageHeader
        title="Match"
        subtitle="Deterministic loan and insurance matching from a seeded Indian catalog. Each result shows why it qualifies."
      />
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setKind("loan")}
          className={`rounded-lg px-4 py-2 text-sm font-medium ${
            kind === "loan" ? "bg-brand-600 text-white" : "border border-ink-200 text-ink-600"
          }`}
        >
          Loans
        </button>
        <button
          onClick={() => setKind("insurance")}
          className={`rounded-lg px-4 py-2 text-sm font-medium ${
            kind === "insurance" ? "bg-brand-600 text-white" : "border border-ink-200 text-ink-600"
          }`}
        >
          Insurance
        </button>
      </div>
      {kind === "loan" ? <LoanPanel /> : <InsurancePanel />}
    </div>
  );
}

const n = (v: FormDataEntryValue | null) => Number(v ?? 0);

function LoanPanel() {
  const [matches, setMatches] = useState<LoanMatch[]>([]);
  const run = useMutation({ mutationFn: api.matchLoans, onSuccess: setMatches });
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            run.mutate({
              loanType: f.get("loanType"),
              amountInr: n(f.get("amountInr")),
              tenureYears: n(f.get("tenureYears")),
              monthlyIncomeInr: n(f.get("monthlyIncomeInr")),
              existingEmiInr: n(f.get("existingEmiInr")),
              propertyValueInr: n(f.get("propertyValueInr")) || undefined,
            });
          }}
          className="space-y-3"
        >
          <label className="block text-sm">
            <span className="text-ink-600">Loan type</span>
            <select
              name="loanType"
              className="mt-1 w-full rounded-lg border border-ink-200 px-3 py-2"
            >
              <option value="home">Home</option>
              <option value="personal">Personal</option>
              <option value="car">Car</option>
            </select>
          </label>
          <NumField name="amountInr" label="Loan amount" def={5000000} />
          <NumField name="tenureYears" label="Tenure (years)" def={20} />
          <NumField name="monthlyIncomeInr" label="Monthly income" def={200000} />
          <NumField name="existingEmiInr" label="Existing EMI" def={0} />
          <NumField name="propertyValueInr" label="Property value (home only)" def={7000000} />
          <button className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Find loans
          </button>
        </form>
      </Card>
      <div className="space-y-3">
        {run.error && <ErrorState message={(run.error as Error).message} />}
        {matches.map((m) => (
          <Card key={m.productId}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{m.name}</span>
              <Badge tone={m.eligible ? "low" : "high"}>
                {m.eligible ? "Eligible" : "Not eligible"}
              </Badge>
            </div>
            <p className="text-xs text-ink-400">{m.provider}</p>
            <div className="mt-2 flex gap-6 text-sm">
              <span>Rate {formatPercent(m.indicativeRate, 2)}</span>
              <span>EMI {m.emiDisplay}</span>
              <span>FOIR {formatPercent(m.foirAfter, 0)}</span>
            </div>
            <ul className="mt-2 list-inside list-disc text-xs text-ink-500">
              {m.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
}

function InsurancePanel() {
  const [matches, setMatches] = useState<InsuranceMatch[]>([]);
  const run = useMutation({ mutationFn: api.matchInsurance, onSuccess: setMatches });
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            run.mutate({
              insuranceType: f.get("insuranceType"),
              coverInr: n(f.get("coverInr")),
              age: n(f.get("age")),
              smoker: f.get("smoker") === "on",
              familyFloater: f.get("familyFloater") === "on",
            });
          }}
          className="space-y-3"
        >
          <label className="block text-sm">
            <span className="text-ink-600">Type</span>
            <select
              name="insuranceType"
              className="mt-1 w-full rounded-lg border border-ink-200 px-3 py-2"
            >
              <option value="term">Term life</option>
              <option value="health">Health</option>
            </select>
          </label>
          <NumField name="coverInr" label="Cover" def={10000000} />
          <NumField name="age" label="Age" def={35} />
          <label className="flex items-center gap-2 text-sm text-ink-600">
            <input type="checkbox" name="smoker" /> Smoker (term)
          </label>
          <label className="flex items-center gap-2 text-sm text-ink-600">
            <input type="checkbox" name="familyFloater" /> Family floater (health)
          </label>
          <button className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Find cover
          </button>
        </form>
      </Card>
      <div className="space-y-3">
        {run.error && <ErrorState message={(run.error as Error).message} />}
        {matches.map((m) => (
          <Card key={m.productId}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{m.name}</span>
              <Badge tone={m.eligible ? "low" : "high"}>
                {m.eligible ? "Eligible" : "Not eligible"}
              </Badge>
            </div>
            <p className="text-xs text-ink-400">{m.provider}</p>
            <p className="mt-2 text-sm">Annual premium {m.premiumDisplay}</p>
            <ul className="mt-2 list-inside list-disc text-xs text-ink-500">
              {m.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
}

function NumField({ name, label, def }: { name: string; label: string; def: number }) {
  return (
    <label className="block text-sm">
      <span className="text-ink-600">{label}</span>
      <input
        name={name}
        type="number"
        step="any"
        defaultValue={def}
        className="mt-1 w-full rounded-lg border border-ink-200 px-3 py-2"
      />
    </label>
  );
}
