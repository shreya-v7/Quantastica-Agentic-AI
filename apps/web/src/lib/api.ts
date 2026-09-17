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

export type DeskException = {
  id: string;
  householdId: string;
  ruleId: string;
  title: string;
  rupeeDelta: number;
  dueDate: string | null;
  severity: string;
  metricIds: string[];
  fingerprint: string;
  traceId: string;
  calculator: string;
  calculatorVersion: string;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  computedAt: string;
};

export type DeskQueue = {
  household: { id: string; name: string; asOf: string; totalMarket: number };
  exceptions: DeskException[];
  lots: {
    id: string;
    symbol: string;
    name: string;
    quantity: number;
    price: number;
    marketValue: number;
    sector: string;
    acquiredOn: string;
  }[];
};

export type FeatureFlags = {
  tradingChat: boolean;
  tradingMode: string;
  voice: boolean;
  demoMode: boolean;
  roles: string[];
};

export type IngestResult = {
  status: "applied" | "needs_review" | string;
  threadId?: string;
  missingFields?: string[];
  extracted?: Record<string, unknown>;
  confidence?: number;
  queue?: DeskQueue;
};

export type SpeechResult = {
  transcript: string;
  intent: string;
  answer?: string;
  audio?: string;
  status?: string;
  threadId?: string;
  missingFields?: string[];
  extracted?: Record<string, unknown>;
  exceptions?: DeskException[];
  order?: Record<string, unknown>;
};

export type DeskMetrics = {
  households: number;
  lots: number;
  documentsIngested: number;
  exceptionsOpen: number;
  rupeeDeltaSurfaced: number;
  reviewRate: number;
  extractionAccuracy: number | null;
  medianUploadToExceptionSeconds: number | null;
};

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
    const raw = await res.text();
    if (!raw) {
      throw new ApiClientError(
        "NETWORK_ERROR",
        "The API did not respond. Start the server with make dev.",
      );
    }
    try {
      body = JSON.parse(raw) as ApiEnvelope<T>;
    } catch {
      throw new ApiClientError(
        "NETWORK_ERROR",
        `The API returned a non-JSON response (${res.status}).`,
      );
    }
  } catch (cause) {
    if (cause instanceof ApiClientError) throw cause;
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

  // Desk
  listHouseholds: () => request<{ id: string; name: string; asOf: string }[]>("/desk/households"),
  deskQueue: (householdId: string) => request<DeskQueue>(`/desk/households/${householdId}/queue`),
  setLotQuantity: (householdId: string, lotId: string, quantity: number) =>
    post<DeskQueue>(`/desk/households/${householdId}/lots/${lotId}`, { quantity }),
  ingestBook: (payload: {
    household_id: string;
    kind: string;
    raw_text?: string;
    image_b64?: string;
    vlm_override?: Record<string, unknown>;
  }) => post<IngestResult>("/ingest", payload),
  resumeIngest: (threadId: string, patch: Record<string, unknown>) =>
    post<IngestResult>("/ingest/resume", { thread_id: threadId, patch }),
  transcribe: (householdId: string, audioB64: string) =>
    post<SpeechResult>("/speech/transcribe", {
      household_id: householdId,
      audio_b64: audioB64,
    }),
  flags: () => request<FeatureFlags>("/flags"),
  deskMetrics: () => request<DeskMetrics>("/metrics/desk"),
  controlDashboards: () =>
    request<{
      exec: Record<string, unknown>;
      product: Record<string, unknown>;
      aiQuality: Record<string, number | Record<string, number>>;
      sre: Record<string, unknown>;
      finops: Record<string, unknown>;
      security: Record<string, unknown>;
      fde: { score: number; rupeesSurfaced: number; layoutCoverage: number };
      olap: { engine: string; events: number; households: number };
    }>("/control/dashboards"),
  controlTrust: () =>
    request<{
      residency: string;
      cmek: boolean;
      rls: string;
      dsr: string[];
      breachWindowHours: number;
      advice: string;
      trading: string;
    }>("/control/trust"),
  controlEvals: () => request<{ gates: { goldenRupee: boolean }; metrics: Record<string, number> }>("/control/evals"),
  runDemo: () => post<Record<string, unknown>>("/demo/run", {}),
  parseTrade: (text: string) => post<Record<string, unknown>>("/trades/parse", { text }),

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
  listDocuments: () =>
    request<{ id: string; title: string; contentType: string; createdAt: string }[]>("/documents"),
  ingestDocument: (title: string, text: string) =>
    post<{ documentId: string | null; chunks: number }>("/documents", { title, text }),

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
