import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Card, PageHeader, Stat } from "../components/ui";
import { ErrorState, Loading } from "../components/states";
import { formatInr } from "../lib/format";

export function MetricsPage() {
  const metrics = useQuery({ queryKey: ["desk-metrics"], queryFn: api.deskMetrics });
  if (metrics.isLoading) return <Loading label="Loading metrics" />;
  if (metrics.error) return <ErrorState message={(metrics.error as Error).message} />;
  const data = metrics.data;
  if (!data) return <ErrorState message="No metrics" />;

  return (
    <div>
      <PageHeader
        title="Metrics"
        subtitle="Pitch instrumentation. Extraction accuracy and review rate fill in once evals run against synthgen."
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Stat label="Households" value={String(data.households)} />
        <Stat label="Lots" value={String(data.lots)} />
        <Stat label="Documents ingested" value={String(data.documentsIngested)} />
        <Stat label="Open exceptions" value={String(data.exceptionsOpen)} />
        <Stat label="Rupee delta surfaced" value={formatInr(data.rupeeDeltaSurfaced)} />
        <Stat
          label="Review rate"
          value={data.reviewRate === 0 ? "n/a" : `${(data.reviewRate * 100).toFixed(0)}%`}
        />
      </div>
      <Card className="mt-6">
        <p className="text-sm text-ink-500">
          Median time from upload to exception and extraction accuracy stay empty until the
          synthgen eval harness has a live run. The rupee total is the sum of open calculator
          deltas, not an estimate.
        </p>
      </Card>
    </div>
  );
}
