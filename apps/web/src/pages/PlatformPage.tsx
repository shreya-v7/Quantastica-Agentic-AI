import { usePlatform } from "../hooks/useApi";
import { Badge, Card, PageHeader } from "../components/ui";
import { ErrorState, Loading } from "../components/states";

export function PlatformPage() {
  const { data, isLoading, error } = usePlatform();

  if (isLoading) return <Loading label="Loading platform status" />;
  if (error) return <ErrorState message={(error as Error).message} />;
  if (!data) return <ErrorState message="No platform status" />;

  return (
    <div>
      <PageHeader title="Platform" subtitle="Active platform and per-component readiness." />

      <Card className="mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-ink-400">Platform</p>
            <p className="text-lg font-semibold uppercase">{data.platform}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-ink-400">Environment</p>
            <p className="text-lg font-semibold">{data.appEnv}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-ink-400">Status</p>
            <Badge tone={data.ready ? "low" : "high"}>{data.ready ? "ready" : "degraded"}</Badge>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {data.components.map((c) => (
          <Card key={c.name}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold capitalize">{c.name}</p>
                <p className="text-sm text-ink-500">{c.implementation}</p>
              </div>
              <Badge tone={c.ready ? "low" : "high"}>{c.ready ? "ready" : "not configured"}</Badge>
            </div>
            {c.missingEnv.length > 0 && (
              <p className="mt-3 text-xs text-ink-400">
                Missing: {c.missingEnv.join(", ")}
              </p>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
