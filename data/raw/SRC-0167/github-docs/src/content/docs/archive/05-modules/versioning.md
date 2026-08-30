---
title: "Module 버전 관리"
description: "Legacy study material imported from 05-modules/versioning.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Semantic Versioning 이해
- Terraform Version Constraint 문법 마스터
- required_version, required_providers 활용
- .terraform.lock.hcl 파일 관리
- Version upgrade 워크플로우
- 안전한 버전 관리 전략

---

## 1. Semantic Versioning (SemVer)

### 형식

```
MAJOR.MINOR.PATCH
   |     |     |
   |     |     └── Bug fix (하위 호환)
   |     └────── New feature (하위 호환)
   └──────────── Breaking change (호환 안 됨)
```

**예시:**
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature
- `1.1.0` → `2.0.0`: Breaking change

### Pre-release

```
1.0.0-alpha
1.0.0-beta
1.0.0-rc.1
```

---

## 2. Version Constraint 문법

### 연산자

| 연산자 | 예제 | 매칭 버전 |
|--------|------|-----------|
| `=` | `= 5.1.2` | 오직 5.1.2 |
| `!=` | `!= 5.1.2` | 5.1.2 제외 모두 |
| `>` | `> 5.0.0` | 5.0.0 초과 |
| `>=` | `>= 5.0.0` | 5.0.0 이상 |
| `<` | `< 6.0.0` | 6.0.0 미만 |
| `<=` | `<= 5.9.9` | 5.9.9 이하 |
| `~>` | `~> 5.1` | 5.1.x, ..., 5.9.x (Not 6.0) |
| `~>` | `~> 5.1.0` | 5.1.0, ..., 5.1.9 (Not 5.2) |

### Pessimistic Constraint (`~>`)

**핵심 원칙:** 마지막 자리만 자유롭게 증가.

```
~> 5.1     → 5.1.x, 5.2.x, ..., 5.9.x  (Major 고정)
~> 5.1.0   → 5.1.0, 5.1.1, ..., 5.1.9  (Minor 고정)
~> 5       → 5.x.x                     (Major 만 고정)
```

### 복합 Constraint

```
>= 5.0, < 6.0                # 5.x 만
>= 5.1.0, != 5.2.0, < 6.0    # 5.1+, 5.2 제외, 6 미만
```

---

## 3. required_version (Terraform CLI)

### 정의

```hcl
terraform {
  required_version = ">= 1.12.0"
}
```

### 다양한 형태

```hcl
# 정확한 버전 (엄격)
required_version = "1.12.0"

# 이상
required_version = ">= 1.5.0"

# Pessimistic
required_version = "~> 1.5"      # 1.5.x, 1.6.x, ... (Not 2.0)

# 범위
required_version = ">= 1.5.0, < 2.0.0"
```

### 확인

```bash
terraform version
# Terraform v1.12.0

terraform init
# Terraform 1.11.0 사용 시:
# Error: Unsupported Terraform Core version
```

---

## 4. required_providers

### 기본 구조

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }
}
```

### Source 필드 이해

```
<HOSTNAME>/<NAMESPACE>/<TYPE>
```

**기본값:** `registry.terraform.io/hashicorp/aws`

**축약:** `hashicorp/aws` = `registry.terraform.io/hashicorp/aws`

**전체 형식:**
```hcl
required_providers {
  aws = {
    source  = "registry.terraform.io/hashicorp/aws"
    version = "~> 5.0"
  }
}
```

**Custom Registry:**
```hcl
required_providers {
  custom = {
    source  = "app.terraform.io/my-org/custom"
    version = "~> 1.0"
  }
}
```

---

## 5. .terraform.lock.hcl 파일

### 목적

- Provider 버전과 체크섬 고정
- 팀 전체가 **정확히 동일 버전** 사용 보장
- 무작위 upgrade 방지

### 위치

프로젝트 루트 (Git 에 커밋 필수).

### 구조

```hcl
# .terraform.lock.hcl
provider "registry.terraform.io/hashicorp/aws" {
  version     = "5.31.0"
  constraints = "~> 5.0"
  hashes = [
    "h1:...",
    "zh:abc123...",
    "zh:def456...",
    # ... platform-specific hashes
  ]
}

