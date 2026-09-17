import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { RunRequest, Severity } from "@quantastica/types";
import { api } from "../lib/api";
import { queryKeys } from "../lib/queryKeys";

export function usePlatform() {
  return useQuery({ queryKey: queryKeys.platform, queryFn: api.platform });
}

export function usePortfolios() {
  return useQuery({ queryKey: queryKeys.portfolios, queryFn: api.listPortfolios });
}

export function usePortfolio(id: string) {
  return useQuery({ queryKey: queryKeys.portfolio(id), queryFn: () => api.getPortfolio(id) });
}

export function useInsights(portfolioId?: string, severity?: Severity) {
  return useQuery({
    queryKey: queryKeys.insights(portfolioId, severity),
    queryFn: () => api.listInsights({ portfolioId, severity }),
  });
}

export function useRuns(portfolioId?: string) {
  return useQuery({ queryKey: queryKeys.runs(portfolioId), queryFn: () => api.listRuns(portfolioId) });
}

export function useRun(id: string | null, poll: boolean) {
  return useQuery({
    queryKey: queryKeys.run(id ?? "none"),
    queryFn: () => api.getRun(id as string),
    enabled: Boolean(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return poll && status !== "completed" && status !== "failed" ? 1200 : false;
    },
  });
}

export function useRunAgents() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: RunRequest) => api.runAgents(payload),
    onSuccess: (run) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.runs() });
      queryClient.invalidateQueries({ queryKey: queryKeys.insights(run.portfolioId) });
    },
  });
}

export function useExportRun() {
  return useMutation({ mutationFn: (id: string) => api.exportRun(id) });
}
