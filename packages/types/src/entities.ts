import { z } from "zod";
import { assetClassSchema, transactionTypeSchema } from "./common.js";

export const holdingSchema = z.object({
  id: z.string(),
  portfolioId: z.string(),
  symbol: z.string(),
  name: z.string(),
  assetClass: assetClassSchema,
  sector: z.string(),
  quantity: z.number(),
  costBasis: z.number(),
  currentPrice: z.number(),
  seed: z.boolean().default(false),
});
export type Holding = z.infer<typeof holdingSchema>;

export const transactionSchema = z.object({
  id: z.string(),
  portfolioId: z.string(),
  symbol: z.string(),
  type: transactionTypeSchema,
  quantity: z.number(),
  price: z.number(),
  timestamp: z.string(),
  seed: z.boolean().default(false),
});
export type Transaction = z.infer<typeof transactionSchema>;

export const portfolioSchema = z.object({
  id: z.string(),
  name: z.string(),
  baseCurrency: z.string(),
  createdAt: z.string(),
  seed: z.boolean().default(false),
});
export type Portfolio = z.infer<typeof portfolioSchema>;

export const allocationSliceSchema = z.object({
  key: z.string(),
  value: z.number(),
  weight: z.number(),
});
export type AllocationSlice = z.infer<typeof allocationSliceSchema>;

export const positionMetricSchema = z.object({
  symbol: z.string(),
  name: z.string(),
  value: z.number(),
  weight: z.number(),
  costBasis: z.number(),
  unrealizedGain: z.number(),
  unrealizedGainPct: z.number(),
});
export type PositionMetric = z.infer<typeof positionMetricSchema>;

export const portfolioMetricsSchema = z.object({
  portfolioId: z.string(),
  totalValue: z.number(),
  totalCostBasis: z.number(),
  unrealizedGain: z.number(),
  unrealizedGainPct: z.number(),
  positions: z.array(positionMetricSchema),
  sectorAllocation: z.array(allocationSliceSchema),
  assetClassAllocation: z.array(allocationSliceSchema),
  topPositions: z.array(positionMetricSchema),
});
export type PortfolioMetrics = z.infer<typeof portfolioMetricsSchema>;

export const portfolioDetailSchema = z.object({
  portfolio: portfolioSchema,
  holdings: z.array(holdingSchema),
  metrics: portfolioMetricsSchema,
});
export type PortfolioDetail = z.infer<typeof portfolioDetailSchema>;
