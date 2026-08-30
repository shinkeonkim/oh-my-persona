import type { CertLabelFixture } from "./types"

/**
 * AIF-C01 objective-only labels: services/features referenced in exam objectives
 * but NOT listed on the official in-scope services page. These are classified as
 * child features of their parent canonical resources.
 * Distinct from the 55 in-scope service labels.
 */
export const AIF_OBJECTIVE_LABELS: CertLabelFixture = {
  certCode: "aif",
  sourceUrl:
    "https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html",
  fetchDate: "2026-08-04",
  labels: [
    // Networking (referenced in security/governance objectives)
    ["AWS PrivateLink", "objective-only", "aws-privatelink", "D5"],
    // Bedrock sub-features (referenced in foundation model application objectives)
    ["Amazon Bedrock Prompt Management", "objective-only", "bedrock-prompt-management", "D3"],
    ["Amazon Bedrock Model Evaluations", "objective-only", "bedrock-model-evaluations", "D3"],
    ["Amazon Bedrock Guardrails", "objective-only", "bedrock-guardrails", "D4"],
    // AgentCore sub-features (referenced in agentic AI objectives)
    ["Amazon Bedrock AgentCore Identity", "objective-only", "agentcore-identity", "D5"],
    ["Policy in AgentCore", "objective-only", "agentcore-policy", "D5"],
    // SageMaker sub-features (referenced in responsible AI objectives)
    ["SageMaker Clarify", "objective-only", "sagemaker-clarify", "D4"],
    ["Amazon SageMaker Model Cards", "objective-only", "sagemaker-model-cards", "D4"],
  ],
}
