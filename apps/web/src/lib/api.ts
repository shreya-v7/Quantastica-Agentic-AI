import type {
  AgentRun,
  ApiEnvelope,
  ErrorCode,
  Finding,
  HealthStatus,
  PlatformStatus,
  Portfolio,
  PortfolioDetail,
  RunRequest,
  Severity,
  ExportResult,
} from "@quantastica/types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "";

export class ApiClientError extends Error {
  code: ErrorCode | "NETWORK_ERROR";

  constructor(code: ErrorCode | "NETWORK_ERROR", message: string) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let body: ApiEnvelope<T>;
  try {
    const res = await fetch(`${BASE_URL}/api${path}`, {
      ...init,
      headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
    });
    body = (await res.json()) as ApiEnvelope<T>;
  } catch (cause) {
    throw new ApiClientError("NETWORK_ERROR", (cause as Error).message);
  }

  if (!body.ok || body.error) {
    const error = body.error ?? { code: "INTERNAL_ERROR" as ErrorCode, message: "Unknown error" };
    throw new ApiClientError(error.code, error.message);
  }
  return body.data as T;
}

export const api = {
  health: () => request<HealthStatus>("/health"),
  platform: () => request<PlatformStatus>("/platform"),
  listPortfolios: () => request<Portfolio[]>("/portfolios"),
  getPortfolio: (id: string) => request<PortfolioDetail>(`/portfolios/${id}`),
  listInsights: (params: { portfolioId?: string; severity?: Severity } = {}) => {
    const search = new URLSearchParams();
    if (params.portfolioId) search.set("portfolioId", params.portfolioId);
    if (params.severity) search.set("severity", params.severity);
    const query = search.toString();
    return request<Finding[]>(`/insights${query ? `?${query}` : ""}`);
  },
  runAgents: (payload: RunRequest) =>
    request<AgentRun>("/agents/run", { method: "POST", body: JSON.stringify(payload) }),
  listRuns: (portfolioId?: string) =>
    request<AgentRun[]>(`/agents/runs${portfolioId ? `?portfolioId=${portfolioId}` : ""}`),
  getRun: (id: string) => request<AgentRun>(`/agents/runs/${id}`),
  exportRun: (id: string) =>
    request<ExportResult>(`/agents/runs/${id}/export`, { method: "POST" }),
  loadSeed: () => request<Record<string, number>>("/seed/load", { method: "POST" }),
};
