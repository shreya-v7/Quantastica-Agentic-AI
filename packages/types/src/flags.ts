export type CloudProvider = "aws" | "azure" | "gcp";

export type FeatureFlags = {
  cloud: CloudProvider;
  ai: boolean;
  insights: boolean;
};
