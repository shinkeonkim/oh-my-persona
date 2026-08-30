import type { CertLabelFixture } from "./types"

/** AIF-C01 v1.1 official in-scope services (2026-08-04). 55 labels. */
export const AIF_LABELS: CertLabelFixture = {
  certCode: "aif",
  sourceUrl:
    "https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html",
  fetchDate: "2026-08-04",
  labels: [
    // Analytics (8)
    ["AWS Data Exchange", "analytics", "aws-data-exchange"],
    ["Amazon EMR", "analytics", "amazon-emr"],
    ["AWS Glue", "analytics", "aws-glue"],
    ["AWS Glue DataBrew", "analytics", "aws-glue-databrew"],
    ["AWS Lake Formation", "analytics", "aws-lake-formation"],
    ["Amazon OpenSearch Service", "analytics", "amazon-opensearch-service"],
    ["Amazon Quick", "analytics", "amazon-quicksight"],
    ["Amazon Redshift", "analytics", "amazon-redshift"],
    // Cloud Financial Management (2)
    ["AWS Budgets", "cloud-financial-mgmt", "aws-budgets"],
    ["AWS Cost Explorer", "cloud-financial-mgmt", "aws-cost-explorer"],
    // Compute (2)
    ["Amazon EC2", "compute", "amazon-ec2"],
    ["AWS Lambda", "compute", "aws-lambda"],
    // Containers (2)
    ["Amazon Elastic Container Service (Amazon ECS)", "containers", "amazon-ecs"],
    ["Amazon Elastic Kubernetes Service (Amazon EKS)", "containers", "amazon-eks"],
    // Database (6)
    ["Amazon Aurora", "database", "amazon-aurora"],
    ["Amazon DocumentDB (with MongoDB compatibility)", "database", "amazon-documentdb"],
    ["Amazon DynamoDB", "database", "amazon-dynamodb"],
    ["Amazon ElastiCache", "database", "amazon-elasticache"],
    ["Amazon Neptune", "database", "amazon-neptune"],
    ["Amazon RDS", "database", "amazon-rds"],
    // Developer Tools (3)
    ["Kiro", "developer-tools", "kiro"],
    ["Strands Agents", "developer-tools", "strands-agents"],
    ["Amazon Q", "developer-tools", "amazon-q"],
    // Machine Learning (16)
    ["Amazon Augmented AI (Amazon A2I)", "machine-learning", "amazon-a2i"],
    ["Amazon Bedrock", "machine-learning", "amazon-bedrock"],
    ["Amazon Bedrock AgentCore", "machine-learning", "amazon-bedrock-agentcore"],
    ["Amazon Comprehend", "machine-learning", "amazon-comprehend"],
    ["Amazon Kendra", "machine-learning", "amazon-kendra"],
    ["Amazon Lex", "machine-learning", "amazon-lex"],
    ["Amazon Nova", "machine-learning", "amazon-nova"],
    ["Amazon Personalize", "machine-learning", "amazon-personalize"],
    ["Amazon Polly", "machine-learning", "amazon-polly"],
    ["Amazon Rekognition", "machine-learning", "amazon-rekognition"],
    ["Amazon SageMaker AI", "machine-learning", "amazon-sagemaker-ai"],
    ["Amazon SageMaker JumpStart", "machine-learning", "amazon-sagemaker-jumpstart"],
    ["Amazon Textract", "machine-learning", "amazon-textract"],
    ["Amazon Transcribe", "machine-learning", "amazon-transcribe"],
    ["Amazon Translate", "machine-learning", "amazon-translate"],
    ["AWS Transform", "machine-learning", "aws-transform"],
    // Management and Governance (5)
    ["AWS CloudTrail", "mgmt-governance", "aws-cloudtrail"],
    ["Amazon CloudWatch", "mgmt-governance", "amazon-cloudwatch"],
    ["AWS Config", "mgmt-governance", "aws-config"],
    ["AWS Trusted Advisor", "mgmt-governance", "aws-trusted-advisor"],
    ["AWS Well-Architected Tool", "mgmt-governance", "aws-well-architected-tool"],
    // Networking and Content Delivery (2)
    ["Amazon CloudFront", "networking-cdn", "amazon-cloudfront"],
    ["Amazon VPC", "networking-cdn", "amazon-vpc"],
    // Security, Identity, and Compliance (7)
    ["AWS Artifact", "security", "aws-artifact"],
    ["AWS Audit Manager", "security", "aws-audit-manager"],
    ["AWS Identity and Access Management (IAM)", "security", "aws-iam"],
    ["Amazon Inspector", "security", "amazon-inspector"],
    ["AWS Key Management Service (AWS KMS)", "security", "aws-kms"],
    ["Amazon Macie", "security", "amazon-macie"],
    ["AWS Secrets Manager", "security", "aws-secrets-manager"],
    // Storage (2)
    ["Amazon S3", "storage", "amazon-s3"],
    ["Amazon S3 Glacier", "storage", "amazon-s3-glacier"],
  ],
}
