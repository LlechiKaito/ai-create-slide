import * as cdk from "aws-cdk-lib/core";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecsPatterns from "aws-cdk-lib/aws-ecs-patterns";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

import type { EnvironmentConfig } from "../../config/environments";

interface ComputeStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
}

export class ComputeStack extends cdk.Stack {
  public readonly fargateService: ecsPatterns.ApplicationLoadBalancedFargateService;

  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, "Vpc", {
      maxAzs: 2,
      natGateways: props.config.envName === "prod" ? 2 : 1,
    });

    const cluster = new ecs.Cluster(this, "Cluster", {
      vpc,
      containerInsights:
        props.config.envName === "prod" ? true : false,
    });

    const removalPolicy =
      props.config.removalPolicy === "destroy"
        ? cdk.RemovalPolicy.DESTROY
        : cdk.RemovalPolicy.RETAIN;

    this.fargateService =
      new ecsPatterns.ApplicationLoadBalancedFargateService(
        this,
        "BackendService",
        {
          cluster,
          cpu: props.config.backendCpu,
          memoryLimitMiB: props.config.backendMemoryMiB,
          desiredCount: props.config.backendDesiredCount,
          taskImageOptions: {
            image: ecs.ContainerImage.fromAsset("../backend"),
            containerPort: 8000,
            logDriver: ecs.LogDrivers.awsLogs({
              streamPrefix: "backend",
              logRetention: logs.RetentionDays.ONE_WEEK,
              logGroup: new logs.LogGroup(this, "BackendLogGroup", {
                removalPolicy,
                retention: logs.RetentionDays.ONE_WEEK,
              }),
            }),
            environment: {
              HOST: "0.0.0.0",
              PORT: "8000",
              CORS_ALLOWED_ORIGINS: "*",
            },
          },
          publicLoadBalancer: true,
          healthCheck: {
            command: [
              "CMD-SHELL",
              "curl -f http://localhost:8000/api/health || exit 1",
            ],
            interval: cdk.Duration.seconds(30),
            timeout: cdk.Duration.seconds(5),
            retries: 3,
          },
        },
      );

    this.fargateService.targetGroup.configureHealthCheck({
      path: "/api/health",
      healthyHttpCodes: "200",
    });

    new cdk.CfnOutput(this, "LoadBalancerDNS", {
      value: this.fargateService.loadBalancer.loadBalancerDnsName,
      description: "Backend ALB DNS name",
    });
  }
}