provider "registry.terraform.io/hashicorp/random" {
  version     = "3.5.1"
  constraints = ">= 3.0"
  hashes = [
    # ...
  ]
}
```

### 생성/업데이트 시점

```bash
terraform init              # 처음 생성
terraform init -upgrade     # 최신 버전 반영
```

### 커밋 여부

✅ **필수:** Git 에 커밋.

**이유:**
- 팀원 모두 동일 버전 사용
- CI/CD 재현성
- Supply chain security

### Multi-platform Hash

```bash
terraform providers lock \
  -platform=linux_amd64 \
  -platform=darwin_amd64 \
  -platform=windows_amd64
```

여러 OS/Arch 개발자가 있을 때 필수.

---

## 6. Module Version 관리

### 기본 사용

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}
```

### Constraint 활용

```hcl
# 정확한 버전 (프로덕션 권장)
version = "5.1.2"

# Pessimistic (일반 권장)
version = "~> 5.1"

# 최소 버전 (Module 개발자용)
version = ">= 5.0"

# 범위
version = ">= 5.0, < 6.0"
```

### Version 없이 (비권장)

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  # 항상 최신 → 예측 불가!
}
```

---

## 7. Git 기반 Module 버전

### Tag 참조

```hcl
module "vpc" {
  source = "git::https://github.com/my-org/vpc.git?ref=v1.2.0"
}
```

### Branch 참조

```hcl
module "vpc" {
  source = "git::https://github.com/my-org/vpc.git?ref=main"
}
```

⚠️ Branch 는 시간에 따라 내용 바뀜. **Tag 권장**.

### Commit Hash

```hcl
module "vpc" {
  source = "git::https://github.com/my-org/vpc.git?ref=abc123def"
}
```

### Subdirectory

```hcl
module "vpc" {
  source = "git::https://github.com/my-org/repo.git//modules/vpc?ref=v1.0.0"
}
```

---

## 8. Version Upgrade 워크플로우

### 8.1 Provider Upgrade

**Minor Update (5.30.0 → 5.31.0):**

```bash
# 1. Constraint 유지 (~> 5.0)
# 2. Lock file 업데이트
terraform init -upgrade

# 3. Plan 확인
terraform plan

# 4. 변경 없으면 apply
terraform apply
```

**Major Update (5.x → 6.0):**

```hcl
# 1. Constraint 변경
required_providers {
  aws = {
    source  = "hashicorp/aws"
    version = "~> 6.0"  # 5.0 → 6.0
  }
}
```

```bash
# 2. Changelog 확인
# https://github.com/hashicorp/terraform-provider-aws/blob/main/CHANGELOG.md

# 3. Upgrade
terraform init -upgrade

# 4. Plan
terraform plan
# Breaking changes 확인

# 5. 필요시 코드 수정
# (deprecated arguments, renamed resources 등)

# 6. Apply (dev/staging 먼저)
terraform apply
```

### 8.2 Module Upgrade

```bash
# 1. Version 변경
# module.vpc.version = "5.1.2" → "5.2.0"

# 2. Init
terraform init -upgrade

# 3. Plan
terraform plan
```

### 8.3 Terraform CLI Upgrade

```bash
# 1. Install 새 버전
brew upgrade terraform

# 2. required_version 확인
# terraform { required_version = ">= 1.12.0" }

# 3. State 형식 호환성 확인
terraform version
terraform show    # State 로드 확인

