import { z } from "zod";
import {
  ratingSchema,
  runStatusSchema,
  severitySchema,
  stepStatusSchema,
} from "./common.js";

export const riskMetricSchema = z.object({
  id: z.string(),
  label: z.string(),
  value: z.number(),
  threshold: z.number(),
  rating: ratingSchema,
  explanation: z.string(),
});
export type RiskMetric = z.infer<typeof riskMetricSchema>;

export const planStepSchema = z.object({
  analysis: z.enum(["research", "risk", "insight"]),
  reason: z.string(),
});
export type PlanStep = z.infer<typeof planStepSchema>;

export const planSchema = z.object({
  steps: z.array(planStepSchema).min(1),
});
export type Plan = z.infer<typeof planSchema>;

export const findingSchema = z.object({
  id: z.string(),
  portfolioId: z.string(),
  runId: z.string(),
  title: z.string(),
  body: z.string(),
  severity: severitySchema,
  confidence: z.number().min(0).max(1),
  metricIds: z.array(z.string()),
  createdAt: z.string(),
  seed: z.boolean().default(false),
});
export type Finding = z.infer<typeof findingSchema>;

export const agentStepSchema = z.object({
  name: z.string(),
  status: stepStatusSchema,
  inputSummary: z.string(),
  outputSummary: z.string(),
  durationMs: z.number(),
  error: z.string().nullable(),
});
export type AgentStep = z.infer<typeof agentStepSchema>;

export const agentRunSchema = z.object({
  id: z.string(),
  portfolioId: z.string(),
  query: z.string(),
  status: runStatusSchema,
  steps: z.array(agentStepSchema),
  findings: z.array(findingSchema),
  metrics: z.array(riskMetricSchema),
  answer: z.string().nullable(),
  error: z.string().nullable(),
  createdAt: z.string(),
  completedAt: z.string().nullable(),
});
export type AgentRun = z.infer<typeof agentRunSchema>;

export const runRequestSchema = z.object({
  query: z.string().min(1),
  portfolioId: z.string().min(1),
});
export type RunRequest = z.infer<typeof runRequestSchema>;

export const exportResultSchema = z.object({
  runId: z.string(),
  location: z.string(),
  contentType: z.string(),
});
export type ExportResult = z.infer<typeof exportResultSchema>;
