import type { ResourceEdge } from "../resource-relations"

/**
 * Real typed AWS relationships between canonical resources.
 * [from, to, type] — compact tuples parsed at the boundary.
 */
export const CATALOG_EDGES: readonly (readonly [string, string, ResourceEdge["type"]])[] = [
  // IAM secures core services
  ["aws-iam", "amazon-ec2", "secures"],
  ["aws-iam", "amazon-s3", "secures"],
  ["aws-iam", "aws-lambda", "secures"],
  ["aws-iam", "amazon-rds", "secures"],
  ["aws-iam", "amazon-dynamodb", "secures"],
  ["aws-iam", "amazon-bedrock", "secures"],
  // KMS secures data services
  ["aws-kms", "amazon-s3", "secures"],
  ["aws-kms", "amazon-ebs", "secures"],
  ["aws-kms", "amazon-rds", "secures"],
  ["aws-kms", "amazon-dynamodb", "secures"],
  ["aws-kms", "amazon-sqs", "secures"],
  // CloudWatch observes services
  ["amazon-cloudwatch", "amazon-ec2", "observes"],
  ["amazon-cloudwatch", "aws-lambda", "observes"],
  ["amazon-cloudwatch", "amazon-rds", "observes"],
  ["amazon-cloudwatch", "amazon-ecs", "observes"],
  ["amazon-cloudwatch", "amazon-api-gateway", "observes"],
  // CloudTrail observes API activity
  ["aws-cloudtrail", "aws-iam", "observes"],
  ["aws-cloudtrail", "amazon-s3", "observes"],
  // Compute uses storage
  ["amazon-ec2", "amazon-ebs", "uses"],
  ["amazon-ec2", "amazon-s3", "stores"],
  ["aws-lambda", "amazon-s3", "stores"],
  ["aws-lambda", "amazon-dynamodb", "stores"],
  // API Gateway integrates with compute
  ["amazon-api-gateway", "aws-lambda", "integrates-with"],
  ["amazon-api-gateway", "amazon-ec2", "integrates-with"],
  // Step Functions orchestrates
  ["aws-step-functions", "aws-lambda", "orchestrates"],
  ["aws-step-functions", "amazon-ecs", "orchestrates"],
  ["aws-step-functions", "amazon-sns", "orchestrates"],
  // EventBridge orchestrates
  ["amazon-eventbridge", "aws-lambda", "orchestrates"],
  ["amazon-eventbridge", "amazon-sqs", "orchestrates"],
  // CloudFront delivers content
  ["amazon-cloudfront", "amazon-s3", "delivers"],
  ["amazon-cloudfront", "elastic-load-balancing", "delivers"],
  ["amazon-cloudfront", "amazon-api-gateway", "delivers"],
  // ELB delivers to compute
  ["elastic-load-balancing", "amazon-ec2", "delivers"],
  ["elastic-load-balancing", "amazon-ecs", "delivers"],
  ["elastic-load-balancing", "aws-fargate", "delivers"],
  // Containers use ECR
  ["amazon-ecs", "amazon-ecr", "uses"],
  ["amazon-eks", "amazon-ecr", "uses"],
  // Data pipeline
  ["amazon-kinesis", "amazon-s3", "stores"],
  ["amazon-kinesis", "amazon-redshift", "stores"],
  ["amazon-data-firehose", "amazon-s3", "stores"],
  ["aws-glue", "amazon-s3", "stores"],
  ["aws-glue", "amazon-redshift", "integrates-with"],
  ["amazon-athena", "amazon-s3", "uses"],
  // Bedrock uses models
  ["amazon-bedrock", "amazon-s3", "stores"],
  ["amazon-bedrock-agentcore", "amazon-bedrock", "uses"],
  ["amazon-sagemaker-ai", "amazon-s3", "stores"],
  ["amazon-sagemaker-ai", "amazon-ec2", "computes"],
  // VPC networking
  ["amazon-vpc", "amazon-ec2", "computes"],
  ["aws-transit-gateway", "amazon-vpc", "integrates-with"],
  ["aws-direct-connect", "amazon-vpc", "integrates-with"],
  // GuardDuty secures
  ["amazon-guardduty", "amazon-ec2", "secures"],
  ["amazon-guardduty", "amazon-s3", "secures"],
  // WAF secures
  ["aws-waf", "amazon-cloudfront", "secures"],
  ["aws-waf", "amazon-api-gateway", "secures"],
  ["aws-waf", "elastic-load-balancing", "secures"],
  ["amazon-lightsail", "amazon-route-53", "integrates-with"],
  ["aws-wavelength", "amazon-vpc", "integrates-with"],
  ["vmware-cloud-on-aws", "aws-direct-connect", "integrates-with"],
  ["aws-serverless-application-repository", "aws-lambda", "delivers"],
  ["aws-device-farm", "aws-amplify", "integrates-with"],
  ["amazon-managed-grafana", "amazon-cloudwatch", "observes"],
  ["amazon-managed-service-for-prometheus", "amazon-eks", "observes"],
  ["amazon-managed-service-for-prometheus", "amazon-ecs", "observes"],
  ["amazon-elastic-transcoder", "amazon-s3", "uses"],
  ["aws-iot-core", "aws-lambda", "integrates-with"],
  ["amazon-appstream-2-0", "amazon-vpc", "uses"],
  ["amazon-workspaces", "aws-directory-service", "uses"],
  ["amazon-workspaces-secure-browser", "amazon-vpc", "uses"],
  ["aws-application-discovery-service", "aws-migration-hub", "integrates-with"],
  ["migration-evaluator", "aws-migration-hub", "integrates-with"],
  ["aws-migration-hub", "aws-application-migration-service", "orchestrates"],
  ["aws-sct", "aws-dms", "integrates-with"],
]
