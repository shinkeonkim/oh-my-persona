# 보안과 거버넌스

AWS의 AI 서비스 보안은 공동 책임 모델(Shared Responsibility Model)을 따른다. AWS가 인프라 보안을 담당하고, 고객이 데이터 보호와 접근 제어를 관리한다. Amazon Bedrock은 이를 위한 전용 보안·거버넌스 도구를 제공한다.

## Amazon Bedrock Guardrails

Guardrails는 FM의 입력과 출력을 실시간으로 필터링하는 안전장치다. 애플리케이션 요구사항에 맞는 정책을 정의하고, 모든 FM 호출에 일관되게 적용한다.

- **콘텐츠 필터**: 혐오, 폭력, 성적 콘텐츠, 모욕 등 유해 카테고리별 차단 강도 설정
- **거부 주제(Denied Topics)**: 특정 주제에 대한 응답을 명시적으로 거부
- **단어 필터**: 금지어 목록과 정규식 패턴으로 부적절한 표현 차단
- **민감 정보 필터**: PII(개인식별정보)를 자동 탐지하고 마스킹 또는 차단
- **그라운딩 검사**: [RAG 응답](/aif/study/bedrock-evaluation-grounding)이 소스 문서에 기반하는지 검증

## IAM 접근 제어

AWS Identity and Access Management(IAM)로 AI 서비스에 대한 세분화된 접근 제어를 구현한다.

- **모델 접근 정책**: 특정 FM에 대한 호출 권한을 사용자·역할별로 제한
- **리소스 기반 정책**: Knowledge Base, 에이전트, 가드레일 등 리소스별 접근 범위 설정
- **서비스 역할**: 에이전트가 Lambda, S3 등 다른 AWS 서비스에 접근할 때 최소 권한 원칙 적용
- **VPC 엔드포인트**: PrivateLink를 통해 퍼블릭 인터넷을 거치지 않고 Bedrock API 호출

## 데이터 보호

Bedrock은 고객 데이터의 기밀성과 무결성을 보장하는 다층 보호 체계를 갖춘다.

- **전송 중 암호화**: TLS 1.2 이상으로 모든 API 통신 암호화
- **저장 시 암호화**: AWS KMS 관리형 키 또는 고객 관리형 키(CMK)로 데이터 암호화
- **모델 커스터마이징 격리**: 파인튜닝 데이터는 고객 전용 환경에서 처리되며 다른 고객과 공유되지 않음
- **데이터 사용 정책 확인**: 기본 배포에서는 고객 콘텐츠를 통제하지만, 모델별 데이터 공유·보존 모드를 확인해야 함

## 규정 준수와 감사

AWS AI 서비스는 주요 규정 준수 프레임워크를 충족하며, 감사 추적을 위한 도구를 제공한다.

- **AWS CloudTrail**: 모든 Bedrock API 호출을 기록하여 감사 추적 제공
- **모델 호출 로깅**: FM 입출력을 Amazon S3 또는 CloudWatch Logs에 저장
- **규정 준수 인증**: SOC, ISO 27001, HIPAA, FedRAMP 등 주요 인증 획득
- **책임 있는 AI 정책**: [책임 있는 AI](/aif/study/responsible-ai) 원칙에 따른 공정성, 투명성, 설명 가능성 확보

## 관련 서비스

- [Amazon Bedrock 개요](/aif/study/bedrock): FM 선택과 서비스 아키텍처
- [에이전트 AI와 MCP](/aif/study/bedrock-agentic-ai-mcp): 에이전트 보안과 도구 접근 제어
- [책임 있는 AI](/aif/study/responsible-ai): 공정성, 편향 감지, 설명 가능성

## 공식 출처

- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Amazon Bedrock 보안](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Amazon Bedrock 데이터 보존](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)
- [AIF-C01 시험 안내](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html)
