# Amazon Bedrock AgentCore

Amazon Bedrock AgentCore는 AI 에이전트의 배포, 실행, 관찰을 위한 관리형 인프라 서비스다. 에이전트 프레임워크에 독립적으로 동작하며, 프로덕션 수준의 에이전트 운영 환경을 제공한다.

## AgentCore 런타임

AgentCore Runtime은 에이전트 코드를 서버리스 환경에서 실행한다. 개발자는 에이전트 로직에만 집중하고, 인프라 프로비저닝과 스케일링은 AgentCore가 자동으로 처리한다.

- **서버리스 실행**: 요청 기반 자동 확장, 유휴 시 비용 없음
- **프레임워크 독립**: LangChain, CrewAI, 커스텀 프레임워크 등 어떤 에이전트 코드든 배포 가능
- **컨테이너 기반**: 에이전트 코드를 컨테이너 이미지로 패키징하여 일관된 실행 환경 보장

## 도구 관리 (Tool Management)

AgentCore는 에이전트가 사용하는 도구를 중앙에서 관리한다. MCP 서버, Lambda 함수, API 엔드포인트를 도구로 등록하고, 에이전트가 런타임에 필요한 도구를 검색하여 호출한다.

- **도구 레지스트리**: 조직 내 모든 도구를 카탈로그로 관리
- **MCP 통합**: [MCP 프로토콜](/aif/study/bedrock-agentic-ai-mcp) 기반 도구 서버를 지원
- **권한 제어**: IAM 정책으로 에이전트별 도구 접근 범위를 제한

## 관찰성 (Observability)

에이전트의 실행 과정을 추적하고 디버깅하는 관찰성 기능을 내장한다. 각 에이전트 호출의 추론 단계, 도구 호출, 응답 생성 과정을 상세히 기록한다.

- **트레이싱**: 에이전트 실행의 전체 흐름을 단계별로 시각화
- **메트릭**: 응답 지연 시간, 도구 호출 성공률, 토큰 사용량 등 핵심 지표 수집
- **CloudWatch 연동**: Amazon CloudWatch로 로그와 메트릭을 자동 전송

## 메모리와 컨텍스트

AgentCore는 에이전트의 장기 메모리를 관리하는 Memory 기능을 제공한다. 대화 이력과 사용자 선호도를 저장하여 개인화된 응답을 생성한다.

- **세션 메모리**: 현재 대화의 컨텍스트를 유지
- **장기 메모리**: 여러 세션에 걸친 사용자 정보를 축적
- **메모리 검색**: 관련 과거 상호작용을 자동으로 검색하여 컨텍스트에 포함

## 관련 서비스

- [에이전트 AI와 MCP](/aif/study/bedrock-agentic-ai-mcp): 에이전트 설계와 MCP 프로토콜
- [프롬프트 관리](/aif/study/bedrock-prompt-management): 프롬프트 플로우와 최적화
- [평가와 그라운딩](/aif/study/bedrock-evaluation-grounding): 에이전트 응답의 품질 평가

## 공식 출처

- [Amazon Bedrock AgentCore 개발자 안내서](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [AIF-C01 시험 범위 서비스](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html)
