export interface EnvironmentConfig {
  envName: string;
  lambdaMemoryMiB: number;
  lambdaTimeoutSeconds: number;
  lambdaReservedConcurrency: number;
  removalPolicy: "destroy" | "retain";
}

export const ENVIRONMENTS: Record<string, EnvironmentConfig> = {
  dev: {
    envName: "dev",
    lambdaMemoryMiB: 512,
    lambdaTimeoutSeconds: 300,
    lambdaReservedConcurrency: 5,
    removalPolicy: "destroy",
  },
  prod: {
    envName: "prod",
    lambdaMemoryMiB: 1024,
    lambdaTimeoutSeconds: 300,
    lambdaReservedConcurrency: 50,
    removalPolicy: "destroy",
  },
};
