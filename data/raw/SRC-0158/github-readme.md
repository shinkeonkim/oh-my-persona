# aws-study-site

`aws-study.shinkeonkim.com` — AWS 자격증(AIF · CLF · SAA) 학습 자료를 통합 제공하는
웹 사이트. 홈랩에서 GitOps로 배포된다.

## 목표

- AWS 자격증별 학습 노트 · 개념 정리 · 문제 유형 분석을 한 곳에서 열람
- 저작권 보호 자료(문항 원본)는 인증된 사용자만 접근
- 진도 · 오답 · 북마크 자동 저장
- 모바일 반응형, 다크/라이트 테마

## 기술 스택

TypeScript · Bun · Next.js 16 · Nest.js 11 · Tailwind CSS 4 · PostgreSQL 16 · Drizzle ORM ·
Docker · ArgoCD · Traefik · Cloudflare Tunnel.

상세: [AGENTS.md § 2](AGENTS.md#2-기술-스택-확정).

## 저장소 구조

```
apps/web            Next.js 프론트엔드
apps/api            Nest.js 백엔드 (REST + OpenAPI)
packages/content    마크다운 파서 + 저작권 필터
packages/db         Drizzle 스키마 + 마이그레이션
packages/shared     Zod 스키마 + 공통 타입
content-sources/    원본 자료 (git submodules, read-only)
docker/             Dockerfile
deploy/             Helm 차트 (Phase 7)
```

전체 구조: [AGENTS.md § 3](AGENTS.md#3-저장소-구조).

## 로컬 개발 (초기 스캐폴딩 완료 후)

```bash
git clone --recursive https://github.com/kokoa-study-room/aws-study-site.git
cd aws-study-site
bun install

# 선택 사항: 로컬 비밀값을 바꿀 때만 생성 (.env.example 기본값으로도 실행 가능)
cp .env.example .env

# 로컬 PostgreSQL 부팅
docker compose -f docker-compose.dev.yml up -d

# DB 마이그레이션 + 컨텐츠 파이프라인
bun run db:migrate
bun run content:build

# 개발 서버 (web + api 동시)
bun run dev
```

접속:
- Web: http://localhost:3000
- API: http://localhost:3001
- API Docs: http://localhost:3001/api/docs

## 관리자 부트스트랩

초기 관리자 계정을 생성(또는 갱신)한다. 이미 존재하는 이메일이면 upsert된다.

```bash
# 필수 환경 변수: DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_DISPLAY_NAME
bun run create-admin
```

상세: [운영 가이드 § 관리자 부트스트랩](docs/OPERATIONS.md#관리자-부트스트랩).

## 검증

```bash
bun run check
bun run e2e:install  # 최초 1회
bun run e2e
```

E2E는 공개 페이지, 인증, 전체 학습노트 링크, AIF/CLF/SAA 퀴즈, 대시보드와
375/768/1280px 가로 오버플로를 실제 Chromium에서 검사한다.

## 컨텐츠 원본

`content-sources/`는 다음 3개 저장소의 서브모듈:

| Cert | 저장소 | 접근 |
|---|---|---|
| SAA | `kokoa-study-room/aws-saa-sutdy-notes` | PRIVATE |
| CLF | `kokoa-study-room/clf-c02-study-notes` | PRIVATE |
| AIF | `shinkeonkim/study-aif-site` | PUBLIC |

**원본 수정 절대 금지** — 이 저장소의 코드로만 파싱 · 필터 · 렌더링한다.
자세한 규칙은 [AGENTS.md § 5](AGENTS.md#5-content-sources-절대-규칙).

## 저작권

SAA/CLF의 문제 은행 데이터는 외부 저작권 대상이라 공개하지 않는다. 사이트에서는:
- 문제 원본 · 총 문제 수 · 카테고리별 비율 · 원본 링크 → **비노출**
- 서비스 개념 · 출제 패턴 분석 · 시나리오 판별 로직 → 노출 가능

필터 정책: [AGENTS.md § 6](AGENTS.md#6-저작권-필터-packagescontentcopyright-filter).

## 배포

- 이미지: `ghcr.io/kokoa-study-room/aws-study-site-{web,api}:${SHA}` (CI가 push)
- 배포: `shinkeonkim/oh-my-homelab` 저장소에 PR → 사람 merge → ArgoCD 동기화
- 도메인: `aws-study.shinkeonkim.com` (Cloudflare Tunnel)

## 기여

1. 브랜치 생성: `feat/xxx` · `fix/xxx` · `chore/xxx`
2. `bun run check`와 `bun run e2e` 통과 확인
3. PR 생성, 템플릿 체크리스트 완료
4. Merge (main 직접 push 금지)

## 상태

**배포 준비 완료 단계.** 코드, 컨텐츠 파이프라인, DB, Docker, CI, Helm 차트가 구성되어 있다.
실제 GitHub/홈랩/Cloudflare 조작은 [배포 실행서](docs/DEPLOYMENT.md)를 따른다.

## 라이선스

MIT (예정) — 컨텐츠 원본은 각 저작자 소유. 이 도구는 파싱/UI/배포만 담당.
