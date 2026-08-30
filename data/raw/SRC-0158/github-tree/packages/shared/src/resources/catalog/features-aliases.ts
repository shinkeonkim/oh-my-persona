import type { FeatureTuple } from "./types"

/**
 * Child features: sub-services discussed within a parent's article.
 * [slug, parentSlug, title, summary, order]
 */
export const CATALOG_FEATURES: readonly FeatureTuple[] = [
  // SageMaker AI child features
  [
    "amazon-sagemaker-jumpstart",
    "amazon-sagemaker-ai",
    "Amazon SageMaker JumpStart",
    "Pre-trained models and solution templates",
    0,
  ],
  [
    "sagemaker-clarify",
    "amazon-sagemaker-ai",
    "SageMaker Clarify",
    "Detect bias and explain model predictions",
    1,
  ],
  [
    "sagemaker-model-cards",
    "amazon-sagemaker-ai",
    "SageMaker Model Cards",
    "Document model details for governance",
    2,
  ],
  // Bedrock child features
  [
    "bedrock-prompt-management",
    "amazon-bedrock",
    "Bedrock Prompt Management",
    "Version and optimize prompts",
    0,
  ],
  [
    "bedrock-model-evaluations",
    "amazon-bedrock",
    "Bedrock Model Evaluations",
    "Evaluate foundation model quality",
    1,
  ],
  [
    "bedrock-guardrails",
    "amazon-bedrock",
    "Bedrock Guardrails",
    "Content filtering and topic restrictions",
    2,
  ],
  // AgentCore child features
  [
    "agentcore-identity",
    "amazon-bedrock-agentcore",
    "AgentCore Identity",
    "Identity management for AI agents",
    0,
  ],
  [
    "agentcore-policy",
    "amazon-bedrock-agentcore",
    "AgentCore Policy",
    "Policy controls for agent actions",
    1,
  ],
  // EC2 child features
  [
    "amazon-ec2-auto-scaling",
    "amazon-ec2",
    "Amazon EC2 Auto Scaling",
    "Automatic scaling for EC2 instances",
    0,
  ],
  // Aurora child features
  [
    "amazon-aurora-serverless",
    "amazon-aurora",
    "Amazon Aurora Serverless",
    "On-demand auto-scaling Aurora configuration",
    0,
  ],
  // ECS child features
  [
    "amazon-ecs-anywhere",
    "amazon-ecs",
    "Amazon ECS Anywhere",
    "Run ECS tasks on external infrastructure",
    0,
  ],
  // EKS child features
  [
    "amazon-eks-anywhere",
    "amazon-eks",
    "Amazon EKS Anywhere",
    "Run EKS on your own infrastructure",
    0,
  ],
  [
    "amazon-eks-distro",
    "amazon-eks",
    "Amazon EKS Distro",
    "Kubernetes distribution used by EKS",
    1,
  ],
]

/**
 * Aliases: alternate URL slugs that resolve to a canonical resource.
 * [alias, canonicalSlug]
 */
export const CATALOG_ALIASES: readonly (readonly [string, string])[] = [
  ["ec2", "amazon-ec2"],
  ["s3", "amazon-s3"],
  ["lambda", "aws-lambda"],
  ["iam", "aws-iam"],
  ["rds", "amazon-rds"],
  ["dynamodb", "amazon-dynamodb"],
  ["vpc", "amazon-vpc"],
  ["cloudfront", "amazon-cloudfront"],
  ["sqs", "amazon-sqs"],
  ["sns", "amazon-sns"],
  ["ecs", "amazon-ecs"],
  ["eks", "amazon-eks"],
  ["ecr", "amazon-ecr"],
  ["kms", "aws-kms"],
  ["ebs", "amazon-ebs"],
  ["efs", "amazon-efs"],
  ["elb", "elastic-load-balancing"],
  ["dms", "aws-dms"],
  ["bedrock", "amazon-bedrock"],
  ["sagemaker", "amazon-sagemaker-ai"],
  ["agentcore", "amazon-bedrock-agentcore"],
]
