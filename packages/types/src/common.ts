import { z } from "zod";

export const CONTRACT_VERSION = "2.0.0";

export const assetClassSchema = z.enum([
  "equity",
  "etf",
  "crypto",
  "bond",
  "cash",
]);
export type AssetClass = z.infer<typeof assetClassSchema>;

export const severitySchema = z.enum(["info", "low", "medium", "high"]);
export type Severity = z.infer<typeof severitySchema>;

export const ratingSchema = z.enum(["low", "medium", "high"]);
export type Rating = z.infer<typeof ratingSchema>;

export const runStatusSchema = z.enum([
  "pending",
  "running",
  "completed",
  "failed",
]);
export type RunStatus = z.infer<typeof runStatusSchema>;

export const stepStatusSchema = z.enum([
  "pending",
  "running",
  "completed",
  "failed",
]);
export type StepStatus = z.infer<typeof stepStatusSchema>;

export const transactionTypeSchema = z.enum(["buy", "sell"]);
export type TransactionType = z.infer<typeof transactionTypeSchema>;

export const platformSchema = z.enum(["local", "gcp", "aws"]);
export type Platform = z.infer<typeof platformSchema>;
