# 에이전트 AI와 MCP

에이전트 AI(Agentic AI)는 사용자의 요청을 자율적으로 분석하고, 필요한 도구를 선택하여 다단계 작업을 수행하는 생성형 AI 패턴이다. Amazon Bedrock Agents는 이 패턴의 관리형 구현체다.

## Bedrock Agents 아키텍처

Bedrock Agents는 파운데이션 모델(FM)에 도구 사용 능력을 부여한다. 에이전트는 사용자 입력을 받으면 FM을 호출하여 의도를 파악하고, 정의된 액션 그룹(Action Group) 중 적절한 도구를 선택하여 실행한다.

- **오케스트레이션(Orchestration)**: FM이 ReAct(Reasoning + Acting) 방식으로 추론과 행동을 반복
- **액션 그룹**: Lambda 함수 또는 OpenAPI 스키마로 정의된 외부 API 호출
- **세션 관리**: 대화 컨텍스트를 유지하며 다중 턴 상호작용 지원

## MCP (Model Context Protocol)

MCP는 AI 모델과 외부 도구·데이터 소스 간의 표준 통신 프로토콜이다. Anthropic이 공개한 개방형 표준으로, 에이전트가 다양한 도구 서버에 일관된 방식으로 접근할 수 있게 한다.

- **MCP 서버**: 도구와 리소스를 노출하는 경량 서비스
- **MCP 클라이언트**: 에이전트가 서버에 연결하여 도구를 검색하고 호출
- **프로토콜 계층**: JSON-RPC 기반 요청/응답으로 도구 목록 조회, 실행, 결과 반환

## Knowledge Bases 연동

[Amazon Bedrock Knowledge Bases](/aif/study/bedrock-evaluation-grounding)는 에이전트에 RAG(검색 증강 생성) 능력을 부여한다. 에이전트가 질문을 받으면 Knowledge Base에서 관련 문서를 검색하고, 검색 결과를 컨텍스트로 활용하여 응답을 생성한다.

- 벡터 데이터베이스: Amazon OpenSearch Serverless, Amazon Aurora, Pinecone 등 지원
- 청킹 전략: 고정 크기, 의미 기반, 계층적 청킹으로 문서 분할
- 데이터 소스: Amazon S3, Confluence, SharePoint, Salesforce 등에서 자동 동기화

## 멀티 에이전트 협업

복잡한 워크플로우는 여러 에이전트가 협업하여 처리한다. 감독 에이전트(supervisor agent)가 하위 에이전트에게 작업을 위임하고 결과를 종합한다.

- 감독-작업자 패턴: 상위 에이전트가 하위 에이전트의 실행을 조율
- 에이전트 간 컨텍스트 전달: 이전 에이전트의 출력이 다음 에이전트의 입력으로 전달
- [Amazon Bedrock AgentCore](/aif/study/bedrock-agentcore)를 통한 에이전트 배포와 관찰성 확보

## 관련 서비스

- [프롬프트 관리](/aif/study/bedrock-prompt-management): 프롬프트 플로우와 버전 관리
- [Amazon Bedrock AgentCore](/aif/study/bedrock-agentcore): 에이전트 런타임과 인프라 관리
- [보안과 거버넌스](/aif/study/security-governance): 가드레일과 접근 제어

## 공식 출처

- [Amazon Bedrock 사용 설명서](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [AIF-C01 시험 범위 서비스](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html)
