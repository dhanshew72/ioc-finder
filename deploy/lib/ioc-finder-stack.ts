import * as cdk from 'aws-cdk-lib';
import * as autoscaling from 'aws-cdk-lib/aws-autoscaling';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export class IocFinderStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const anthropicApiKeySecret = secretsmanager.Secret.fromSecretNameV2(
      this, 'AnthropicApiKeySecret', 'ClaudeAPIKey'
    );
    const googleClientIdSecret = secretsmanager.Secret.fromSecretNameV2(
      this, 'GoogleClientIdSecret', 'GoogleClientID'
    );
    const iocDataBucket = s3.Bucket.fromBucketName(this, 'IocDataBucket', 'ioc-finder-data');

    const extractionFn = this.createExtractionLambda()
    iocDataBucket.grantReadWrite(extractionFn);
    anthropicApiKeySecret.grantRead(extractionFn);
    googleClientIdSecret.grantRead(extractionFn);

    const vpc = ec2.Vpc.fromLookup(this, 'Vpc', { vpcId: "vpc-0bc7cae8c296f4c58" });
    const apiRepo = ecr.Repository.fromRepositoryAttributes(this, 'ApiRepository', {
      repositoryArn: 'arn:aws:ecr:us-east-1:515504445954:repository/ioc-finder-app',
      repositoryName: 'ioc-finder-app',
    });

    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
      clusterName: 'ioc-finder',
    });

    const instanceRole = new iam.Role(this, 'EcsInstanceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2ContainerServiceforEC2Role'),
      ],
    });

    const userData = ec2.UserData.forLinux();
    userData.addCommands(`echo ECS_CLUSTER=${cluster.clusterName} >> /etc/ecs/ecs.config`);

    const launchTemplate = new ec2.LaunchTemplate(this, 'EcsLaunchTemplate', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      machineImage: ecs.EcsOptimizedImage.amazonLinux2(),
      userData,
      role: instanceRole,
    });

    const asg = new autoscaling.AutoScalingGroup(this, 'EcsAsg', {
      vpc,
      launchTemplate,
      desiredCapacity: 1,
      minCapacity: 1,
      maxCapacity: 1,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS},
    });

    const capacityProvider = new ecs.AsgCapacityProvider(this, 'AsgCapacityProvider', {
      autoScalingGroup: asg,
      enableManagedScaling: false,
      enableManagedTerminationProtection: false,
    });
    cluster.addAsgCapacityProvider(capacityProvider);


    const apiService = new ecsPatterns.ApplicationLoadBalancedEc2Service(this, 'ApiService', {
      cluster,
      desiredCount: 1,
      listenerPort: 8001,
      openListener: false,
      memoryLimitMiB: 256,
      cpu: 256,
      taskImageOptions: {
        image: ecs.ContainerImage.fromEcrRepository(apiRepo, 'latest'),
        containerPort: 8001,
      },
    });
    apiService.loadBalancer.connections.allowFrom(
      ec2.Peer.ipv4(vpc.vpcCidrBlock),
      ec2.Port.tcp(8001),
      'Allow port 8001 from VPC only'
    );

    apiService.targetGroup.configureHealthCheck({
      path: '/health',
      healthyHttpCodes: '200',
      interval: cdk.Duration.seconds(30),
      unhealthyThresholdCount: 3,
    });

    extractionFn.grantInvoke(apiService.taskDefinition.taskRole);
    googleClientIdSecret.grantRead(apiService.taskDefinition.taskRole);
  }

  private createExtractionLambda(): cdk.aws_lambda.Function {
    const deployBucket = s3.Bucket.fromBucketName(this, 'DeployBucket', 'ioc-deploy');
    const extractionFn = new lambda.Function(this, 'ExtractionFunction', {
      functionName: 'ioc-finder-extraction',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'main.main',
      code: lambda.Code.fromBucket(deployBucket, 'extraction/package.zip'),
      memorySize: 512,
      timeout: cdk.Duration.minutes(5)
    });
    return extractionFn
  }
}
