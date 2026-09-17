import { z } from "zod";
import { platformSchema } from "./common.js";

export const componentStatusSchema = z.object({
  name: z.enum(["repository", "llm", "events", "storage", "cache"]),
  implementation: z.string(),
  ready: z.boolean(),
  missingEnv: z.array(z.string()),
});
export type ComponentStatus = z.infer<typeof componentStatusSchema>;

export const providerStatusSchema = z.object({
  name: z.string(),
  implementation: z.string(),
  ready: z.boolean(),
  missingEnv: z.array(z.string()),
});
export type ProviderStatus = z.infer<typeof providerStatusSchema>;

export const platformStatusSchema = z.object({
  platform: platformSchema,
  appEnv: z.enum(["dev", "prod"]),
  ready: z.boolean(),
  components: z.array(componentStatusSchema),
  providers: z.array(providerStatusSchema),
});
export type PlatformStatus = z.infer<typeof platformStatusSchema>;

export const healthStatusSchema = z.object({
  status: z.literal("ok"),
  version: z.string(),
});
export type HealthStatus = z.infer<typeof healthStatusSchema>;
