import {
  createContext,
  useContext,
  type ReactNode,
} from "react";
import { useQuery } from "@tanstack/react-query";
import {
  type ConfigResponse,
  parseConfigResponse,
} from "@quantastica/types";
import { apiUrl } from "../lib/apiUrl";

const SystemConfigContext = createContext<ConfigResponse | null>(null);

async function fetchConfig(): Promise<ConfigResponse> {
  const res = await fetch(apiUrl("/config"));
  if (!res.ok) {
    throw new Error(`Config failed: ${res.status}`);
  }
  return parseConfigResponse(await res.json());
}

export function SystemConfigProvider({ children }: { children: ReactNode }) {
  const { data, isPending, isError, error, refetch } = useQuery({
    queryKey: ["system", "config"],
    queryFn: fetchConfig,
    staleTime: Infinity,
    retry: 2,
  });

  if (isPending) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-background text-foreground">
        <div className="h-12 w-48 rounded-xl fi-shimmer" aria-hidden />
        <p className="fi-body text-center">Loading configuration…</p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background p-6 text-center text-foreground">
        <p className="text-sm font-medium text-destructive">Could not load system config.</p>
        <p className="fi-caption max-w-md">
          {(error as Error)?.message ?? "Unknown error"}
        </p>
        <button
          type="button"
          onClick={() => refetch()}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <SystemConfigContext.Provider value={data}>{children}</SystemConfigContext.Provider>
  );
}

export function useSystemConfig(): ConfigResponse {
  const ctx = useContext(SystemConfigContext);
  if (!ctx) {
    throw new Error("useSystemConfig must be used within SystemConfigProvider");
  }
  return ctx;
}
