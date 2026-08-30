---
name: pr-review-apply
description: GitHub PR 코드 리뷰 적용 - 리뷰 확인, Agent 병렬 할당, pre-commit 검증, CI 확인
compatibility: opencode
---

# PR 코드 리뷰 적용 워크플로우

## 사용 시점
- GitHub PR에 코드 리뷰 코멘트가 달렸을 때
- 여러 PR(backend/frontend/scraping)을 동시에 처리할 때
- 리뷰 적용 후 CI가 실패했을 때

---

## Step 1. 리뷰 코멘트 조회

```bash
# PR 리뷰 코멘트 확인
gh pr view <PR_NUMBER> --repo <org>/<repo> --comments

# 또는 리뷰 상세
gh api repos/<org>/<repo>/pulls/<PR_NUMBER>/reviews
gh api repos/<org>/<repo>/pulls/<PR_NUMBER>/comments
```

---

## Step 2. Agent 병렬 할당 (여러 PR 동시 처리)

각 PR에 별도 Agent를 할당할 때 지시문에 반드시 포함:

```
- PR URL
- 로컬 레포 경로 (예: /Users/koa/006-capstone-modules/backend)
- 현재 브랜치명
- "테스트 파일의 관련 mock/fixture도 함께 수정"
- "수정 후 pre-commit run으로 검증 후 commit/push"
- 프로젝트 들여쓰기 기준 (예: 2-space)
```

---

## Step 3. pre-commit 검증 (commit 전 필수)

```bash
# 변경된 파일 검증
pre-commit run --files <파일경로>

# 전체 검증
pre-commit run --all-files

# hook이 파일을 수정하면 → git add 후 재실행
git add <수정된 파일>
pre-commit run --files <파일경로>
# → 모든 hook Passed 확인 후 commit
```

### yapf 들여쓰기 오류 발생 시
```bash
# IndentationError 발생 → 파일 전체 재작성
# 혼합 들여쓰기(2-space + 4-space)가 원인인 경우가 많음
# Edit 반복 대신 파일 전체를 Read → Write로 재작성
```

---

## Step 4. commit & push

```bash
git add <수정된 파일들>
git commit -m "fix: <변경 내용 요약>"
git push
```

---

## Step 5. CI 확인

```bash
# push 후 60-120초 대기 후 확인
sleep 60
gh run list --repo <org>/<repo> --branch <branch> --limit 3 \
  --json status,conclusion,name,headSha | python3 -c "
import sys, json
runs = json.load(sys.stdin)
for r in runs:
    print(r['headSha'][:7], '|', r['name'], '|', r['status'], '|', r.get('conclusion') or 'pending')
"

# 실패 시 로그 확인
gh run view <run-id> --log-failed
```

---

## 체크리스트

- [ ] PR 리뷰 코멘트 전체 확인
- [ ] 소스 파일 수정
- [ ] **테스트 파일의 mock/fixture 연동 수정** (메서드 삭제/변경 시)
- [ ] `pre-commit run` → Passed 확인
- [ ] commit & push
- [ ] CI 성공 확인

---

## 자주 발생하는 CI 실패 패턴

### 1. yapf lint 실패
- pre-commit이 파일 수정 → git add 없이 commit
- 해결: `pre-commit run --all-files` → git add → 재실행 → Passed → commit

### 2. 테스트 AttributeError (삭제된 메서드 mock)
- 리뷰로 메서드가 삭제/병합됐는데 테스트에 여전히 patch.object로 참조
- 해결: 단일 메서드에 `side_effect` 리스트로 순서별 반환값 지정
```python
# 메서드가 N번 호출되는 경우
AsyncMock(side_effect=[return1, return2, return3])
```

### 3. 들여쓰기 혼합 IndentationError
- 부분 Edit 반복으로 2-space / 4-space 혼재
- 해결: 파일 전체 Read → Write 재작성 (2-space 기준)
