import type { CloudProvider } from "@quantastica/config";

export type { CloudProvider };

export type FeatureFlags = {
  cloud: CloudProvider;
  ai: boolean;
  insights: boolean;
};
