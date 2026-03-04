#!/usr/bin/env node
import * as cdk from "aws-cdk-lib/core";

import { ENVIRONMENTS } from "../config/environments";
import { ApiStack } from "../lib/api/api-stack";
import { FrontendStack } from "../lib/frontend/frontend-stack";

const app = new cdk.App();

const envName = app.node.tryGetContext("env") || "dev";
const config = ENVIRONMENTS[envName];

if (!config) {
  throw new Error(`Unknown environment: ${envName}. Use "dev" or "prod".`);
}

const stackPrefix = `SlideGen-${config.envName}`;

const cdkEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const apiStack = new ApiStack(app, `${stackPrefix}-Api`, {
  config,
  env: cdkEnv,
});

new FrontendStack(app, `${stackPrefix}-Frontend`, {
  config,
  apiUrl: apiStack.functionUrl.url,
  env: cdkEnv,
});
