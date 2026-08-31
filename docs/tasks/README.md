# 실행 작업 그래프

기준일: 2026-08-28. 상태는 `TODO`, `DOING`, `DONE`, `BLOCKED` 중 하나다.

```text
T00 기준선
 ├─ T01 task/계약 ─┬─ T02 안전 수집 ─┬─ T04 corpus build ─ T06 hybrid search ─┐
 │                 └─ T03 DB schema ─┘                                      ├─ T08 통합
 └─ T05 자료 조사 seed ──────────────────────────────────────────────────────┘
                                      T06 ─┬─ T07A RAG API ─┐
                                            └─ T07B Web UI ──┤
                                                            ├─ T09 평가/CI
                                                            └─ T10 배포 패키지
```

| ID | 상태 | 실행 | 선행 | 산출물/완료 기준 |
|---|---|---|---|---|
| T00 | DONE | 순차 | - | 기존 3,000줄, resume, portfolio, homelab 규약 조사 |
| T01 | DONE | 순차 | T00 | 작업 그래프, 데이터 계약, ADR |
| T02 | DONE | 병렬 A | T01 | ZIP/PDF/MD inbox 검사·추출·격리·manifest |
| T03 | DONE | 병렬 B | T01 | PostgreSQL/pgvector migration과 저장 계보 |
| T04 | DONE | 순차 | T02,T03 | source/document/claim/chunk build 및 exact dedupe |
| T05 | DONE | 병렬 C | T01 | URL·관측일·동일인 근거를 가진 seed corpus |
| T06 | DONE | 순차 | T04,T05 | 메모리 lexical + PostgreSQL hybrid/RRF 검색 |
| T07A | DONE | 병렬 A | T06 | `/search`, `/sources`, `/chat`, `/chat/stream` |
| T07B | DONE | 병렬 B | T06 | 반응형 웹 UI, 시점·인용 카드, 모델 alias 선택 |
| T08 | DONE | 순차 | T07A,T07B | Strands+LiteLLM RAG 연결, 근거 없는 응답 abstain |
| T09 | DONE | 병렬 A | T08 | corpus/API/retrieval/evaluation 테스트와 CI |
| T10 | DONE | 병렬 B | T08 | Docker, Compose, K8s, homelab handoff |
| T11 | DONE | 운영 | T09,T10 | 21,211 청크, 역추적 99.87%, 검색 평가 통과 |
| T12 | DONE | 순차 | T11 | 서버 대화 이력, API 속도 제한, 본인 인터뷰 워크플로 배포·검증 |
| T13 | DONE | 순차 | T12 | 1인칭 존댓말, 관리자 지식 CRUD·대화 조회, 메신저 UI 배포·검증 |
| T14 | DONE | 순차 | T13 | Playwright 기반 메신저 UI 재설계·시각 회귀·운영 검증 |
| T15 | DONE | 순차+병렬 | T14 | 응답 Markdown·페르소나 이탈 차단·GitHub 프로젝트 근거 확장 |
| T16 | DOING | 순차+병렬 | T15 | 임베드 SDK, 서명 세션, Discord Forum 비동기 상담, portfolio/resume 통합 |
| T17 | DOING | 반복 | T16 | 추천 질문 기반 지식 공백 측정, 직접 답변, 재평가 루프 |
| T18 | DONE | 순차 | T17 | React·TypeScript 전환, Python 계층 분리, 실제 SSE와 지연 개선 |

T11은 2만 청크 품질 게이트까지 실행됐다. T12는 대화 맥락을 PostgreSQL에 저장하고 공개
API를 보호하며, 질문지 답변을 검토 가능한 1인칭 자료로 승격한다. 구체적인 절차는
[T11](T11-corpus-and-production.md)과 [T12](T12-conversations-and-interview.md)에 있다.
외부 사이트 위젯과 Discord 상담 연결은 [T16](T16-embed-sdk-and-discord-forum.md)에 있다.
질문으로 빈 지식 영역을 찾고 보강하는 반복 과정은 [T17](T17-knowledge-gap-loop.md)에 있다.

## 공통 Definition of Done

1. 모든 파생 데이터는 원 source URL과 content hash로 역추적된다.
2. 날짜가 없는 자료에 날짜를 추정해서 넣지 않는다.
3. 동명이인 자료는 strong identity signal 두 개 미만이면 자동 채택하지 않는다.
4. 비밀·PII 의심 자료는 격리되고 검색 대상이 되지 않는다.
5. `persona validate`, `pytest`, `ruff check`를 통과한다.
