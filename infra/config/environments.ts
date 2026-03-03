export interface EnvironmentConfig {
  envName: string;
  backendCpu: number;
  backendMemoryMiB: number;
  backendDesiredCount: number;
  removalPolicy: "destroy" | "retain";
}

export const ENVIRONMENTS: Record<string, EnvironmentConfig> = {
  dev: {
    envName: "dev",
    backendCpu: 256,
    backendMemoryMiB: 512,
    backendDesiredCount: 1,
    removalPolicy: "destroy",
  },
  prod: {
    envName: "prod",
    backendCpu: 512,
    backendMemoryMiB: 1024,
    backendDesiredCount: 2,
    removalPolicy: "retain",
  },
};
