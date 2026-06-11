import { z } from "zod";

export const errorCodeSchema = z.enum([
  "NOT_FOUND",
  "VALIDATION_ERROR",
  "LLM_ERROR",
  "PLATFORM_NOT_CONFIGURED",
  "AUTH_REQUIRED",
  "INTERNAL_ERROR",
]);
export type ErrorCode = z.infer<typeof errorCodeSchema>;

export const apiErrorSchema = z.object({
  code: errorCodeSchema,
  message: z.string(),
});
export type ApiError = z.infer<typeof apiErrorSchema>;

export const apiMetaSchema = z.object({
  requestId: z.string(),
  version: z.string(),
});
export type ApiMeta = z.infer<typeof apiMetaSchema>;

export interface ApiEnvelope<T> {
  ok: boolean;
  data: T | null;
  error: ApiError | null;
  meta: ApiMeta;
}

export const envelopeSchema = <T extends z.ZodTypeAny>(data: T) =>
  z.object({
    ok: z.boolean(),
    data: data.nullable(),
    error: apiErrorSchema.nullable(),
    meta: apiMetaSchema,
  });
