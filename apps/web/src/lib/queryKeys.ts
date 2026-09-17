export const queryKeys = {
  health: ["health"] as const,
  platform: ["platform"] as const,
  portfolios: ["portfolios"] as const,
  portfolio: (id: string) => ["portfolio", id] as const,
  insights: (portfolioId?: string, severity?: string) =>
    ["insights", portfolioId ?? null, severity ?? null] as const,
  runs: (portfolioId?: string) => ["runs", portfolioId ?? null] as const,
  run: (id: string) => ["run", id] as const,
};
