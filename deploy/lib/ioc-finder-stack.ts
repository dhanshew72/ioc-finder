import * as cdk from 'aws-cdk-lib';
import * as autoscaling from 'aws-cdk-lib/aws-autoscaling';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export class IocFinderStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const anthropicApiKeySecret = secretsmanager.Secret.fromSecretNameV2(
      this, 'AnthropicApiKeySecret', 'TBD'
    );
    const googleClientIdSecret = secretsmanager.Secret.fromSecretNameV2(
      this, 'GoogleClientIdSecret', 'TBD'
    );

    // ── VPC ──────────────────────────────────────────────────────────────────
    const vpc = ec2.Vpc.fromLookup(this, 'Vpc', { isDefault: true });

    // ── S3 ───────────────────────────────────────────────────────────────────
    const iocDataBucket = s3.Bucket.fromBucketName(this, 'IocDataBucket', 'ioc-finder-data');
    const deployBucket = s3.Bucket.fromBucketName(this, 'DeployBucket', 'ioc-deploy');

    // ── Lambda: IOC Extraction ────────────────────────────────────────────────
    // Code is pulled from the zip uploaded by `make deploy` in extraction/.
    const extractionFn = new lambda.Function(this, 'ExtractionFunction', {
      functionName: 'ioc-finder-extraction',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'main.main',
      code: lambda.Code.fromBucket(deployBucket, 'extraction/package.zip'),
      memorySize: 512,
      timeout: cdk.Duration.minutes(5)
    });

    iocDataBucket.grantReadWrite(extractionFn);
    anthropicApiKeySecret.grantRead(extractionFn);
    googleClientIdSecret.grantRead(extractionFn);

    // ── ECR: existing repository lookup ──────────────────────────────────────
    const apiRepo = ecr.Repository.fromRepositoryAttributes(this, 'ApiRepository', {
      repositoryArn: 'arn:aws:ecr:us-east-1:515504445954:repository/ioc-finder-app',
      repositoryName: 'ioc-finder-app',
    });

    // ── ECS Cluster on EC2 ────────────────────────────────────────────────────
    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
      clusterName: 'ioc-finder',
    });

    // t2.micro = 750 free hours/month for the first 12 months of free tier.
    // maxCapacity: 1 ensures we never spin up a second (paid) instance.
    const asg = new autoscaling.AutoScalingGroup(this, 'EcsAsg', {
      vpc,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
      machineImage: ecs.EcsOptimizedImage.amazonLinux2(),
      desiredCapacity: 1,
      minCapacity: 1,
      maxCapacity: 1,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      associatePublicIpAddress: true,
    });

    const capacityProvider = new ecs.AsgCapacityProvider(this, 'AsgCapacityProvider', {
      autoScalingGroup: asg,
      enableManagedScaling: false,
      enableManagedTerminationProtection: false,
    });
    cluster.addAsgCapacityProvider(capacityProvider);

    // ── ECS Service + ALB ─────────────────────────────────────────────────────
    // ALB is covered by free tier: 750 hours/month, first 12 months.
    // memoryLimitMiB 512 leaves ~500 MB for the OS + ECS agent on a 1 GB host.
    const apiService = new ecsPatterns.ApplicationLoadBalancedEc2Service(this, 'ApiService', {
      cluster,
      desiredCount: 1,
      publicLoadBalancer: true,
      listenerPort: 80,
      memoryLimitMiB: 512,
      cpu: 256,
      taskImageOptions: {
        image: ecs.ContainerImage.fromEcrRepository(apiRepo, 'latest'),  // 515504445954.dkr.ecr.us-east-1.amazonaws.com/ioc-finder-app:latest
        containerPort: 80,
      },
    });

    // Health check — FastAPI's root or a /health endpoint
    apiService.targetGroup.configureHealthCheck({
      path: '/health',
      healthyHttpCodes: '200',
      interval: cdk.Duration.seconds(30),
      unhealthyThresholdCount: 3,
    });

    // ── Outputs ───────────────────────────────────────────────────────────────
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: `http://${apiService.loadBalancer.loadBalancerDnsName}`,
      description: 'API service URL',
    });

    new cdk.CfnOutput(this, 'ExtractionLambdaArn', {
      value: extractionFn.functionArn,
      description: 'Extraction Lambda ARN',
    });
  }
}
