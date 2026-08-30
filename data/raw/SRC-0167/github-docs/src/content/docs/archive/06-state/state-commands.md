---
title: "terraform state 명령어 완전 가이드"
description: "Legacy study material imported from 06-state/state-commands.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- terraform state 하위 명령어 마스터
- 리소스 이름 변경 (state mv)
- 리소스 관리 해제 (state rm)
- moved / removed / import 블록 (신규 방식)
- Provider 마이그레이션 (state replace-provider)
- 실전 refactoring 워크플로우

---

## 1. terraform state 명령어 개요

### 하위 명령어

```bash
terraform state list                    # 리소스 목록
terraform state show <resource>         # 리소스 상세
terraform state mv <src> <dst>          # 이동/이름 변경
terraform state rm <resource>           # State 에서 제거
terraform state pull                    # Remote → 로컬
terraform state push <file>             # 로컬 → Remote (위험)
terraform state replace-provider <old> <new>   # Provider 변경
terraform state list -id=<ID>           # ID 로 필터
```

---

## 2. terraform state list

### 목적
State 에 있는 모든 리소스 나열.

### 문법

```bash
terraform state list [options] [ADDRESS...]
```

### 예제

```bash
# 전체 목록
terraform state list
# aws_instance.web
# aws_s3_bucket.data
# aws_vpc.main
# module.vpc.aws_vpc.main
# module.vpc.aws_subnet.public[0]
# module.vpc.aws_subnet.public[1]

# 특정 module 만
terraform state list module.vpc.*
# module.vpc.aws_vpc.main
# module.vpc.aws_subnet.public[0]
# module.vpc.aws_subnet.public[1]

# 특정 resource type
terraform state list aws_instance.*

# ID 로 조회
terraform state list -id=i-1234567890abcdef0
```

---

## 3. terraform state show

### 목적
특정 리소스의 상세 정보 조회.

### 문법

```bash
terraform state show [options] ADDRESS
```

### 예제

```bash
terraform state show aws_instance.web
# # aws_instance.web:
# resource "aws_instance" "web" {
#     ami                  = "ami-12345678"
#     id                   = "i-1234567890abcdef0"
#     instance_type        = "t3.micro"
#     public_ip            = "54.123.45.67"
#     private_ip           = "10.0.1.10"
#     tags                 = {
#         "Name" = "WebServer"
#     }
#     # ...
# }

# Module 내부
terraform state show module.vpc.aws_vpc.main
```

**JSON 형식:**
```bash
terraform state show -json aws_instance.web | jq .
```

---

## 4. terraform state mv

### 목적
State 내에서 리소스 이동/이름 변경 (실제 인프라 영향 없음).

### 문법

```bash
terraform state mv [options] SOURCE DESTINATION
```

### 4.1 리소스 이름 변경

```bash
# aws_instance.web → aws_instance.web_server
terraform state mv aws_instance.web aws_instance.web_server

# main.tf 도 함께 수정 필요
```

**main.tf 변경:**
```hcl
# Before:
resource "aws_instance" "web" { ... }

# After:
resource "aws_instance" "web_server" { ... }
```

### 4.2 리소스를 Module 로 이동

```bash
# Root → Module
terraform state mv aws_instance.web module.compute.aws_instance.web
```

**main.tf:**
```hcl
# Before:
resource "aws_instance" "web" { ... }

# After:
module "compute" {
  source = "./modules/compute"
}

# modules/compute/main.tf:
resource "aws_instance" "web" { ... }
```

### 4.3 Module 에서 Root 로 이동

```bash
terraform state mv module.old.aws_instance.web aws_instance.web
```

### 4.4 count/for_each 변경

```bash
# count [0] → for_each ["web"]
terraform state mv 'aws_instance.web[0]' 'aws_instance.web["primary"]'
```

### 4.5 Cross-State 이동

```bash
# 다른 state 파일로 이동
terraform state mv \
  -state-out=other.tfstate \
  aws_instance.web \
  aws_instance.web
```

⚠️ **주의:** 소스 state 에서 제거, 대상 state 에 추가. 백업 필수.

### 4.6 Dry Run

```bash
terraform state mv -dry-run aws_instance.old aws_instance.new
# 실제 이동 없이 결과만 표시
```

---

## 5. terraform state rm

### 목적
State 에서만 리소스 제거 (**실제 인프라는 그대로 유지**).

### 문법

```bash
terraform state rm [options] ADDRESS...
```

### 예제

```bash
# State 에서 제거
terraform state rm aws_instance.legacy

# 여러 개
terraform state rm aws_instance.legacy aws_s3_bucket.old

# Module 전체
terraform state rm 'module.old_vpc.*'
```

### 사용 시나리오

**Case 1: 리소스를 Terraform 관리에서 제외**
```bash
terraform state rm aws_instance.manual_managed
# 실제 인스턴스는 유지, Terraform 은 이제 무시
```

**Case 2: 다른 프로젝트로 이관**
```bash
# Project A 에서 제거
terraform state rm aws_vpc.shared

# Project B 에서 import
cd ../project-b
terraform import aws_vpc.shared vpc-1234567890abcdef0
```

