/** Canonical insight metrics — always produced by `generate_insights` on the backend. */
export type FinancialSummary = {
  netWorth: number;
  riskExposure: number;
  debtLoad: number;
};

export type ChartPoint = {
  name: string;
  value: number;
};

/**
 * UI dashboard payload — all numeric fields computed server-side from a snapshot + insight engine.
 * UI must not re-derive net worth or summary metrics.
 */
export type DashboardPayload = {
  version: string;
  summary: FinancialSummary;
  cash: number;
  investmentsTotal: number;
  debtTotal: number;
  chart: ChartPoint[];
  insightSummary: string;
  /** Server-evaluated; do not recompute in UI. */
  showRefinanceCta: boolean;
};

export type InsightsResponse = {
  userId: string;
  insights: FinancialSummary;
};

export type InsightHighlight = {
  id: string;
  severity: "info" | "watch" | "action";
  title: string;
  body: string;
  actionLabel?: string;
};

export type InsightHighlightsResponse = {
  version: string;
  highlights: InsightHighlight[];
};
