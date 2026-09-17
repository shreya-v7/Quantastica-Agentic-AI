// Domain types for the Indian finance product surface. These mirror the server's
// camelCase response shapes for the Phase B to G endpoints.

export interface Quote {
  symbol: string;
  price: number;
  currency: string;
  timestamp: string;
  previousClose?: number | null;
}

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TaxRegimeResult {
  regime: string;
  grossIncome: number;
  taxableIncome: number;
  slabTax: number;
  rebate87a: number;
  surcharge: number;
  cess: number;
  totalTax: number;
}

export interface TaxComparison {
  assessmentYear: string;
  oldRegime: TaxRegimeResult;
  newRegime: TaxRegimeResult;
  recommended: string;
  savingInr: number;
  savingDisplay: string;
}

export interface SipResult {
  targetInr: number;
  targetDisplay: string;
  monthlySip: number;
  monthlySipDisplay: string;
  stepUpFirstMonthSip?: number;
  stepUpFirstMonthSipDisplay?: string;
}

export interface SimulationResult {
  horizonYears: number;
  monthlySip: number;
  p10: number;
  p50: number;
  p90: number;
  bandsDisplay: { p10: string; p50: string; p90: string };
}

export interface LoanMatch {
  productId: string;
  provider: string;
  name: string;
  indicativeRate: number;
  emiInr: number;
  emiDisplay: string;
  processingFeeInr: number;
  foirAfter: number;
  eligible: boolean;
  reasons: string[];
  score: number;
}

export interface InsuranceMatch {
  productId: string;
  provider: string;
  name: string;
  annualPremiumInr: number;
  premiumDisplay: string;
  eligible: boolean;
  reasons: string[];
  score: number;
}

export type OrderStatus =
  | "pending_approval"
  | "approved"
  | "submitted"
  | "filled"
  | "rejected"
  | "cancelled";

export interface OrderIntent {
  id: string;
  portfolioId: string;
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  orderType: "market" | "limit";
  limitPrice: number | null;
  mode: "paper" | "live";
  status: OrderStatus;
  source: string;
  reason: string | null;
  brokerOrderId: string | null;
  fillPrice: number | null;
  notionalInr: number;
  createdAt: string;
  updatedAt: string;
}

export interface AutomationRule {
  id: string;
  name: string;
  enabled: boolean;
  portfolioId: string;
  trigger: { symbol: string; operator: "above" | "below"; price: number };
  action: { side: "buy" | "sell"; quantity: number; orderType: "market" | "limit" };
  maxNotionalInr: number;
  cooldownSeconds: number;
  executionsToday: number;
  dayNotionalInr: number;
  lastFiredAt: string | null;
  createdAt: string;
}

export type AlertKind = "price" | "percent_move" | "sentiment_flip";

export interface Alert {
  id: string;
  name: string;
  kind: AlertKind;
  symbol: string;
  operator: "above" | "below";
  threshold: number;
  channel: string;
  enabled: boolean;
  cooldownSeconds: number;
  lastLabel: string | null;
  lastTriggeredAt: string | null;
  createdAt: string;
}

export interface ChatResponse {
  intent: string;
  answer: string;
  data?: Record<string, unknown> | null;
  needsInput?: string[] | null;
  citations?: string[] | null;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface NetWorth {
  assetsInr: number;
  liabilitiesInr: number;
  netWorthInr: number;
  netWorthDisplay: string;
}

export interface Goal {
  id: string;
  name: string;
  targetInr: number;
  targetDate: string;
  priority: string;
  savedInr: number;
  progress: number;
}

export interface FinancialProfile {
  userId: string;
  income: {
    basicSalary: number;
    hraReceived: number;
    specialAllowance: number;
    otherIncome: number;
    rentPaid: number;
    metro: boolean;
  };
  cashAccounts: { id: string; name: string; institution: string; balanceInr: number }[];
  deposits: { id: string; kind: string; institution: string; principalInr: number; rate: number; maturityDate: string }[];
  retirementAccounts: { id: string; kind: string; balanceInr: number; annualContributionInr: number }[];
  mfFolios: { id: string; schemeCode: string; schemeName: string; units: number; sipAmountInr: number; sipDay: number }[];
  debts: { id: string; loanType: string; lender: string; principalOutstandingInr: number; rate: number; emiInr: number; tenureMonths: number; annualInterestInr: number }[];
  insurancePolicies: { id: string; policyType: string; provider: string; coverInr: number; annualPremiumInr: number; termYears: number }[];
  expenses: { id: string; category: string; monthlyInr: number }[];
  goals: Goal[];
  netWorth: NetWorth;
}
