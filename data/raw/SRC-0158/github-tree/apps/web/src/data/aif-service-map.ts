export type ServiceNode = {
  readonly id: string
  readonly label: string
  readonly description: string
  readonly studySlug: string
}

export type ServiceGroup = {
  readonly id: string
  readonly title: string
  readonly nodes: readonly ServiceNode[]
}

export const AIF_SERVICE_GROUPS: readonly ServiceGroup[] = [
  {
    id: "foundations",
    title: "AI/ML 기초",
    nodes: [
      {
        id: "ai-ml-fundamentals",
        label: "AI/ML Fundamentals",
        description: "지도·비지도·강화학습, 딥러닝 기초",
        studySlug: "fundamentals",
      },
      {
        id: "generative-ai",
        label: "Generative AI",
        description: "Foundation Model, 프롬프트 엔지니어링",
        studySlug: "fundamentals",
      },
    ],
  },
  {
    id: "managed-ai",
    title: "관리형 AI 서비스",
    nodes: [
      {
        id: "rekognition",
        label: "Amazon Rekognition",
        description: "이미지·영상 분석",
        studySlug: "aws-services",
      },
      {
        id: "comprehend",
        label: "Amazon Comprehend",
        description: "자연어 처리·감정 분석",
        studySlug: "aws-services",
      },
      {
        id: "translate",
        label: "Amazon Translate",
        description: "실시간 번역",
        studySlug: "aws-services",
      },
      {
        id: "polly",
        label: "Amazon Polly",
        description: "텍스트 음성 변환",
        studySlug: "aws-services",
      },
      {
        id: "textract",
        label: "Amazon Textract",
        description: "문서 OCR·데이터 추출",
        studySlug: "aws-services",
      },
      {
        id: "kendra",
        label: "Amazon Kendra",
        description: "지능형 엔터프라이즈 검색",
        studySlug: "aws-services",
      },
    ],
  },
  {
    id: "bedrock",
    title: "Amazon Bedrock",
    nodes: [
      {
        id: "bedrock-core",
        label: "Bedrock",
        description: "Foundation Model 호스팅·추론",
        studySlug: "bedrock",
      },
      {
        id: "bedrock-kb",
        label: "Knowledge Bases",
        description: "RAG 기반 지식 검색",
        studySlug: "bedrock-evaluation-grounding",
      },
      {
        id: "bedrock-guardrails",
        label: "Guardrails",
        description: "콘텐츠 필터·주제 제한",
        studySlug: "responsible-ai",
      },
      {
        id: "bedrock-prompt",
        label: "Prompt Management",
        description: "프롬프트 버전 관리·최적화",
        studySlug: "bedrock-prompt-management",
      },
      {
        id: "bedrock-agents",
        label: "Agents & MCP",
        description: "에이전트 오케스트레이션",
        studySlug: "bedrock-agentic-ai-mcp",
      },
    ],
  },
  {
    id: "platform",
    title: "ML 플랫폼",
    nodes: [
      {
        id: "sagemaker",
        label: "SageMaker AI",
        description: "커스텀 모델 학습·배포·MLOps",
        studySlug: "sagemaker",
      },
      {
        id: "agentcore",
        label: "Bedrock AgentCore",
        description: "에이전트 런타임·메모리·도구",
        studySlug: "bedrock-agentcore",
      },
    ],
  },
  {
    id: "governance",
    title: "거버넌스·보안",
    nodes: [
      {
        id: "responsible-ai",
        label: "Responsible AI",
        description: "공정성·편향 감지·투명성",
        studySlug: "responsible-ai",
      },
      {
        id: "security",
        label: "Security & Compliance",
        description: "데이터 보호·IAM·암호화",
        studySlug: "security-governance",
      },
      {
        id: "exam-prep",
        label: "Exam Prep",
        description: "시험 전략·도메인 가중치",
        studySlug: "exam-prep",
      },
    ],
  },
] as const

export const AIF_TOTAL_NODES: number = AIF_SERVICE_GROUPS.reduce(
  (sum, group) => sum + group.nodes.length,
  0,
)
