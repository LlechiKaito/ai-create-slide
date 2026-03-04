import * as cdk from "aws-cdk-lib/core";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import * as path from "path";
import { Construct } from "constructs";

import type { EnvironmentConfig } from "../../config/environments";

interface ApiStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
}

export class ApiStack extends cdk.Stack {
  public readonly functionUrl: lambda.FunctionUrl;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    const removalPolicy =
      props.config.removalPolicy === "destroy"
        ? cdk.RemovalPolicy.DESTROY
        : cdk.RemovalPolicy.RETAIN;

    const logGroup = new logs.LogGroup(this, "BackendLogGroup", {
      removalPolicy,
      retention: logs.RetentionDays.ONE_WEEK,
    });

    const backendFunction = new lambda.DockerImageFunction(
      this,
      "BackendFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset(
          path.join(__dirname, "..", "..", "..", "backend"),
          { file: "Dockerfile.lambda" },
        ),
        memorySize: props.config.lambdaMemoryMiB,
        timeout: cdk.Duration.seconds(props.config.lambdaTimeoutSeconds),
        reservedConcurrentExecutions:
          props.config.lambdaReservedConcurrency,
        environment: {
          HOST: "0.0.0.0",
          PORT: "8000",
          CORS_ALLOWED_ORIGINS: "*",
        },
        logGroup,
      },
    );

    this.functionUrl = backendFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    new cdk.CfnOutput(this, "BackendUrl", {
      value: this.functionUrl.url,
      description: "Backend Lambda Function URL",
    });
  }
}
