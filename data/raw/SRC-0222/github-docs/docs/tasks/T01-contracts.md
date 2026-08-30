# T01 — 계약과 결정

상태: DONE
실행: 순차
선행: T00

## 결정

- JSONL은 사람이 검토하고 Git으로 추적하는 control plane이다.
- PostgreSQL은 운영 query plane이며 JSONL로부터 멱등 동기화한다.
- 검색은 lexical/vector를 RRF로 합성한다.
- 생성 모델은 Strands, Provider 라우팅은 LiteLLM Proxy가 담당한다.
- 공개 답변은 URL 인용을 강제하고 근거 부족 시 답변을 보류한다.

## 완료 증거

- `data/registry/sources.jsonl`, `data/curated/claims.jsonl`
- `migrations/001_initial.sql`
- `src/oh_my_persona/models.py`
