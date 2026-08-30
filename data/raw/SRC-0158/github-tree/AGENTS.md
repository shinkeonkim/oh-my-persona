# AGENTS.md — aws-study-site 작업 규칙

이 저장소에서 일하는 사람과 코딩 에이전트(Claude Code / OpenCode / Codex 등)가
공통으로 따라야 하는 규칙. 결정 배경은 저장소 루트의 [`README.md`](README.md)와
프로젝트 계획인 상위 저장소의 `plan.md`에 있다.

---

## 1. 프로젝트 한줄 요약

`aws-study.shinkeonkim.com` 도메인에서 서비스되는 AWS 자격증 학습 사이트.
컨텐츠 원본은 `content-sources/`의 서브모듈(AIF/CLF/SAA) — 이 저장소는 파싱·저장·
UI·배포만 담당하며 **원본은 절대 수정하지 않는다**.

## 2. 기술 스택 (확정)

| 계층 | 선택 | 근거 |
|---|---|---|
| 런타임 | **Bun 1.3+** | plan.md 18번, monorepo workspaces 기본 |
| 언어 | **TypeScript strict** | 타입 안전성 하드 요구사항 |
| 프론트엔드 | **Next.js 16+ (App Router)** | SSR + SEO + 정적 페이지 혼합 |
| 백엔드 | **Nest.js 11+ (Fastify)** | plan.md 4번 명시, 모듈 구조 |
| DB | **PostgreSQL 16 + Drizzle ORM** | Bun 호환성 우수 |
| 스타일 | **Tailwind CSS 4** | plan.md 18번, study-aif-site와 동일 |
| 마크다운 | **marked + shiki** | study-aif-site 계승 |
| 검증 | **Zod v4** | Nest DTO + Drizzle 스키마 통합 |
| 인증 | **JWT (@nestjs/jwt) + argon2 해시** | plan.md 19번 |
| 린트/포맷 | **Biome** | 단일 도구, 빠름 |
| 테스트 | **Bun test** (unit) / **Playwright** (e2e) | Bun 친화 |
| 로깅 | **Pino** | Loki 수집 대응 |
| 컨테이너 | **Docker** (multi-stage) → **ghcr.io** | plan.md 18번 |
| 배포 | **ArgoCD GitOps** (via `shinkeonkim/oh-my-homelab`) | 홈랩 표준 |

## 3. 저장소 구조

```
aws-study-site/
├── apps/
│   ├── web/                    # Next.js — SSR/SSG 프론트엔드
│   └── api/                    # Nest.js — REST/OpenAPI 백엔드
├── packages/
│   ├── content/                # 마크다운 파서 + 저작권 필터 (@aws-study/content)
│   ├── db/                     # Drizzle 스키마 + 마이그레이션 (@aws-study/db)
│   └── shared/                 # Zod 스키마 + 공통 타입 (@aws-study/shared)
├── content-sources/            # git submodules (read-only)
│   ├── aws-saa-sutdy-notes/    # SAA 원본
│   ├── clf-c02-study-notes/    # CLF 원본
│   └── study-aif-site/         # AIF 원본
├── docker/                     # Dockerfile.web / Dockerfile.api
├── deploy/                     # Helm 차트 (Phase 7)
├── .github/
│   ├── workflows/              # CI (빌드 + push to ghcr.io)
│   └── pull_request_template.md
├── docker-compose.dev.yml      # 로컬 PostgreSQL 등
├── package.json                # Bun workspaces root
├── tsconfig.base.json          # 모든 workspace가 상속
├── biome.json                  # 린트 + 포맷
└── AGENTS.md · README.md · CODEOWNERS
```

## 4. 파일 길이 정책 (하드 룰)

**모든 소스 파일 · 문서 파일은 250 pure LOC 이하를 유지한다.** 200 라인 근처가
분리 검토 지점, 250 pure LOC는 절대 상한이다. 빈 줄과 주석만 있는 줄은 제외한다.

### 왜

- 리뷰 가능한 단위 유지 (한 화면에 큰 흐름이 보이도록)
- LLM 컨텍스트 · IDE 심볼 탐색 효율
- 단일 책임 원칙 자연 강제

### 분리 기준

- **파일 = 하나의 응집된 관심사**. 두 개의 서로 다른 도메인이 한 파일에 있으면 분리.
- 클래스 · 컴포넌트: 1개 파일 = 1개 export가 원칙.
- 250 pure LOC를 넘으면 **반드시** 다음 중 하나:
  - 도우미 함수/타입을 `_helpers.ts` / `types.ts`로 분리
  - 서브모듈 디렉토리 생성 (`foo.ts` → `foo/index.ts` + `foo/parse.ts` + `foo/validate.ts`)
  - 컴포넌트라면 하위 컴포넌트로 쪼개기

