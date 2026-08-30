# Amazon Bedrock 프롬프트 관리

Amazon Bedrock의 프롬프트 관리(Prompt Management) 기능은 프롬프트를 체계적으로 생성, 버전 관리, 테스트할 수 있는 통합 환경을 제공한다.

## 프롬프트 플로우 (Prompt Flows)

프롬프트 플로우는 여러 파운데이션 모델(FM)과 AWS 서비스를 연결하는 시각적 워크플로우 빌더다. 각 노드는 프롬프트 실행, 조건 분기, 데이터 변환 등의 단위 작업을 수행하며, 노드 간 연결로 복잡한 생성형 AI 파이프라인을 구성한다.

- **입력/출력 노드**: 플로우의 시작과 끝을 정의
- **프롬프트 노드**: 특정 FM에 프롬프트를 전송하고 응답을 수신
- **조건 노드**: 이전 노드 출력에 따라 분기 경로를 결정
- **Lambda 노드**: AWS Lambda 함수를 호출하여 커스텀 로직 실행

## 프롬프트 버전 관리

Bedrock 콘솔에서 프롬프트를 생성하면 초안(draft) 상태로 시작한다. 초안을 확정하면 불변 버전(immutable version)이 생성되며, 이전 버전과 비교하거나 특정 버전으로 롤백할 수 있다.

- 각 버전은 고유 ARN을 가지며 API 호출 시 버전을 명시적으로 지정
- 프로덕션 배포 전 테스트 환경에서 버전별 성능을 비교 평가
- 프롬프트 템플릿에 변수(`{{variable}}`)를 삽입하여 동적 입력 처리

## 모델 평가와 프롬프트 최적화

Bedrock은 프롬프트 성능을 정량적으로 측정하는 평가 도구를 내장한다. 자동 평가(automatic evaluation)는 정확도, 독성, 견고성 등의 지표를 산출하고, 사람 평가(human evaluation)는 도메인 전문가가 응답 품질을 직접 판정한다.

- **프롬프트 최적화(Prompt Optimization)**: Bedrock이 프롬프트를 자동으로 재작성하여 FM 성능을 개선
- **추론 프로파일(Inference Profile)**: 리전 간 트래픽 분산으로 처리량 확보와 지연 시간 최적화

## 가드레일 연동

프롬프트 관리는 [Amazon Bedrock Guardrails](/aif/study/security-governance)와 통합된다. 가드레일을 프롬프트 플로우에 연결하면 입력 필터링과 출력 검증 정책을 일관되게 적용할 수 있다.

- 콘텐츠 필터: 유해 콘텐츠 차단 (혐오, 폭력, 성적 콘텐츠 등)
- 거부 주제(Denied Topics): 특정 주제에 대한 응답 거부
- 민감 정보 필터: PII(개인식별정보) 자동 마스킹

## 관련 서비스

- [Amazon Bedrock 개요](/aif/study/bedrock): FM 선택과 커스터마이징
- [에이전트 AI와 MCP](/aif/study/bedrock-agentic-ai-mcp): 에이전트 기반 자율 작업 수행
- [평가와 그라운딩](/aif/study/bedrock-evaluation-grounding): 모델 평가 및 RAG 기반 사실 검증

## 공식 출처

- [Amazon Bedrock 사용 설명서](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [AIF-C01 시험 범위 서비스](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html)
