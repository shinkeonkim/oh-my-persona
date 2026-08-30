# MeFit Capstone Monorepo

멀티 서비스 (backend, frontend, scraping, analysis-resume, interview-analysis-report, voice-api, infra) 를 단일 저장소에서 관리한다.

## Project-level Agents & Skills

프로젝트 전용 AI 에이전트/스킬 정의는 `.claude/` 디렉토리에 위치한다. OpenCode (oh-my-openagent) 와 Claude Code 가 모두 이 경로를 인식한다.

- `.claude/agents/*.md` — 47 개 전용 에이전트 (PM, 도메인 전문가, 개발자 등)
- `.claude/skills/<name>/SKILL.md` — 24 개 스킬 (백엔드/프론트엔드/인프라/스크래핑)
- `.claude/settings.json` — Claude Code 권한/훅 설정
- `.opencode/docs/` — 조직도, 온보딩 문서, 도메인 지식 (문서만 남김)

### 에이전트 이름 규칙

에이전트 이름은 **lowercase-hyphenated** (Claude Code 규격). 호출 예:

| 역할 | 에이전트 |
|---|---|
| CEO | `ceo` |
| CTO | `cto` |
| 백엔드 PM | `be-pm` |
| 백엔드 API 개발자 | `be-api` |
| 프론트엔드 PM | `fe-pm` |
| 분석 PM | `analysis-pm` |
| 스크래핑 PM | `scraping-pm` |
| 보이스 PM | `voice-pm` |
| 인프라 PM | `infra-pm` |
| HR | `hr-manager` |
| 기획 리드 | `product-lead` |
| MefitTools 유지보수 | `mefittools-manager` |

서브 디렉토리별 하위 에이전트는 `.claude/agents/` 를 직접 참조하거나 해당 PM 에게 문의한다.

### 호환성 노트 (OpenCode ↔ Claude Code)

- 에이전트 `name` 은 소문자, 본문 내 다른 에이전트 언급도 소문자로 통일
- `permission.skill`, `permission.tool`, `mode: subagent` 는 OpenCode 전용 필드 (Claude Code 는 무시)
- `tools: "*"` 는 Claude Code 용으로 병기 (OpenCode 는 `permission.tool` 를 사용)
- skill `compatibility: opencode` 필드는 두 툴 모두 무시 (에러 아님)

## 프로젝트별 가이드

- Backend (Django): [`backend/CLAUDE.md`](backend/CLAUDE.md)
- Frontend/Scraping/Analysis 등: 각 서브모듈 내부 CLAUDE.md 또는 README 참고

## 서브모듈

```bash
git submodule update --init --recursive
```

## 공통 명령

각 서비스 디렉토리 내부에 개별 명령이 있다. 전체 프로젝트 수준 작업은 루트 `tool.sh` 를 사용한다.
