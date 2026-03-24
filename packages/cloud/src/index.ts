/**
 * TypeScript contract for cloud adapters. Implementations live in `apps/server`
 * (`app/financial_intelligence/cloud/`). This package is types-only.
 */
export type { CloudProvider } from "@quantastica/config";
export { CONFIG } from "@quantastica/config";

export interface CloudServices {
  queue(topic: string, payload: unknown): Promise<void>;
  store(key: string, value: unknown): Promise<void>;
  fetch(key: string): Promise<unknown>;
  run(job: string, payload: unknown): Promise<unknown>;
  ai(prompt: string, context?: unknown): Promise<string>;
}
