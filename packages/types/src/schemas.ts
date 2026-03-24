import { z } from "zod";
import { CONTRACT_VERSION } from "./version";

export const CloudProviderSchema = z.enum(["aws", "azure", "gcp"]);

export const FeatureFlagsSchema = z.object({
  cloud: CloudProviderSchema,
  ai: z.boolean(),
  insights: z.boolean(),
});

export const ConfigResponseSchema = z.object({
  version: z.string(),
  flags: FeatureFlagsSchema,
  demo: z.object({
    enabled: z.boolean(),
  }),
});

export const FinancialSummarySchema = z.object({
  netWorth: z.number(),
  riskExposure: z.number(),
  debtLoad: z.number(),
});

export const ChartPointSchema = z.object({
  name: z.string(),
  value: z.number(),
});

export const DashboardPayloadSchema = z.object({
  version: z.string(),
  summary: FinancialSummarySchema,
  cash: z.number(),
  investmentsTotal: z.number(),
  debtTotal: z.number(),
  chart: z.array(ChartPointSchema),
  insightSummary: z.string(),
  showRefinanceCta: z.boolean(),
});

export type ConfigResponse = z.infer<typeof ConfigResponseSchema>;

/** Validate unknown JSON from GET /config */
export function parseConfigResponse(data: unknown): ConfigResponse {
  const parsed = ConfigResponseSchema.parse(data);
  if (parsed.version !== CONTRACT_VERSION) {
    console.warn(
      `[quantastica] Contract version mismatch: UI types ${CONTRACT_VERSION}, API ${parsed.version}`,
    );
  }
  return parsed;
}

export function parseDashboardPayload(data: unknown) {
  return DashboardPayloadSchema.parse(data);
}

export const InsightHighlightSchema = z.object({
  id: z.string(),
  severity: z.enum(["info", "watch", "action"]),
  title: z.string(),
  body: z.string(),
  actionLabel: z.string().optional(),
});

export const InsightHighlightsResponseSchema = z.object({
  version: z.string(),
  highlights: z.array(InsightHighlightSchema),
});

export function parseInsightHighlightsResponse(data: unknown) {
  return InsightHighlightsResponseSchema.parse(data);
}