**Case 3: 임시 리소스 정리 (실제 인프라 유지)**
```bash
terraform state rm aws_instance.test_migrations
# apply 시 재생성 X, 실제 인스턴스 유지
```

⚠️ **주의:** State rm 후 실제 인프라를 삭제하려면 AWS Console 이나 CLI 사용.

---

## 6. terraform state pull

### 목적
Remote state 를 로컬로 다운로드 (백업 용도).

### 예제

```bash
terraform state pull > backup-$(date +%Y%m%d).tfstate

# JSON 그대로 확인
terraform state pull | jq .

# 특정 리소스 확인
terraform state pull | jq '.resources[] | select(.type == "aws_instance")'
```

---

## 7. terraform state push

### 목적
로컬 state 를 remote 에 업로드 (**매우 위험**).

### 문법

```bash
terraform state push [options] PATH
```

### 예제

```bash
# 백업 복구
terraform state push backup.tfstate
```

### ⚠️ 위험성

- Remote state 를 덮어씀
- Serial 번호 불일치 시 에러
- 잘못된 state 로 인프라 불일치 발생 가능

**사용 시나리오:**
- Backup 에서 복구 (마지막 수단)
- 손상된 state 수리

**절대 하지 마세요:**
- 다른 사람의 작업 중 push
- 검증 없이 push
- 오래된 backup push

---

## 8. terraform state replace-provider

### 목적
Provider source 변경 (fork, rename, migration).

### 문법

```bash
terraform state replace-provider [options] OLD NEW
```

### 예제

```bash
# hashicorp/aws → mycompany/aws
terraform state replace-provider \
  registry.terraform.io/hashicorp/aws \
  app.terraform.io/mycompany/aws

# Deprecated provider → 새 provider
terraform state replace-provider \
  registry.terraform.io/-/aws \
  registry.terraform.io/hashicorp/aws
```

### 사용 시나리오

**Case 1: Provider fork**
```
hashicorp/aws → mycompany/aws-custom
```

**Case 2: Terraform 0.12 → 0.13 마이그레이션**
```
registry.terraform.io/-/aws → registry.terraform.io/hashicorp/aws
```

---

## 9. moved Block (Terraform 1.1+)

### 목적
`state mv` 명령어의 **선언적 대체**.

### 예제

**Before (state mv):**
```bash
terraform state mv aws_instance.web aws_instance.web_server
```

**After (moved block):**
```hcl
moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}

resource "aws_instance" "web_server" {
  # ...
}
```

**적용:**
```bash
terraform plan
# # aws_instance.web has moved to aws_instance.web_server

terraform apply
# 이동 완료
```

### 이점

- ✅ 코드에 명시 (버전 관리)
- ✅ 팀원도 자동 적용
- ✅ CI/CD 자동화
- ✅ Rollback 용이

### Module Refactoring

```hcl
# 예전: root 에 정의
# resource "aws_vpc" "main" { ... }

# 이제: module 로 이동
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}

module "network" {
  source = "./modules/network"
}
```

### count → for_each 마이그레이션

```hcl
moved {
  from = aws_instance.web[0]
  to   = aws_instance.web["primary"]
}

moved {
  from = aws_instance.web[1]
  to   = aws_instance.web["secondary"]
}

resource "aws_instance" "web" {
  for_each = { primary = "10.0.1.0", secondary = "10.0.2.0" }
  # ...
}
```

---

## 10. removed Block (Terraform 1.7+)

### 목적
State 에서 리소스 제거 (**실제 인프라 유지**), 선언적으로.

### 예제

```hcl
removed {
  from = aws_instance.legacy

  lifecycle {
    destroy = false  # 실제 인프라 유지
  }
}
```

### 이점

- ✅ `terraform state rm` 대체
- ✅ 코드로 명시
- ✅ Rollback 가능

### 옵션

```hcl
# 실제 인프라도 삭제
removed {
  from = aws_instance.old

  lifecycle {
    destroy = true
  }
}

# State 에서만 제거 (기본)
removed {
  from = aws_instance.legacy

  lifecycle {
    destroy = false
  }
}
```

---

## 11. import Block (Terraform 1.5+)

### 목적
`terraform import` 명령어의 **선언적 대체**.

### 예제

**Before (CLI):**
```bash
terraform import aws_instance.web i-1234567890abcdef0
```

**After (import block):**
```hcl
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  # ...
}
```

**적용:**
```bash
terraform plan
# # aws_instance.web will be imported

terraform apply
```

### Config 자동 생성

```hcl
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}
# resource 블록 없음
```

```bash
terraform plan -generate-config-out=generated.tf
# generated.tf 에 resource 블록 자동 생성
```

---

## 12. Deprecated 명령어

### terraform taint (Deprecated)

**Before:**
```bash
terraform taint aws_instance.web
terraform apply
```

**After:**
```bash
terraform apply -replace=aws_instance.web
```

**시험 필수:** `taint` 는 deprecated. `-replace` 사용.

### terraform refresh (Deprecated)

**Before:**
```bash
terraform refresh
```

**After:**
```bash
terraform apply -refresh-only
```

---