# 4. Init
terraform init -upgrade
```

⚠️ Terraform CLI 다운그레이드는 **불가능** (state schema 호환성 문제).

---

## 9. Multi-Environment Version 관리

### 시나리오

Dev/Staging/Prod 에서 서로 다른 버전 사용.

### 옵션 1: 환경별 별도 State

```
project/
├── environments/
│   ├── dev/
│   │   ├── main.tf         # ~> 5.0
│   │   └── .terraform.lock.hcl
│   ├── staging/
│   │   ├── main.tf         # ~> 5.0
│   │   └── .terraform.lock.hcl
│   └── prod/
│       ├── main.tf         # = 5.1.2 (pin)
│       └── .terraform.lock.hcl
```

### 옵션 2: Workspace 별 변수

```hcl
locals {
  aws_version = {
    dev     = ">= 5.0"
    staging = "~> 5.0"
    prod    = "= 5.1.2"
  }
}
```

⚠️ required_providers 에는 표현식 사용 불가. 이 방식은 문서화 목적.

---

## 10. 자동화된 Upgrade

### Dependabot (GitHub)

**.github/dependabot.yml:**
```yaml
version: 2
updates:
  - package-ecosystem: "terraform"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

자동으로 provider/module version PR 생성.

### Renovate

```json
{
  "extends": ["config:base"],
  "terraform": {
    "enabled": true
  }
}
```

---

## 11. 실전 예제

### 프로덕션 안전 설정

```hcl
terraform {
  required_version = "~> 1.12"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "s3" {
    bucket         = "my-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"

  # ...
}
```

### 개발 유연한 설정

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

---

## 12. Best Practices

### ✅ DO

- **모든 provider 에 version constraint 명시**
- **Pessimistic constraint (`~>`) 사용**
- **`.terraform.lock.hcl` Git 커밋**
- **Multi-platform lock (`terraform providers lock -platform=...`)**
- **Upgrade 전 Changelog 확인**
- **Dev/Staging 에서 먼저 테스트**
- **Major upgrade 는 별도 PR**

### ❌ DON'T

- Version 생략 (항상 최신)
- Lock file 을 gitignore
- 프로덕션에 pre-release 사용
- Major upgrade 를 직접 프로덕션에
- Breaking change 없이 major bump

---

## 13. 시험 자주 나오는 함정

### 함정 1: ~> 연산자 이해

```
Q: ~> 5.1 이 매칭하는 버전은?
A: 5.1.0 ~ 5.9.9 (6.0 은 제외)
   즉, 5.1 이상 6.0 미만.
```

### 함정 2: ~> 5.1.0 vs ~> 5.1

```
~> 5.1     → 5.1.0 ~ 5.9.9
~> 5.1.0   → 5.1.0 ~ 5.1.9
```

### 함정 3: lock file 은 언제 생성?

```
Q: .terraform.lock.hcl 은 언제 생성되나요?
A: terraform init 실행 시.
```

### 함정 4: lock file 커밋

```
Q: .terraform.lock.hcl 은 Git 에 커밋해야 하나요?
A: ✅ YES. 팀 재현성 위해 필수.
```

### 함정 5: 정확한 버전 지정

```
Q: 프로덕션에서는 어떻게 version 지정?
A: 정확한 버전 (= 5.1.2) 또는 pessimistic (~> 5.1.0).
   너무 넓은 constraint (>= 5.0) 는 위험.
```

### 함정 6: required_version 위반 시

```
Q: required_version = ">= 1.5" 인데 1.4.0 실행하면?
A: Error. terraform init 실패.
```

---

## 14. 요약

### Version Constraint Cheat Sheet

```hcl
version = "1.2.3"        # 정확히 1.2.3
version = "!= 1.2.3"     # 1.2.3 제외
version = ">= 1.0.0"     # 1.0.0 이상
version = "~> 1.2"       # 1.2 <= v < 2.0
version = "~> 1.2.0"     # 1.2.0 <= v < 1.3.0
version = ">= 1.0, < 2.0"  # 범위
```

### Lock file 관리

```
✅ 커밋 필수
✅ CI/CD 에서 검증
✅ Upgrade 시 -upgrade 옵션
✅ Multi-platform lock
```

### Upgrade 원칙

```
1. Changelog 확인
2. Dev → Staging → Prod
3. Plan 으로 검증
4. Lock file 업데이트
5. 팀 공유
```

---

## 참고 자료

- [Version Constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints)
- [Provider Requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Dependency Lock File](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [terraform providers lock](https://developer.hashicorp.com/terraform/cli/commands/providers/lock)
- 관련 문서: [Module 작성](/archive/05-modules/creating-modules/), [Module Registry](/archive/05-modules/registry/)
