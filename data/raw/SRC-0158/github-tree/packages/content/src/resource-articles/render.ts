import type { CanonicalResource, ChildFeature, ResourceEdge } from "@aws-study/shared"

const DIFFICULTY_GUIDANCE = {
  foundation:
    "먼저 서비스가 해결하는 한 가지 핵심 문제와 책임 경계를 구분한다. 관리 주체, 기본 보안 경계, 비용이 발생하는 단위를 확인한 뒤 작은 구성으로 동작을 검증한다.",
  advanced:
    "기본 기능을 아는 것에서 멈추지 않고 확장성, 장애 격리, 일관성, 네트워크 경로를 함께 검토한다. 운영 지표와 실패 모드를 먼저 정한 뒤 기능을 조합한다.",
  applied:
    "실제 아키텍처에서는 요구사항, 제한 조건, 복구 목표를 수치로 정하고 대안을 비교한다. 선택 근거와 롤백 경로를 기록하고 관측 가능한 단계로 배포한다.",
} as const

const EDGE_LABELS = {
  uses: "사용해 기능을 확장합니다",
  "integrates-with": "연동해 하나의 처리 흐름을 만듭니다",
  secures: "보안 경계와 통제를 제공합니다",
  observes: "상태와 활동을 관측합니다",
  stores: "데이터를 저장하거나 전달합니다",
  computes: "컴퓨팅 실행 기반을 제공합니다",
  delivers: "사용자 또는 다음 계층으로 결과를 전달합니다",
  orchestrates: "여러 작업의 순서와 실패 처리를 조정합니다",
} as const

type RenderContext = {
  readonly resource: CanonicalResource
  readonly features: readonly ChildFeature[]
  readonly outgoing: readonly ResourceEdge[]
  readonly incoming: readonly ResourceEdge[]
  readonly titles: ReadonlyMap<string, string>
  readonly officialUrl: string
}

function resourceLink(slug: string, titles: ReadonlyMap<string, string>): string {
  return `[${titles.get(slug) ?? slug}](/resources/${slug})`
}

function renderPrerequisites(context: RenderContext): string {
  if (context.resource.prerequisites.length === 0) {
    return `- 별도 선행 서비스 없이 시작할 수 있는 기반 항목입니다.
- 계정, 리전, IAM 최소 권한, 비용 알림을 먼저 준비합니다.`
  }
  return context.resource.prerequisites
    .map((slug) => `- ${resourceLink(slug, context.titles)}의 역할과 책임 경계를 먼저 확인합니다.`)
    .join("\n")
}

function renderRelations(context: RenderContext): string {
  const outgoing = context.outgoing.map(
    (edge) =>
      `- **${context.resource.title} → ${resourceLink(edge.to, context.titles)}**: ${EDGE_LABELS[edge.type]}.`,
  )
  const incoming = context.incoming.map(
    (edge) =>
      `- **${resourceLink(edge.from, context.titles)} → ${context.resource.title}**: ${EDGE_LABELS[edge.type]}.`,
  )
  const relations = [...outgoing, ...incoming]
  if (relations.length > 0) return relations.join("\n")
  return `- 단독 도입보다 요청 경로, 데이터 소유권, IAM 경계를 먼저 그린 뒤 연결 대상을 결정합니다.
- 연결 서비스가 없더라도 로그, 비용, 장애 알림의 수집 위치를 명확히 둡니다.`
}

function renderFeatures(context: RenderContext): string {
  if (context.features.length === 0) {
    return `### 기본 기능 경계

${context.resource.title}의 기능은 ${context.resource.summary}라는 핵심 역할을 기준으로 평가합니다. 이름이 비슷한 별도 서비스와 책임을 섞지 않고, 현재 요구사항에 필요한 기능만 활성화합니다.`
  }
  return context.features
    .map(
      (feature) => `### ${feature.title}

${feature.summary}. 이 기능은 ${context.resource.title}의 하위 기능이므로 별도 서비스 글로 복제하지 않습니다. 상위 서비스의 권한, 비용, 장애 경계를 그대로 고려하면서 적용 범위를 좁혀 사용합니다.`,
    )
    .join("\n\n")
}