## 13. 실전 시나리오

### 시나리오 1: 리소스 이름 변경

**Before:**
```hcl
resource "aws_instance" "web" {
  # ...
}
```

**After (더 명확한 이름):**
```hcl
resource "aws_instance" "web_server_primary" {
  # ...
}

moved {
  from = aws_instance.web
  to   = aws_instance.web_server_primary
}
```

```bash
terraform plan
terraform apply
```

### 시나리오 2: Refactoring - Module 로 분리

**Before (모든 리소스 root 에):**
```hcl
resource "aws_vpc" "main" { ... }
resource "aws_subnet" "public" { ... }
resource "aws_subnet" "private" { ... }
```

**After (module 사용):**
```hcl
module "network" {
  source = "./modules/network"
}

moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}

moved {
  from = aws_subnet.public
  to   = module.network.aws_subnet.public
}

moved {
  from = aws_subnet.private
  to   = module.network.aws_subnet.private
}
```

### 시나리오 3: count → for_each 마이그레이션

**Before:**
```hcl
variable "instances" {
  default = ["web-01", "web-02", "web-03"]
}

resource "aws_instance" "web" {
  count = length(var.instances)
  tags = {
    Name = var.instances[count.index]
  }
}
```

**Problem:** "web-02" 만 제거 시 "web-03" 이 재생성됨 (인덱스 밀림).

**After:**
```hcl
variable "instances" {
  default = ["web-01", "web-02", "web-03"]
}

resource "aws_instance" "web" {
  for_each = toset(var.instances)
  tags = {
    Name = each.key
  }
}

moved {
  from = aws_instance.web[0]
  to   = aws_instance.web["web-01"]
}

moved {
  from = aws_instance.web[1]
  to   = aws_instance.web["web-02"]
}

moved {
  from = aws_instance.web[2]
  to   = aws_instance.web["web-03"]
}
```

### 시나리오 4: State 분리 (Multi-project)

**Project A 에서 VPC 제거:**
```hcl
removed {
  from = aws_vpc.shared

  lifecycle {
    destroy = false  # 실제 VPC 유지
  }
}
```

**Project B (Network) 에서 import:**
```hcl
import {
  to = aws_vpc.shared
  id = "vpc-1234567890abcdef0"
}

resource "aws_vpc" "shared" {
  # ...
}
```

### 시나리오 5: 손상된 State 복구

```bash
# 1. State 백업
terraform state pull > current-state.tfstate

# 2. S3 Versioning 에서 이전 버전 복구
aws s3api list-object-versions \
  --bucket my-tfstate \
  --prefix prod.tfstate

aws s3api get-object \
  --bucket my-tfstate \
  --key prod.tfstate \
  --version-id <OLD_VERSION> \
  recovered-state.tfstate

# 3. 검증
terraform show recovered-state.tfstate

# 4. Push (매우 신중히!)
terraform state push recovered-state.tfstate
```

---

## 14. Best Practices

### ✅ DO

- **moved/removed/import 블록 사용** (state 명령어 대신)
- **State 조작 전 백업** (`terraform state pull`)
- **Dry run 활용** (`-dry-run`)
- **작은 단위로 이동** (여러 리소스 한번에 X)
- **팀에 공유** (Slack, PR)
- **Plan 으로 검증** 후 apply

### ❌ DON'T

- **State 파일 직접 수정** ❌❌❌
- **다른 사람 작업 중 state push**
- **검증 없이 force-unlock 후 state 조작**
- **taint 명령어 사용** (deprecated)
- **refresh 명령어 사용** (deprecated)

---

## 15. 시험 자주 나오는 함정

### 함정 1: state rm 은 삭제?

```
Q: terraform state rm 은 실제 인프라도 삭제하나요?
A: ❌ NO. State 에서만 제거. 실제 인프라 유지.
```

### 함정 2: taint 는 살아있는가?

```
Q: terraform taint 사용해도 되나요?
A: ❌ Deprecated. terraform apply -replace=... 사용.
```

### 함정 3: refresh 대체

```
Q: terraform refresh 대체 명령어는?
A: terraform apply -refresh-only
```

### 함정 4: moved block 도입 시기

```
Q: moved block 은 언제 도입되었나요?
A: Terraform 1.1+
```

### 함정 5: import block 도입 시기

```
Q: import block 은 언제 도입되었나요?
A: Terraform 1.5+
```

### 함정 6: state mv 는 실제 인프라 변경?

```
Q: state mv 는 AWS API 를 호출하나요?
A: ❌ NO. Local state 만 조작. 실제 인프라 그대로.
```

---

## 참고 자료

- [terraform state](https://developer.hashicorp.com/terraform/cli/commands/state)
- [moved Block](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [removed Block](https://developer.hashicorp.com/terraform/language/resources/syntax#removing-resources)
- [import Block](https://developer.hashicorp.com/terraform/language/import)
- 관련 문서: [State 기본](/archive/03-core-workflow/state-basics/), [Drift Detection](/archive/06-state/drift-detection/)
- 실습: [Lab 10: State 조작 마스터](/archive/labs/lab-10-state-manipulation/readme/)
