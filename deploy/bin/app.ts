#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { IocFinderStack } from '../lib/ioc-finder-stack';

const app = new cdk.App();

new IocFinderStack(app, 'IocFinderStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
  },
  description: 'IOC Finder — Lambda extraction + ECS API on EC2',
});