### 예외 (합의된 것만)

- 자동 생성 파일 (`drizzle/`, `.next/`, `dist/`)
- 원본 마크다운 (`content-sources/`)
- 스냅샷 · 픽스처 (`__snapshots__/`)

예외는 파일 상단에 `// eslint-disable-next-line-` 대신 **AGENTS.md에 사유 추가**.

## 5. content-sources/ 절대 규칙

- **서브모듈 디렉토리 내 어떤 파일도 수정 금지.** 파서 · 필터 · 렌더링은 이 저장소
  코드로만 처리한다.
- 서브모듈 커밋 고정 업데이트는 별도 PR (`chore(content): bump SAA to <sha>`).
- 서브모듈 pull 실패 시(private repo 인증 문제) 로컬 개발자는
  `git submodule update --init --recursive` + SSH 키 확인. CI는 deploy key 사용.

## 6. 저작권 필터 (packages/content/copyright-filter)

원본 마크다운을 파싱해 DB에 적재하기 전 반드시 필터를 통과해야 한다.

### 제거 대상 (자동)

- `문제 수 | \*\*\d+문제\*\*` 형태의 카테고리 카운트
- "문제 분포" 표 (숫자 컬럼 포함)
- `[예시 문제](../NN-*/....md)` 형태의 원본 문제 링크
- "N문제 풀기", "문제 은행 홈" 같은 UI 카피

### 유지 대상

- 출제 패턴 분석 (신호어, 정답 방향, 함정 오답)
- 서비스 개념 · 한줄 요약
- 시나리오 판별 로직

### 검증

- `bun run content:audit`으로 스캔 → 필터된 결과에 민감 표현 남으면 CI 실패.

## 7. 코딩 컨벤션

- **TypeScript strict 필수**. `any` · `@ts-ignore` · `as any` 금지 (예외는 PR에서 명시).
- 함수 시그니처에 반환 타입 명시 (`export function foo(): Result` — 추론 의존 금지).
- **Parse-don't-validate**: Zod로 경계에서 파싱, 내부는 타입만.
- 에러: 실패 가능한 것은 `Result<T, E>` 또는 커스텀 에러 클래스 (throw 남용 금지).
- Nest.js: DTO는 Zod 스키마 재사용 (`@aws-study/shared`).
- React: 서버 컴포넌트 우선, 클라이언트 컴포넌트는 `'use client'` 명시.

## 8. 테스트

- **커밋 전 최소 조건**: `bun run typecheck` + `bun run lint` + `bun run test`.
- 새 로직에는 최소 1개 단위 테스트.
- e2e는 주요 유저 플로우 (로그인 / 카테고리 진입 / 학습노트 열람 / 퀴즈 세션).
- `packages/content` 파서는 fixture 기반 스냅샷 테스트 필수.

## 9. 커밋 & PR

- Conventional Commits: `feat(web): ...` / `fix(api): ...` / `chore(content): ...`.
- `main` 직접 push 금지 (branch protection).
- PR 단위: 하나의 논리적 변경. 대형 refactor는 여러 PR로 쪼갠다.
- PR 템플릿의 체크리스트 (typecheck / lint / test) 모두 통과 후 리뷰 요청.

## 10. 배포 인식 (Phase 7)

- 이미지: `ghcr.io/kokoa-study-room/aws-study-site-{web,api}:${SHA}` → shinkeonkim 홈랩에서 pull
  (cross-org이므로 pull secret 필요).
- 배포 매니페스트/시크릿은 `shinkeonkim/oh-my-homelab` 저장소에 PR로 제출.
  이 저장소는 **차트 소스**만 제공 (`deploy/charts/aws-study-site/`).
- 홈랩 배포 규칙(직접 kubectl 금지, main 직접 push 금지)은 `oh-my-homelab/CLAUDE.md` 참고.

## 11. 로컬 개발 요약

```bash
git clone --recursive https://github.com/kokoa-study-room/aws-study-site.git
cd aws-study-site
bun install
docker compose -f docker-compose.dev.yml up -d   # PostgreSQL
bun run db:migrate                                # Drizzle 스키마 적용
bun run content:build                             # 원본 → DB seed
bun run dev                                       # web + api 동시 부팅
```

## 12. 규칙 우선순위

1. 이 파일 (AGENTS.md)
2. 사용자 요청
3. `plan.md` (프로젝트 헌장)
4. `oh-my-homelab/CLAUDE.md` (배포 시)

충돌 시 상위가 이긴다. 규칙 자체를 바꾸려면 PR로.
