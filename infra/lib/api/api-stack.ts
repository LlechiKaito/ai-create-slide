import * as cdk from "aws-cdk-lib/core";
import * as ecr_assets from "aws-cdk-lib/aws-ecr-assets";
import * as iam from "aws-cdk-lib/aws-iam";
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

    const ssmParamName = props.config.geminiApiKeySsmParam;

    const backendFunction = new lambda.DockerImageFunction(
      this,
      "BackendFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset(
          path.join(__dirname, "..", "..", "..", "backend"),
          {
            file: "Dockerfile.lambda",
            platform: ecr_assets.Platform.LINUX_AMD64,
          },
        ),
        architecture: lambda.Architecture.X86_64,
        memorySize: props.config.lambdaMemoryMiB,
        timeout: cdk.Duration.seconds(props.config.lambdaTimeoutSeconds),
        environment: {
          HOST: "0.0.0.0",
          PORT: "8000",
          CORS_ALLOWED_ORIGINS: "*",
          GEMINI_API_KEY_SSM_PARAM: ssmParamName,
        },
        logGroup,
      },
    );

    backendFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["ssm:GetParameter"],
        resources: [
          cdk.Arn.format(
            {
              service: "ssm",
              resource: "parameter",
              resourceName: ssmParamName.replace(/^\//, ""),
            },
            this,
          ),
        ],
      }),
    );

    this.functionUrl = backendFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    });

    new cdk.CfnOutput(this, "BackendUrl", {
      value: this.functionUrl.url,
      description: "Backend Lambda Function URL",
    });
  }
}
