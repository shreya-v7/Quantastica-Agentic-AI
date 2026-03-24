import type { CloudProvider } from "./config";

export type { CloudProvider };

export type FeatureFlags = {
  cloud: CloudProvider;
  ai: boolean;
  insights: boolean;
};
