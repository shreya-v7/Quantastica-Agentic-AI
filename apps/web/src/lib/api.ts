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
import type {
  Alert,
  AutomationRule,
  Candle,
  ChatResponse,
  FinancialProfile,
  InsuranceMatch,
  LoanMatch,
  OrderIntent,
  Quote,
  SimulationResult,
  SipResult,
  TaxComparison,
  TokenPair,
} from "./domain";

const BASE_URL = import.meta.env.VITE_API_URL ?? "";
const TOKEN_KEY = "quantastica.accessToken";

function safeStorage(): Storage | null {
  try {
    if (typeof localStorage !== "undefined" && typeof localStorage.getItem === "function") {
      return localStorage;
    }
  } catch {
    /* access can throw in some sandboxes */
  }
  return null;
}

export function setAccessToken(token: string | null): void {
  const store = safeStorage();
  if (!store) return;
  if (token) store.setItem(TOKEN_KEY, token);
  else store.removeItem(TOKEN_KEY);
}

export function getAccessToken(): string | null {
  const store = safeStorage();
  return store ? store.getItem(TOKEN_KEY) : null;
}

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
  const token = getAccessToken();
  try {
    const res = await fetch(`${BASE_URL}/api${path}`, {
      ...init,
      headers: {
        "content-type": "application/json",
        ...(token ? { authorization: `Bearer ${token}` } : {}),
        ...(init?.headers ?? {}),
      },
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

const post = <T>(path: string, payload: unknown) =>
  request<T>(path, { method: "POST", body: JSON.stringify(payload) });

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

  // Auth
  register: (email: string, password: string) =>
    post<{ id: string; email: string }>("/auth/register", { email, password }),
  login: (email: string, password: string, totpCode?: string) =>
    post<TokenPair>("/auth/login", { email, password, totpCode }),

  // Markets
  quote: (symbol: string) => request<Quote>(`/market/${encodeURIComponent(symbol)}/quote`),
  candles: (symbol: string, range: string) =>
    request<Candle[]>(`/market/${encodeURIComponent(symbol)}/candles?range=${range}`),

  // Calculators
  taxCompare: (payload: Record<string, unknown>) => post<TaxComparison>("/tax/compare", payload),
  sip: (payload: Record<string, unknown>) => post<SipResult>("/calc/sip", payload),
  simulate: (payload: Record<string, unknown>) => post<SimulationResult>("/simulate", payload),

  // Match
  matchLoans: (payload: Record<string, unknown>) => post<LoanMatch[]>("/match/loans", payload),
  matchInsurance: (payload: Record<string, unknown>) =>
    post<InsuranceMatch[]>("/match/insurance", payload),

  // Chat
  chat: (message: string, portfolioId?: string, params?: Record<string, unknown>) =>
    post<ChatResponse>("/chat", { message, portfolioId, params: params ?? {} }),

  // Trades
  listIntents: () => request<OrderIntent[]>("/trades/intents"),
  createIntent: (payload: Record<string, unknown>) =>
    post<OrderIntent>("/trades/intents", payload),
  executeIntent: (id: string) => post<OrderIntent>(`/trades/intents/${id}/execute`, {}),
  cancelIntent: (id: string) => post<OrderIntent>(`/trades/intents/${id}/cancel`, {}),
  killSwitch: (disabled: boolean) =>
    post<{ tradingDisabled: boolean }>("/trades/kill-switch", { disabled }),

  // Automation
  listRules: () => request<AutomationRule[]>("/automation/rules"),
  createRule: (payload: Record<string, unknown>) =>
    post<AutomationRule>("/automation/rules", payload),
  toggleRule: (id: string, enabled: boolean) =>
    post<unknown>(`/automation/rules/${id}/toggle`, { enabled }),
  deleteRule: (id: string) => request<unknown>(`/automation/rules/${id}`, { method: "DELETE" }),
  automationMaster: (enabled: boolean) => post<unknown>("/automation/master", { enabled }),

  // Alerts
  listAlerts: () => request<Alert[]>("/alerts"),
  createAlert: (payload: Record<string, unknown>) => post<Alert>("/alerts", payload),
  deleteAlert: (id: string) => request<unknown>(`/alerts/${id}`, { method: "DELETE" }),

  // Profile
  getProfile: () => request<FinancialProfile>("/profile"),
  setIncome: (payload: Record<string, unknown>) =>
    request<unknown>("/profile/income", { method: "PUT", body: JSON.stringify(payload) }),
  addProfileItem: (segment: string, payload: Record<string, unknown>) =>
    post<{ id: string }>(`/profile/${segment}`, payload),
  deleteProfileItem: (segment: string, id: string) =>
    request<unknown>(`/profile/${segment}/${id}`, { method: "DELETE" }),
};
