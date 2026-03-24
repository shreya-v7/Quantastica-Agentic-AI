import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export type ChartPoint = { name: string; value: number };

type ChartProps = {
  data: ChartPoint[];
  dataKey?: string;
  /** Unique id for SVG gradient defs */
  gradientId?: string;
  className?: string;
};

const defaultFormatter = (v: number) =>
  new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
    v,
  );

export function Chart({ data, dataKey = "value", gradientId = "fi-area-blue", className = "" }: ChartProps) {
  return (
    <div className={`h-[260px] w-full ${className}`.trim()}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(var(--chart-1))" stopOpacity={0.45} />
              <stop offset="100%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 8" stroke="hsl(var(--border) / 0.5)" vertical={false} />
          <XAxis
            dataKey="name"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
            tickFormatter={(v) => `${Math.round(v / 1000)}k`}
            width={40}
          />
          <Tooltip
            contentStyle={{
              borderRadius: "12px",
              border: "1px solid hsl(var(--border))",
              background: "hsl(var(--card))",
              color: "hsl(var(--card-foreground))",
              boxShadow: "0 12px 32px hsl(0 0% 0% / 0.12)",
            }}
            formatter={(value: number | string) => [defaultFormatter(Number(value)), "Portfolio"]}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke="hsl(var(--chart-1))"
            strokeWidth={2}
            fill={`url(#${gradientId})`}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0, fill: "hsl(var(--chart-1))" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
