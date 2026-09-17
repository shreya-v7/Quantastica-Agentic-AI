import { Link } from "react-router-dom";
import { usePortfolios } from "../hooks/useApi";
import { Card, PageHeader } from "../components/ui";
import { EmptyState, ErrorState, Loading } from "../components/states";

export function PortfoliosPage() {
  const { data, isLoading, error } = usePortfolios();

  if (isLoading) return <Loading label="Loading portfolios" />;
  if (error) return <ErrorState message={(error as Error).message} />;
  if (!data || data.length === 0) {
    return <EmptyState title="No portfolios">Load the seed data to get started.</EmptyState>;
  }

  return (
    <div>
      <PageHeader title="Portfolios" subtitle="Holdings, allocation, and computed metrics." />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {data.map((p) => (
          <Link key={p.id} to={`/portfolios/${p.id}`}>
            <Card className="transition hover:border-brand-500">
              <p className="font-semibold text-ink-900">{p.name}</p>
              <p className="mt-1 text-sm text-ink-500">
                {p.baseCurrency} · created {new Date(p.createdAt).toLocaleDateString()}
              </p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
