import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Card, PageHeader, Stat, Badge } from "../components/ui";
import { ErrorState } from "../components/states";
import { formatInr } from "../lib/format";
import type { SipResult, SimulationResult, TaxComparison } from "../lib/domain";

const TABS = ["Tax regime", "SIP goal", "Projection"] as const;
type Tab = (typeof TABS)[number];

export function GoalsPage() {
  const [tab, setTab] = useState<Tab>("Tax regime");
  return (
    <div>
      <PageHeader
        title="Planning"
        subtitle="Deterministic Indian tax, SIP, and projection calculators. The numbers are computed, not estimated by a model."
      />
      <div className="mb-6 flex gap-2">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-brand-600 text-white" : "border border-ink-200 text-ink-600"
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === "Tax regime" && <TaxPanel />}
      {tab === "SIP goal" && <SipPanel />}
      {tab === "Projection" && <ProjectionPanel />}
    </div>
  );
}

function num(v: FormDataEntryValue | null): number {
  return Number(v ?? 0);
}

function TaxPanel() {
  const [result, setResult] = useState<TaxComparison | null>(null);
  const run = useMutation({ mutationFn: api.taxCompare, onSuccess: setResult });

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            run.mutate({
              basicSalary: num(f.get("basicSalary")),
              hraReceived: num(f.get("hraReceived")),
              rentPaid: num(f.get("rentPaid")),
              deduction80C: num(f.get("deduction80C")),
              healthPremiumSelf: num(f.get("healthPremiumSelf")),
              nps80Ccd1B: num(f.get("nps80Ccd1B")),
              homeLoanInterest: num(f.get("homeLoanInterest")),
            });
          }}
          className="space-y-3"
        >
          {[
            ["basicSalary", "Basic salary"],
            ["hraReceived", "HRA received"],
            ["rentPaid", "Rent paid"],
            ["deduction80C", "80C investments"],
            ["healthPremiumSelf", "80D health premium"],
            ["nps80Ccd1B", "NPS 80CCD(1B)"],
            ["homeLoanInterest", "Home loan interest"],
          ].map(([name, label]) => (
            <label key={name} className="block text-sm">
              <span className="text-ink-600">{label}</span>
              <input
                name={name}
                type="number"
                defaultValue={0}
                className="mt-1 w-full rounded-lg border border-ink-200 px-3 py-2"
              />
            </label>
          ))}
          <button className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Compare regimes
          </button>
        </form>
      </Card>
      <div className="space-y-4">
        {run.error && <ErrorState message={(run.error as Error).message} />}
        {result && (
          <>
            <Card>
              <div className="flex items-center justify-between">
                <span className="font-semibold">Recommended</span>
                <Badge tone="low">{result.recommended} regime</Badge>
              </div>
              <p className="mt-2 text-sm text-ink-500">
                Saves {result.savingDisplay} versus the other regime (AY {result.assessmentYear}).
              </p>
            </Card>
            <div className="grid grid-cols-2 gap-4">
              <Stat label="Old regime tax" value={formatInr(result.oldRegime.totalTax)} />
              <Stat label="New regime tax" value={formatInr(result.newRegime.totalTax)} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SipPanel() {
  const [result, setResult] = useState<SipResult | null>(null);
  const run = useMutation({ mutationFn: api.sip, onSuccess: setResult });
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            run.mutate({
              targetInr: num(f.get("targetInr")),
              years: num(f.get("years")),
              annualReturn: num(f.get("annualReturn")) / 100,
              annualStepUp: num(f.get("annualStepUp")) / 100,
            });
          }}
          className="space-y-3"
        >
          <Field name="targetInr" label="Target corpus (INR)" def={20000000} />
          <Field name="years" label="Years" def={15} />
          <Field name="annualReturn" label="Expected return (%)" def={12} />
          <Field name="annualStepUp" label="Annual step-up (%)" def={10} />
          <button className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Compute SIP
          </button>
        </form>
      </Card>
      <div className="space-y-4">
        {run.error && <ErrorState message={(run.error as Error).message} />}
        {result && (
          <>
            <Stat label="Required monthly SIP" value={result.monthlySipDisplay} />
            {result.stepUpFirstMonthSipDisplay && (
              <Stat
                label="Step-up first-month SIP"
                value={result.stepUpFirstMonthSipDisplay}
                hint="Lower start, grows each year"
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

function ProjectionPanel() {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const run = useMutation({ mutationFn: api.simulate, onSuccess: setResult });
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            run.mutate({
              monthlySip: num(f.get("monthlySip")),
              years: num(f.get("years")),
              annualReturn: num(f.get("annualReturn")) / 100,
              annualVolatility: num(f.get("annualVolatility")) / 100,
            });
          }}
          className="space-y-3"
        >
          <Field name="monthlySip" label="Monthly SIP (INR)" def={25000} />
          <Field name="years" label="Years" def={10} />
          <Field name="annualReturn" label="Expected return (%)" def={12} />
          <Field name="annualVolatility" label="Volatility (%)" def={18} />
          <button className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white">
            Run Monte Carlo
          </button>
        </form>
      </Card>
      <div className="space-y-4">
        {run.error && <ErrorState message={(run.error as Error).message} />}
        {result && (
          <div className="grid grid-cols-3 gap-3">
            <Stat label="Pessimistic (P10)" value={result.bandsDisplay.p10} />
            <Stat label="Median (P50)" value={result.bandsDisplay.p50} />
            <Stat label="Optimistic (P90)" value={result.bandsDisplay.p90} />
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ name, label, def }: { name: string; label: string; def: number }) {
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
