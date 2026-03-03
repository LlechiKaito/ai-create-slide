#!/usr/bin/env node
import * as cdk from "aws-cdk-lib/core";

import { ENVIRONMENTS } from "../config/environments";
import { ComputeStack } from "../lib/compute/compute-stack";
import { FrontendStack } from "../lib/frontend/frontend-stack";

const app = new cdk.App();

const envName = app.node.tryGetContext("env") || "dev";
const config = ENVIRONMENTS[envName];

if (!config) {
  throw new Error(`Unknown environment: ${envName}. Use "dev" or "prod".`);
}

const stackPrefix = `SlideGen-${config.envName}`;

new ComputeStack(app, `${stackPrefix}-Compute`, {
  config,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

new FrontendStack(app, `${stackPrefix}-Frontend`, {
  config,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