export function renderResourceArticle(context: RenderContext): string {
  const guidance = DIFFICULTY_GUIDANCE[context.resource.difficulty]
  return `# ${context.resource.title}

## 한눈에 보기

${context.resource.summary}. ${context.resource.title}는 이 책임을 다른 AWS 구성 요소와 명확히 나눌 때 가장 이해하기 쉽습니다. 먼저 입력과 출력, 데이터 소유자, 호출 주체를 적고 서비스가 직접 관리하는 범위를 표시합니다.

이 글은 특정 자격증에 종속된 복사본이 아니라 모든 학습 경로가 공유하는 기준 글입니다. 세부 기능을 외우기보다 어떤 요구사항에서 선택하고, 어떤 조건에서는 다른 서비스를 검토해야 하는지에 집중합니다.

## 선행 학습

${renderPrerequisites(context)}

## 핵심 개념과 책임

${guidance}

${context.resource.title}를 설계할 때는 **제어 영역**, **데이터 영역**, **운영 영역**을 분리합니다. 제어 영역에서는 생성과 정책 변경 권한을 최소화하고, 데이터 영역에서는 암호화와 네트워크 경로를 확인합니다. 운영 영역에서는 지표, 로그, 감사 이벤트, 비용 태그를 배포 전에 준비합니다.

서비스의 기본값이 모든 워크로드에 적합하다고 가정하지 않습니다. 리전 지원, 할당량, 지연 시간, 내구성, 가용성, 데이터 이동 비용을 현재 요구사항과 대조하고, 변경 가능한 선택과 되돌리기 어려운 선택을 구분합니다.

## 일반적인 사용 방식

${renderRelations(context)}

요청 흐름을 설계할 때는 호출자가 실패를 어떻게 인식하고 재시도하는지, 중복 처리가 안전한지, 부분 실패를 어디에서 복구하는지 결정합니다. 데이터 흐름에서는 저장 위치와 보존 기간, 암호화 키 소유자, 리전 간 이동 여부를 함께 기록합니다.

## 한계와 트레이드오프

- **운영 복잡도:** ${context.resource.title} 자체의 편의 기능보다 모니터링, 권한 검토, 장애 대응 절차까지 포함한 총 운영 비용을 비교합니다.
- **확장 경계:** 자동 확장 기능이 있더라도 계정 할당량, 종속 서비스 한도, 급격한 트래픽 변화가 병목이 될 수 있습니다.
- **비용 구조:** 요청, 실행 시간, 저장 용량, 데이터 전송, 부가 기능 중 어떤 단위로 과금되는지 확인하고 예산 알림을 연결합니다.
- **보안 책임:** AWS가 관리하는 계층과 사용자가 설정해야 하는 IAM, 네트워크, 데이터 보호 책임을 문서화합니다.

구현 전에는 최소 두 가지 대안을 같은 기준으로 비교합니다. 기능 개수만 비교하지 말고 복구 시간, 데이터 손실 허용치, 팀의 운영 역량, 장기 변경 비용을 포함합니다. 선택하지 않은 대안과 그 이유도 남기면 이후 요구사항이 바뀌었을 때 재검토하기 쉽습니다.

## 주요 기능

${renderFeatures(context)}

## 운영 관계

${renderRelations(context)}

관계는 단순 연결 가능 여부가 아니라 실패와 권한이 전파되는 방향을 뜻합니다. 연결마다 인증 주체, 타임아웃, 재시도, 암호화, 로그 상관관계 ID를 정의하고 한 서비스의 장애가 전체 경로로 확대되지 않도록 격리 지점을 둡니다.

## 적용 단계

1. ${context.resource.title}가 해결할 요구사항과 성공 지표를 한 문장으로 정의합니다.
2. 가장 작은 격리 환경에서 최소 권한과 기본 암호화를 적용해 동작을 확인합니다.
3. 정상 요청뿐 아니라 권한 거부, 할당량 초과, 종속 서비스 지연, 부분 실패를 재현합니다.
4. 지표·로그·감사 이벤트·비용 태그를 대시보드와 알림에 연결합니다.
5. 배포 전 롤백 조건, 데이터 복구 절차, 담당자와 검증 주기를 기록합니다.

적용 결과는 서비스 생성 여부가 아니라 처음 정의한 성공 지표로 판단합니다. 지표가 개선되지 않거나 운영 부담이 예상보다 크면 구성을 단순화하거나 다른 관리형 서비스를 비교합니다.

## 학습 체크리스트

- ${context.resource.title}의 핵심 책임과 책임 밖의 영역을 설명할 수 있는가?
- 주요 권한 주체와 데이터 암호화 경계를 그릴 수 있는가?
- 장애 시 영향 범위와 복구 순서를 설명할 수 있는가?
- 비용이 증가하는 단위와 제어 방법을 알고 있는가?
- 선행 서비스 및 연결 서비스와의 선택 기준을 비교할 수 있는가?

## 공식 참고 자료

- [AWS 공식 문서에서 ${context.resource.title} 검색](${context.officialUrl})
`
}

export function estimateReadingMinutes(markdown: string): number {
  const readableCharacters = markdown.replace(/[`#*[\]()/_-]/g, "").replace(/\s/g, "").length
  return Math.max(3, Math.min(8, Math.ceil(readableCharacters / 500)))
}
