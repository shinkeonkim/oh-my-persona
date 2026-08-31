# T18 — React 전환·Python 책임 분리·응답 지연 개선

상태: DONE (코드 검증 완료, 재배포는 사용자 요청 시 수행)
선행: T17

## 현재 기준선

- `api.py` 526줄: DTO, 인증, 라우팅, 채팅 orchestration, Admin 조회가 한 파일에 혼재
- `admin.js` 394줄, `app.css` 595줄: 상태·API·렌더링·스타일이 전역 파일에 결합
- `/api/chat/stream`은 모델 응답 완료 후 문자열을 나누므로 실제 streaming이 아님
- Strands `Agent.stream_async(..., cancel_signal=...)` 사용 가능

## 목표 구조

```text
backend/
├── pyproject.toml
├── oh_my_persona/
├── domain/          # entity, value object, repository protocol
├── application/     # chat, knowledge, conversation use case
├── infrastructure/  # PostgreSQL, corpus, LiteLLM/Strands, Discord adapter
│   └── presentation/ # FastAPI app, dependency, DTO, router
└── tests/            # Python 계층별 테스트

frontend/
├── package.json     # Bun 기반 독립 frontend project
├── bun.lock
├── src/api/         # typed HTTP/SSE client
├── src/components/  # 공통 UI
├── src/features/    # chat, admin knowledge/gaps/chunks/conversations
└── src/pages/       # ChatPage, AdminPage
└── tests/           # Vitest/Playwright
```

## 실행 순서

1. domain entity·DTO·repository protocol을 도입하고 기존 저장소를 adapter로 감싼다.
2. 300줄을 넘는 API를 public/chat/widget/admin router로 분리한다.
3. Chat use case에 timeout, cancel signal, 실제 async stream을 적용한다.
4. React+TypeScript+Vite 앱을 만들고 `/`와 `/admin`을 이전한다.
5. FastAPI는 빌드된 SPA와 SDK만 제공하고 기존 API URL은 유지한다.
6. 테스트를 domain/application/infrastructure/presentation 및 frontend feature 단위로 재배치한다.
7. Ruff, mypy, Vitest, Playwright, Docker build, 운영 E2E를 통과한다.

## 지연 예산

- 검색 p95: 500ms 이하
- SSE 연결과 source 이벤트: 1초 이내
- 모델 첫 token 목표: 5초 이내
- 모델 hard timeout: 환경변수 기본 45초
- 클라이언트 연결 종료 시 Strands cancel signal 전달

## 완료 기준

- React 이외의 정적 사용자/Admin HTML·전역 JS 렌더러를 사용하지 않는다.
- production Python 파일은 원칙적으로 300줄 미만이며 예외는 사유를 문서화한다.
- API 입력·출력은 Pydantic DTO, 내부 핵심 값은 dataclass/entity로 타입이 명시된다.
- router는 HTTP 변환, use case는 orchestration, repository는 저장만 담당한다.
- `/api/chat/stream`이 실제 model stream을 전달하고 timeout/error/cancel을 테스트한다.
- 전체 회귀 및 모바일·데스크톱 Playwright 검증 후 운영 배포한다.

## 진행 기록

- 2026-08-31: React/TypeScript/Vite 사용자·관리자 SPA와 멀티아키텍처 운영 배포 완료.
- 2026-08-31: Strands 실제 SSE, 연결 취소, 45초 hard timeout 적용.
- 2026-08-31: FastAPI composition root 527→112줄, public/chat/widget/admin router 패키지로 분리.
- 2026-08-31: domain entity/repository protocol 및 application ChatUseCase 도입.
- 2026-08-31: 테스트를 `tests/domain`, `tests/application`, UI feature 검증으로 확장.
- 2026-08-31: GitHub REST/GraphQL client, 민감정보 검사, 문서 writer를 infrastructure adapter로 분리.
- 2026-08-31: 새 domain/application/presentation 경계에 strict mypy 검사와 CI gate 적용.
- 2026-08-31: GitHub 활동·공개 문서·priority tree 수집기를 203/149/179줄 adapter로 분리.
- 2026-08-31: 모든 production Python 모듈을 300줄 이하로 제한하는 architecture test 적용.
- 2026-08-31: RateLimiter를 conversation persistence에서 infrastructure adapter로 분리.
- 2026-08-31: 루트 production 모듈을 제거하고 application/domain/infrastructure/presentation/bootstrap 패키지로 전면 이동.
- 2026-08-31: PersonaService의 persistence·LLM 직접 생성을 제거하고 composition container에서 의존성을 주입.
- 2026-08-31: Conversation PostgreSQL와 memory adapter를 물리적으로 분리하고 도메인 repository protocol로 연결.
- 2026-08-31: strict mypy 범위를 일부 16개 파일에서 전체 production 62개 파일로 확대하고 전부 통과.
- 2026-08-31: Knowledge PostgreSQL/memory, retrieval PostgreSQL/memory adapter를 물리적으로 분리.
- 2026-08-31: Admin 지식·지식 공백·대화 router를 각각 독립 모듈로 분리.
- 2026-08-31: 레거시 정적 HTML/JS/CSS fallback을 제거하고 React build만 제공하도록 통일.
- 2026-08-31: Ruff, strict mypy, Pytest 49개, Vitest, React build, Playwright 16개, Docker local build 통과.
- 재배포는 사용자 요청 전까지 보류한다.
- 2026-09-01: Python 프로젝트를 `backend/`, Bun 기반 React 프로젝트를 `frontend/`로 완전히 분리.
