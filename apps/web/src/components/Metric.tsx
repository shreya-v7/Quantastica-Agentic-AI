import { motion } from "framer-motion";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";

type Trend = "up" | "down" | "neutral";

export type MetricProps = {
  label: string;
  value: string;
  sublabel?: string;
  trend?: Trend;
  trendLabel?: string;
  delay?: number;
};

export function Metric({ label, value, sublabel, trend = "neutral", trendLabel, delay = 0 }: MetricProps) {
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;
  const trendColor =
    trend === "up"
      ? "text-emerald-600 dark:text-emerald-400"
      : trend === "down"
        ? "text-rose-600 dark:text-rose-400"
        : "text-muted-foreground";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
      className="flex flex-col gap-1"
    >
      <p className="text-sm font-medium text-muted-foreground">{label}</p>
      <h2 className="text-3xl font-semibold tracking-tight text-foreground tabular-nums">{value}</h2>
      {(sublabel || trendLabel) && (
        <div className="flex flex-wrap items-center gap-2 text-sm">
          {sublabel && <span className="text-muted-foreground">{sublabel}</span>}
          {trendLabel && (
            <span className={`inline-flex items-center gap-1 font-medium ${trendColor}`}>
              <TrendIcon className="h-3.5 w-3.5" aria-hidden />
              {trendLabel}
            </span>
          )}
        </div>
      )}
    </motion.div>
  );
}
