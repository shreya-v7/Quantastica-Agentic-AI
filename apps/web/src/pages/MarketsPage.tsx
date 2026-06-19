import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { Card, PageHeader, Stat } from "../components/ui";
import { ErrorState } from "../components/states";
import { formatInr } from "../lib/format";
import type { Candle, Quote } from "../lib/domain";

const RANGES = ["1d", "5d", "1mo", "6mo", "1y", "5y"];

export function MarketsPage() {
  const [symbol, setSymbol] = useState("RELIANCE.NS");
  const [range, setRange] = useState("1mo");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [candles, setCandles] = useState<Candle[]>([]);

  const load = useMutation({
    mutationFn: async (sym: string) => {
      const [q, c] = await Promise.all([api.quote(sym), api.candles(sym, range)]);
      return { q, c };
    },
    onSuccess: ({ q, c }) => {
      setQuote(q);
      setCandles(c);
    },
  });

  return (
    <div>
      <PageHeader
        title="Markets"
        subtitle="Live NSE/BSE quotes and candles. Symbols are exchange qualified (RELIANCE.NS, TCS.BO)."
      />

      <form
        onSubmit={(e) => {
          e.preventDefault();
          load.mutate(symbol.trim().toUpperCase());
        }}
        className="mb-6 flex flex-wrap gap-3"
      >
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="rounded-lg border border-ink-200 px-3 py-2 text-sm uppercase"
          placeholder="RELIANCE.NS"
        />
        <select
          value={range}
          onChange={(e) => setRange(e.target.value)}
          className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
        >
          {RANGES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={load.isPending}
          className="rounded-lg bg-brand-600 px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {load.isPending ? "Loading" : "Load"}
        </button>
      </form>

      {load.error && <ErrorState message={(load.error as Error).message} />}

      {quote && (
        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3">
          <Stat label={quote.symbol} value={formatInr(quote.price)} hint="Last price" />
          <Stat label="Currency" value={quote.currency} />
          <Stat label="As of" value={new Date(quote.timestamp).toLocaleString("en-IN")} />
        </div>
      )}

      {candles.length > 0 && (
        <Card>
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={candles}>
              <defs>
                <linearGradient id="close" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="timestamp"
                tickFormatter={(t) => new Date(t).toLocaleDateString("en-IN")}
                tick={{ fontSize: 11 }}
                minTickGap={40}
              />
              <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} width={70} />
              <Tooltip
                formatter={(value) => formatInr(Number(value))}
                labelFormatter={(t) => new Date(String(t)).toLocaleString("en-IN")}
              />
              <Area type="monotone" dataKey="close" stroke="#4f46e5" fill="url(#close)" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
