export interface EnvironmentConfig {
  envName: string;
  lambdaMemoryMiB: number;
  lambdaTimeoutSeconds: number;
  lambdaReservedConcurrency: number;
  geminiApiKeySsmParam: string;
  removalPolicy: "destroy" | "retain";
}

export const ENVIRONMENTS: Record<string, EnvironmentConfig> = {
  dev: {
    envName: "dev",
    lambdaMemoryMiB: 512,
    lambdaTimeoutSeconds: 300,
    lambdaReservedConcurrency: 5,
    geminiApiKeySsmParam: "/slide-gen/dev/gemini-api-key",
    removalPolicy: "destroy",
  },
  prod: {
    envName: "prod",
    lambdaMemoryMiB: 1024,
    lambdaTimeoutSeconds: 300,
    lambdaReservedConcurrency: 50,
    geminiApiKeySsmParam: "/slide-gen/prod/gemini-api-key",
    removalPolicy: "destroy",
  },
};
