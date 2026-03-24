import type { ChartPoint } from "../components/Chart";
import {
  type DashboardPayload,
  type InsightHighlight,
  parseDashboardPayload,
  parseInsightHighlightsResponse,
} from "@quantastica/types";
import { apiUrl } from "./apiUrl";

export type { DashboardPayload, InsightHighlight };

/** Re-export for components that only need chart data. */
export type { ChartPoint };

/**
 * Dashboard snapshot — server-only. Demo uses `/demo/dashboard`; production uses authenticated routes.
 */
export async function fetchDashboardPayload(): Promise<DashboardPayload> {
  const res = await fetch(apiUrl("/demo/dashboard"));
  if (!res.ok) {
    throw new Error(`Dashboard: ${res.status}`);
  }
  return parseDashboardPayload(await res.json());
}

export async function fetchInsightHighlights(): Promise<InsightHighlight[]> {
  const res = await fetch(apiUrl("/demo/insight-highlights"));
  if (!res.ok) {
    throw new Error(`Insights: ${res.status}`);
  }
  const parsed = parseInsightHighlightsResponse(await res.json());
  return parsed.highlights;
}
