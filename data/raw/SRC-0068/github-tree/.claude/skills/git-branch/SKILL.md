---
name: git-branch
description: GitHub Issue 기반 branch 관리 - prefix 규칙, Conventional Commits, PR workflow
compatibility: opencode
---

# Git Branch Management

## 개요

MeFit 플랫폼의 GitHub Issue 기반 branch 관리 workflow입니다.
모든 기능 개발, 버그 수정, 문서 작업은 Issue를 생성하고 해당 Issue를 기반으로 branch를 생성하여 진행합니다.

---

## Branch Prefix 규칙

| Prefix | 사용 시나리오 | 예시 |
|--------|--------------|------|
| `feature/` | 신규 기능 개발 | `feature/123-add-user-profile` |
| `hotfix/` | 긴급 버그 수정 ( producción 직접 수정) | `hotfix/456-fix-login-error` |
| `bugfix/` | 일반 버그 수정 | `bugfix/789-fix-search-filter` |
| `refactor/` | 코드 리팩토링 (기능 변경 없음) | `refactor/101-cleanup-user-service` |
| `docs/` | 문서 변경 (README, API docs 등) | `docs/202-update-api-docs` |
| `test/` | 테스트 관련 작업 | `test/303-add-user-profile-tests` |
| `chore/` | 기타 작업 (의존성 업데이트, 빌드 설정 등) | `chore/404-update-dependencies` |

### Branch 명명 규칙

```
{prefix}{issue-number}-{short-description}
```

- `issue-number`: GitHub Issue 번호
- `short-description`: 영어 또는 한국어 (영어 권장), `-`로 단어 연결

---

## 작업 시작 명령어

### 1. Issue 생성

GitHub에서 먼저 Issue를 생성합니다.

```bash
# GitHub CLI로 Issue 생성 (선택)
gh issue create --title "Add user profile feature" \
  --body "## Description\n사용자 프로필 기능을 추가합니다.\n\n## Acceptance Criteria\n- [ ] 프로필 모델 생성\n- [ ] 프로필 API 구현" \
  --label "feature"
```

### 2. Branch 생성

Issue 번호를 기반으로 branch를 생성합니다.

```bash
# 기본 branch 생성
git checkout -b feature/123-add-user-profile

# 또는 git switch (Git 2.23+)
git switch -c feature/123-add-user-profile

# 원격에서 가져오기 (다른 개발자가 만든 branch인 경우)
git checkout -b feature/123-add-user-profile origin/feature/123-add-user-profile
```

### 3. 원격에 Branch Push

```bash
# 첫 번째 push 시 -u로 upstream 설정
git push -u origin feature/123-add-user-profile
```

---

## Commit Convention

[Conventional Commits](https://www.conventionalcommits.org/) 기반의 commit 메시지 규칙입니다.

### Commit 메시지 구조

```
{type}({scope}): {description}

[optional body]

[optional footer(s)]
```

### Type 종류

| Type | 설명 | 예시 |
|------|------|------|
| `feat` | 신규 기능 추가 | `feat(user): add user profile model` |
| `fix` | 버그 수정 | `fix(auth): resolve login timeout issue` |
| `refactor` | 리팩토링 (기능 변경 없음) | `refactor(api): simplify user service` |
| `docs` | 문서 변경 | `docs(readme): update installation guide` |
| `style` | 코드 스타일 변경 (기능 변경 없음) | `style: format code with prettier` |
| `test` | 테스트 추가/수정 | `test(user): add unit tests for profile` |
| `chore` | 빌드, 의존성, 도구 등 | `chore: update node dependencies` |
| `perf` | 성능 개선 | `perf(search): optimize query performance` |
| `ci` | CI/CD 설정 변경 | `ci: add GitHub Actions workflow` |

### Scope (선택)

영역 지정:
- `user`, `auth`, `api`, `frontend`, `backend`, `db`, `infra` 등

### 예시

```bash
# 단일라인 commit
git commit -m "feat(user): add profile model and serializer"

# 멀티라인 commit (body 포함)
git commit -m "feat(api): add user profile endpoint

- GET /api/v1/users/{id}/profile
- PUT /api/v1/users/{id}/profile
- ProfileImage upload support

Closes #123"

# Issue 닫기 포함
git commit -m "fix(search): resolve filter not working issue

검색 필터가 제대로 동작하지 않는 버그를 수정했습니다.

Fixes #456"
```

---

## PR (Pull Request) 생성

### PR 생성 명령어

```bash
gh pr create \
  --title "feat(user): add user profile feature" \
  --body "$(cat <<'EOF'
## Summary
- 사용자 프로필 모델 및 API 추가
- 프로필 이미지 업로드 기능 지원

## Description
### 변경 사항
- `UserProfile` 모델 추가
- `ProfileSerializer` 생성
- `ProfileViewSet` API 구현
- 프론트엔드 프로필 페이지 컴포넌트 추가

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 수동 테스트 완료

## Checklist
- [ ] 코드 스타일 검사 통과
- [ ] 테스트 커버리지 80% 이상
- [ ] 관련 문서 업데이트

## Related Issues
Closes #123
EOF
)" \
  --base main \
  --label "feature" \
  --reviewer "reviewer1,reviewer2"
```

### PR 템플릿 (.github/pull_request_template.md)

프로젝트 루트에 `.github/pull_request_template.md`를 생성하여 일관된 PR 양식을 사용할 수 있습니다.

---

## Branch 관리 원칙

### 1. Branch 병합 순서

```
feature/123-xxx  →  develop  →  main
                       ↑
bugfix/456-yyy  ────────┘
```

- `main`: 프로덕션 브랜치
- `develop`: 개발 브랜치 (필요시)
- 기능 브랜치: Issue 기반 생성

### 2. Branch 보호 규칙

- `main` 브랜치는 직접 push 불가
- 모든 PR은 최소 1명 이상의 리뷰 필요
- CI/CD 파이프라인 통과 필수

### 3. Branch 정리

```bash
# 로컬에서 이미 병합된 branch 삭제
git branch -d feature/123-xxx

# 원격에서 이미 병합된 branch 삭제
git push origin --delete feature/123-xxx

# 병합된 branch 일괄 정리 (로컬)
git fetch -p && git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d
```

---

## 빠른 참조

### Alias 설정 (.gitconfig)

```bash
# ~/.gitconfig에 추가
[alias]
  # Issue 기반 branch 생성
  nb = "!f() { git checkout -b \"$1/$2-$3\"; }; f"
  # 예: git nb feature 123 add-login

  # Conventional commit
  cm = "!f() { git commit -m \"$1: $2\"; }; f"
  # 예: git cm feat \"add user login\"

  # Branch 삭제 (로컬 + 원격)
  bd = "!f() { git branch -d $1 && git push origin --delete $1; }; f"
```

### 일상 명령어 모음

```bash
# 1. Issue 확인
gh issue view 123

# 2. Branch 생성 및 이동
git checkout -b feature/123-add-user-profile

# 3. 변경 사항 commit
git add .
git commit -m "feat(user): add user profile model"

# 4. 원격에 push
git push -u origin feature/123-add-user-profile

# 5. PR 생성
gh pr create --title "feat: add user profile model" --body "..."

# 6. PR 확인
gh pr view 123 --web
```
