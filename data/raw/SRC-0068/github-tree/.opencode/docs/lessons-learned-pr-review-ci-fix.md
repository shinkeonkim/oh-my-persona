# Lessons Learned: PR 생성, 코드 리뷰 적용, CI 수정 작업

> 작성일: 2026-04-17
> 작업 범위: backend PR #112, frontend PR #97, scraping PR #1

---

## 1. 작업 흐름 요약

```
pmg로 PR 설명 생성
  → gh pr create
  → 코드 리뷰 확인 후 Agent에 병렬 할당
  → Agent가 리뷰 적용 (코드 수정 + commit + push)
  → CI 실패 확인 → 원인 분석 → 수정 commit + push
  → CI 재실행 확인
```

---

## 2. 발생한 문제와 원인

### 2-1. yapf lint CI 실패

**원인**: pre-commit hook 중 `yapf`이 파일을 자동 수정했지만 수정된 파일이 staging에 포함되지 않은 채 commit됨.

**해결**:
```bash
pre-commit run yapf --all-files
git add <수정된 파일>
git commit --amend  # 또는 새 commit
git push
```

**다음 작업 시 주의**:
- commit 전 반드시 `pre-commit run --all-files` 실행 (또는 최소한 변경 파일에 대해 실행)
- pre-commit이 파일을 수정하면 "Files were modified by this hook" 메시지가 나옴 → 반드시 `git add` 후 재실행하여 Passed 확인 후 commit

---

### 2-2. 테스트 CI 실패 - 삭제된 메서드 mock 참조

**원인**: 코드 리뷰 Agent가 `_get_user_job_description_fresh` 메서드를 삭제하고 `_get_user_job_description`으로 통합했으나, 테스트 파일의 2개 테스트가 여전히 삭제된 메서드를 `patch.object`로 mock하고 있었음.

**실패 메시지**: `AttributeError: <class '...'> does not have the attribute '_get_user_job_description_fresh'`

**해결 패턴**:

메서드가 1개로 통합되고 여러 번 호출될 때, `side_effect` 리스트로 순서대로 반환값 지정:

```python
# Before (삭제된 메서드 2개 mock)
patch.object(consumer, "_get_user_job_description", return_value=initial_ujd)
patch.object(consumer, "_get_user_job_description_fresh", side_effect=[ujd_in_progress, ujd_done])

# After (단일 메서드, 호출 순서대로 side_effect)
patch.object(consumer, "_get_user_job_description",
    new=AsyncMock(side_effect=[initial_ujd, ujd_in_progress, ujd_done]))
```

**다음 작업 시 주의**:
- 코드 리뷰 Agent가 메서드를 삭제하거나 병합할 때, **테스트 파일도 함께 검토**해야 함
- Agent에게 리뷰 적용을 지시할 때 "테스트 파일의 관련 mock도 함께 수정하세요" 명시적으로 요청

---

### 2-3. 파일 들여쓰기 혼합으로 IndentationError

**원인**: 여러 번의 부분 Edit이 누적되어 파일 내에 2-space / 4-space 혼합 들여쓰기가 발생. yapf가 `IndentationError`를 발생시켜 hook 자체가 실패.

**해결**: 파일 전체를 Write 도구로 재작성. 부분 Edit 반복은 들여쓰기 일관성을 깨뜨릴 위험이 있음.

**다음 작업 시 주의**:
- 프로젝트 들여쓰기 기준(2-space) 확인 후 파일 작성
- 3회 이상 연속 Edit 시 파일 전체를 Read한 후 Write로 재작성 고려
- Edit 후 `pre-commit run --files <파일>` 으로 즉시 검증

---

## 3. Agent 병렬 작업 시 주의사항

### 리뷰 적용 Agent 할당 시

```
각 PR에 별도 Agent를 할당할 때 아래를 명시적으로 포함:
1. PR URL (리뷰 코멘트 조회용)
2. 로컬 레포 경로
3. 현재 브랜치명
4. "테스트 파일의 관련 mock도 함께 수정" 지시
5. "수정 후 pre-commit run으로 검증 후 commit/push" 지시
```

### 리뷰 적용 후 CI 확인

Agent 작업 완료 후 CI를 반드시 확인:
```bash
gh run list --repo <org>/<repo> --branch <branch> --limit 3 \
  --json status,conclusion,name,headSha
```

---

## 4. 한 번에 작업이 완료되려면

| 단계 | 빠뜨리기 쉬운 것 | 해결책 |
|------|----------------|--------|
| PR 생성 | pmg 초기화 안 됨 | `.pr-generator/` 디렉토리가 레포 루트에 있는지 먼저 확인 |
| lint CI | pre-commit 미검증 commit | commit 전 `pre-commit run --all-files` 필수 |
| 리뷰 적용 | 테스트 파일 미수정 | Agent 지시 시 테스트 수정 명시 |
| 리뷰 적용 | 들여쓰기 불일치 | Agent에게 프로젝트 들여쓰기 기준(2-space) 명시 |
| CI 확인 | 시간 지연 | push 후 60-120초 대기 후 `gh run list`로 확인 |

---

## 5. 유용한 명령어 모음

```bash
# pre-commit 전체 실행
pre-commit run --all-files

# 특정 파일만
pre-commit run --files webapp/path/to/file.py

# PR CI 상태 확인
gh run list --repo <org>/<repo> --branch <branch> --limit 5 \
  --json status,conclusion,name,headSha

# CI 실패 로그 확인
gh run view <run-id> --log-failed

# pmg로 PR 설명 생성 후 PR 생성
pmg | tail -n +2 > /tmp/pr_body.md
gh pr create --title "<title>" --body-file /tmp/pr_body.md --base develop
```
