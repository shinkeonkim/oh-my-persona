# RAG 챗봇 아키텍처와 배포 계획

## 선택

Strands Agents를 유지하고 그 모델 계층에 LiteLLM을 연결한다. Strands는 에이전트/도구/스트리밍을 담당하고 LiteLLM Proxy는 Provider 교체, 논리 모델, fallback, 예산과 키 격리를 담당한다. Provider를 앱 코드의 `if/else`로 늘리지 않는다.

## 흐름

```text
브라우저(모바일/PC)
  → persona.shinkeonkim.com
  → FastAPI /chat (SSE 예정)
  → query rewrite + 날짜/별칭 필터
  → PostgreSQL: FTS(BM25 계열) + pgvector
  → rerank + source diversity
  → Strands Agent
  → LiteLLM Proxy 논리 모델
  → Bedrock / OpenAI / Gemini / Ollama 등
```

벡터 검색만 쓰지 않는다. 프로젝트명·기술명·날짜는 lexical search가 강하고, 가치관·유사 경험 질문은 vector search가 강하므로 hybrid retrieval 후 reciprocal-rank fusion과 rerank를 적용한다.

## 저장 모델

- `sources`: canonical URL, publisher, 관측/발행/수정 시각, 신뢰 유형, 라이선스
- `documents`: 원문 해시, MIME, 언어, 공개 등급, 추출기 버전
- `claims`: subject-predicate-object, 유효 기간, 날짜 정밀도, 사실/자기서술/해석
- `chunks`: document/claim FK, 텍스트, section/page, token 수, content hash
- `embeddings`: chunk FK, provider/model/dimension/version; 모델별 컬렉션 분리
- `citations`: 답변에서 사용한 chunk와 공개 URL

임베딩 모델/차원이 다르면 같은 컬럼에서 fallback하지 않는다. 새 모델은 별도 버전으로 전량 생성하고 shadow 평가 후 alias를 전환한다.

## API와 보안

- 공개 API는 검색된 근거 밖의 개인정보를 반환하지 않는다.
- 관리 ingestion API는 인터넷에 노출하지 않고 homelab 내부 인증을 적용한다.
- LLM 키는 LiteLLM/Kubernetes Secret에만 두며 프론트엔드 번들에 포함하지 않는다.
- 프롬프트 인젝션을 막기 위해 수집 문서는 명령이 아닌 인용 데이터로 감싼다.
- 요청별 model alias, 검색 chunk ID, 비용, latency, citation coverage를 기록하되 질문 원문 보존 기간은 최소화한다.

## 단계별 구현

1. 현재 CLI와 JSONL로 corpus contract·검증·청킹을 고정한다.
2. PostgreSQL/pgvector migration과 hybrid retriever를 구현한다.
3. `/search`, `/chat`, `/sources/{id}` 및 SSE streaming을 구현한다.
4. 답변 근거율, temporal correctness, abstention, PII 평가를 CI에 넣는다.
5. 모바일 우선 웹 UI에 인용 카드, 시점 배지, 모델 선택(허용된 alias만)을 제공한다.
6. `oh-my-homelab`에 Deployment/Service/Ingress, cert-manager TLS, NetworkPolicy, PDB, backup을 추가해 `persona.shinkeonkim.com`으로 배포한다.

운영 배포 변경은 이 저장소에서 임의 실행하지 않는다. 해당 저장소에서 이미지 레지스트리, namespace, DNS, secret 관리 방식을 확인한 뒤 별도 변경으로 진행한다.

참고: [Strands model providers](https://strandsagents.com/docs/user-guide/concepts/model-providers/), [Strands LiteLLM provider](https://strandsagents.com/docs/user-guide/concepts/model-providers/litellm/), [Strands Python SDK](https://github.com/strands-agents/sdk-python)
