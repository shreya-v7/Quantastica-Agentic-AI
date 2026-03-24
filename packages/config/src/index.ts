/**
 * Shared runtime config (TypeScript). Server authority remains env + GET /config.
 * Use for tooling and optional client imports — UI should prefer API /config at runtime.
 */
export type CloudProvider = "aws" | "azure" | "gcp";

function readCloud(): CloudProvider {
  const raw =
    typeof process !== "undefined" && process.env?.CLOUD_PROVIDER
      ? process.env.CLOUD_PROVIDER
      : undefined;
  if (raw === "aws" || raw === "azure" || raw === "gcp") {
    return raw;
  }
  return "gcp";
}

export const CONFIG = {
  cloud: readCloud(),
} as const;
