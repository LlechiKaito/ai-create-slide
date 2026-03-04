import * as cdk from "aws-cdk-lib/core";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

import type { EnvironmentConfig } from "../../config/environments";

interface FrontendStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  apiUrl: string;
}

export class FrontendStack extends cdk.Stack {
  public readonly distribution: cloudfront.Distribution;

  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    const removalPolicy =
      props.config.removalPolicy === "destroy"
        ? cdk.RemovalPolicy.DESTROY
        : cdk.RemovalPolicy.RETAIN;

    const siteBucket = new s3.Bucket(this, "SiteBucket", {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy,
      autoDeleteObjects: props.config.removalPolicy === "destroy",
    });

    const originAccessIdentity = new cloudfront.OriginAccessIdentity(
      this,
      "OAI",
    );
    siteBucket.grantRead(originAccessIdentity);

    this.distribution = new cloudfront.Distribution(this, "Distribution", {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessIdentity(siteBucket, {
          originAccessIdentity,
        }),
        viewerProtocolPolicy:
          cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      },
      defaultRootObject: "index.html",
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.minutes(0),
        },
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.minutes(0),
        },
      ],
    });

    new s3deploy.BucketDeployment(this, "DeployWebsite", {
      sources: [s3deploy.Source.asset("../frontend/dist")],
      destinationBucket: siteBucket,
      distribution: this.distribution,
      distributionPaths: ["/*"],
    });

    new s3deploy.BucketDeployment(this, "DeployRuntimeConfig", {
      sources: [
        s3deploy.Source.jsonData("runtime-config.json", {
          apiUrl: props.apiUrl,
        }),
      ],
      destinationBucket: siteBucket,
      distribution: this.distribution,
      distributionPaths: ["/runtime-config.json"],
    });

    new cdk.CfnOutput(this, "DistributionDomainName", {
      value: this.distribution.distributionDomainName,
      description: "CloudFront distribution domain name",
    });

    new cdk.CfnOutput(this, "BucketName", {
      value: siteBucket.bucketName,
      description: "S3 bucket name for frontend assets",
    });
  }
}
