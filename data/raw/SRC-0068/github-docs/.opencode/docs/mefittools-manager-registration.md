# mefittools-manager Agent 등록 보고

> 업데이트: 유지보수 중심 역할 정의 반영 (2026-04-17)

## 역할 재정의 요약

mefittools-manager는 단순 실행 담당이 아니라, **mefit-tools 유지보수 책임자**로 재정의되었습니다.

### 핵심 변경점

1. **운영 안정성 중심**
   - Docker/Compose 제어 신뢰성, 오류 분류, 경로/권한 진단 강화

2. **구조적 유지보수성 강제**
   - GUI 모듈 경계(app.py / docker_ops.py / dashboard.py / logs_view.py) 준수
   - app.py 비대화 금지 정책

3. **문서 동기화 책임 포함**
   - 변경 시 README와 운영 문서 동시 업데이트를 Done 기준에 포함

4. **검증 표준화**
   - py_compile, GUI 재기동, 안전 curl 헬스체크를 최소 검증 세트로 정의

## 현재 기준 문서

- Agent 정의: `.opencode/agents/mefittools-manager.md`
- 운영 문서: `mefit-tools/README.md`
- 유지보수 규칙: 본 문서 + agent 문서

## 등록 상태

| 항목 | 상태 |
|------|------|
| Agent 파일 존재 | ✅ `.opencode/agents/mefittools-manager.md` |
| mode 설정 | ✅ `subagent` 추가 |
| YAML 포맷 유효성 | ✅ 확인 완료 |

## 현재 동작 방식

OpenCode는 `.opencode/agents/` 디렉토리의 Markdown 파일을 자동으로 로드합니다:
- 파일명이 Agent 이름이 됩니다 (`mefittools-manager.md` → `mefittools-manager`)
- frontmatter에 `name`, `description`, `mode`, `permission` 등을 정의합니다
- 파일이 존재하면 다음 세션 시작 시 자동 인식됩니다

## 세션에서 사용 불가한 이유

현재 세션에서 `mefittools-manager` agent type이 인식되지 않는 이유는:

1. **OpenCode는 시작 시 에이전트를 한 번 로드**하고 이후 변경을 감지하지 않음
2. **새로 추가된 Agent는 새 세션을 시작해야 사용 가능**

## 해결 방법

### 방법 1: 새 세션 시작 (권장)
- 현재 세션을 종료하고 새 세션을 시작
- 세션 시작 시 `.opencode/agents/` 디렉토리 스캔
- `mefittools-manager` agent 자동 인식

### 방법 2:-opencode command 사용
```bash
# 새 세션에서 agent 확인
opencode agents list
```

## 테스트 결과

| 테스트 | 결과 |
|--------|------|
| 파일 존재 확인 | ✅ |
| frontmatter 유효성 | ✅ |
| mode 필드 추가 | ✅ |
| 세션 로드 (새 세션 필요) | ⏳ |

## 다음 단계

1. **새 세션 시작** - `mefittools-manager` agent 인식 확인
2. **@mefittools-manager** 형태로 서브에이전트 호출 가능
3. infra-pm 또는 ceo가 이 에이전트를 작업 지시자로 사용 가능
