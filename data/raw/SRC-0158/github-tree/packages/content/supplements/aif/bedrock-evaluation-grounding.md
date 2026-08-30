# 모델 평가와 그라운딩

Amazon Bedrock은 파운데이션 모델(FM)의 응답 품질을 측정하고, RAG(검색 증강 생성)를 통해 사실에 기반한 응답을 생성하는 평가·그라운딩 기능을 제공한다.

## 모델 평가 (Model Evaluation)

Bedrock 모델 평가는 FM의 성능을 정량적으로 측정한다. 자동 평가와 사람 평가 두 가지 방식을 지원하며, 용도에 맞는 FM을 선택하는 근거를 제공한다.

- **자동 평가**: 정확도(Accuracy), 견고성(Robustness), 독성(Toxicity) 등 내장 지표로 자동 채점
- **사람 평가**: Amazon SageMaker Ground Truth 작업자가 응답 품질을 직접 판정
- **벤치마크 데이터셋**: 내장 데이터셋 또는 커스텀 데이터셋으로 평가 실행

## Knowledge Bases와 RAG

Amazon Bedrock Knowledge Bases는 RAG 파이프라인을 관리형으로 구현한다. 문서를 벡터로 변환하여 저장하고, 질의 시 관련 문서를 검색하여 FM의 컨텍스트로 제공한다.

- **데이터 수집**: Amazon S3, Confluence, SharePoint 등에서 문서를 자동 동기화
- **임베딩 생성**: Amazon Titan Embeddings 또는 Cohere Embed 모델로 벡터 변환
- **벡터 저장소**: Amazon OpenSearch Serverless, Amazon Aurora, Pinecone 등 지원
- **청킹 전략**: 고정 크기, 의미 기반, 계층적 청킹으로 검색 정밀도 최적화

## 그라운딩 검증

그라운딩(Grounding)은 FM 응답이 제공된 소스 문서에 기반하는지 검증하는 과정이다. Bedrock Guardrails의 그라운딩 검사(Grounding Check)가 이 역할을 수행한다.

- **사실 검증**: 응답의 각 주장이 소스 문서에서 뒷받침되는지 자동 판정
- **관련성 필터**: 검색된 문서가 질의와 실제로 관련 있는지 필터링
- **환각 감소**: 소스에 없는 정보를 생성하는 환각(hallucination)을 탐지하고 차단

## 평가 지표와 활용

모델 평가 결과는 FM 선택, 프롬프트 최적화, 파인튜닝 판단의 근거로 활용한다.

- **작업별 평가**: 텍스트 생성, 요약, 질의응답, 분류 등 작업 유형별 지표 제공
- **모델 비교**: 동일 데이터셋으로 여러 FM을 비교하여 최적 모델 선택
- **지속적 평가**: 프로덕션 환경에서 응답 품질을 모니터링하고 성능 저하 탐지

## 관련 서비스

- [Amazon Bedrock 개요](/aif/study/bedrock): FM 선택과 커스터마이징
- [프롬프트 관리](/aif/study/bedrock-prompt-management): 프롬프트 최적화와 버전 관리
- [보안과 거버넌스](/aif/study/security-governance): 가드레일과 콘텐츠 필터링

## 공식 출처

- [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [AIF-C01 시험 범위 서비스](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html)
