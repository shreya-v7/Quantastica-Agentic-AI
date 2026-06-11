import { Link, useParams } from "react-router-dom";
import { usePortfolio } from "../hooks/useApi";
import { Card, PageHeader, Stat } from "../components/ui";
import { ErrorState, Loading } from "../components/states";
import { AllocationChart } from "../components/AllocationChart";
import { formatCurrency, formatPercent } from "../lib/format";

export function PortfolioDetailPage() {
  const { id = "" } = useParams();
  const { data, isLoading, error } = usePortfolio(id);

  if (isLoading) return <Loading label="Loading portfolio" />;
  if (error) return <ErrorState message={(error as Error).message} />;
  if (!data) return <ErrorState message="Portfolio not found" />;

  const { portfolio, holdings, metrics } = data;
  const currency = portfolio.baseCurrency;

  return (
    <div>
      <PageHeader title={portfolio.name} subtitle={`${holdings.length} holdings · ${currency}`} />
      <div className="mb-6 flex">
        <Link to="/portfolios" className="text-sm text-brand-600">
          Back to portfolios
        </Link>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Total value" value={formatCurrency(metrics.totalValue, currency)} />
        <Stat label="Cost basis" value={formatCurrency(metrics.totalCostBasis, currency)} />
        <Stat
          label="Unrealized gain"
          value={formatCurrency(metrics.unrealizedGain, currency)}
          hint={formatPercent(metrics.unrealizedGainPct)}
        />
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-semibold">Sector allocation</h2>
          <AllocationChart data={metrics.sectorAllocation} />
        </Card>
        <Card>
          <h2 className="mb-3 font-semibold">Asset class allocation</h2>
          <AllocationChart data={metrics.assetClassAllocation} />
        </Card>
      </div>

      <Card>
        <h2 className="mb-3 font-semibold">Holdings</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-ink-400">
                <th className="py-2">Symbol</th>
                <th>Sector</th>
                <th className="text-right">Value</th>
                <th className="text-right">Weight</th>
                <th className="text-right">Unrealized</th>
              </tr>
            </thead>
            <tbody>
              {metrics.positions.map((pos) => (
                <tr key={pos.symbol} className="border-t border-ink-100">
                  <td className="py-2 font-medium">{pos.symbol}</td>
                  <td className="text-ink-500">{pos.name}</td>
                  <td className="text-right">{formatCurrency(pos.value, currency)}</td>
                  <td className="text-right">{formatPercent(pos.weight)}</td>
                  <td className={`text-right ${pos.unrealizedGain >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                    {formatPercent(pos.unrealizedGainPct)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
