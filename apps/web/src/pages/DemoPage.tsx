import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Card, PageHeader, PrimaryButton } from "../components/ui";
import { ErrorState } from "../components/states";

export function DemoPage() {
  const run = useMutation({ mutationFn: api.runDemo });
  const data = run.data as
    | {
        steps?: string[];
        speech?: string;
        beforeCount?: number;
        afterCount?: number;
        form16?: string;
        bonus?: string;
      }
    | undefined;

  return (
    <div>
      <PageHeader
        title="3-minute demo"
        subtitle="Seeds Mehta, drops the Form 16 fixture, applies a 12 lakh bonus, and reads the queue. Re-seed afterwards if you need a clean book."
      />
      <PrimaryButton type="button" onClick={() => run.mutate()} disabled={run.isPending}>
        {run.isPending ? "Running..." : "Run scripted demo"}
      </PrimaryButton>
      {run.error && <ErrorState message={(run.error as Error).message} />}
      {data && (
        <Card className="mt-6">
          <ol className="list-decimal space-y-2 pl-5 text-sm text-ink-700">
            {(data.steps ?? []).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
          <p className="mt-4 font-mono text-xs text-ink-500">
            Form 16 {data.form16} · bonus {data.bonus} · exceptions {data.beforeCount} →{" "}
            {data.afterCount}
          </p>
          {data.speech && <p className="mt-4 text-sm text-ink-800">{data.speech}</p>}
          <Link to="/desk" className="mt-4 inline-block text-sm text-pine-500">
            Open the desk
          </Link>
        </Card>
      )}
    </div>
  );
}
