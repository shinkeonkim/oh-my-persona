---
title: "Terraform CLI 명령어 상세 가이드"
description: "Legacy study material imported from 03-core-workflow/cli-commands.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- 모든 주요 Terraform CLI 명령어 완벽 이해
- 각 명령어의 옵션과 사용 시나리오
- Deprecated 명령어와 대체 방법
- 환경 변수 활용
- CI/CD 통합 시 알아야 할 점

---

## 1. CLI 명령어 카테고리

```
Main Commands (자주 사용):
├── init          # 초기화
├── validate      # 검증
├── fmt           # 포맷팅
├── plan          # 계획
├── apply         # 실행
└── destroy       # 정리

State & Info:
├── show          # 상태/plan 조회
├── output        # 출력값 조회
├── state         # State 조작
├── graph         # 의존성 그래프
└── providers     # Provider 정보

Others:
├── workspace     # Workspace 관리
├── import        # 기존 리소스 임포트
├── console       # 대화형 콘솔
├── force-unlock  # Lock 해제
├── login/logout  # HCP Terraform 인증
├── test          # Test framework (1.6+)
└── version       # 버전 확인
```

---

## 2. terraform init

### 목적
작업 디렉토리 초기화, Provider 다운로드, Backend 설정.

### 문법

```bash
terraform init [options]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-upgrade` | Provider/module 최신 버전으로 |
| `-reconfigure` | Backend 재구성 (state 마이그레이션 없음) |
| `-migrate-state` | State 를 새 backend 로 마이그레이션 |
| `-backend=false` | Backend 초기화 건너뜀 |
| `-backend-config=KEY=VAL` | Backend 설정 override |
| `-backend-config=FILE` | Backend 설정 파일 |
| `-get=false` | Module 다운로드 건너뜀 |
| `-input=false` | 대화형 입력 비활성화 |
| `-no-color` | 색상 비활성화 (CI/CD) |
| `-lock=false` | State locking 비활성화 |
| `-plugin-dir=DIR` | 커스텀 Provider 디렉토리 |

### 예제

```bash
# 기본
terraform init

# Provider 업데이트
terraform init -upgrade

# Backend 재구성 (마이그레이션 없음)
terraform init -reconfigure

# State 마이그레이션 (local → s3)
terraform init -migrate-state

# Partial Backend 구성
terraform init \
  -backend-config="bucket=my-tfstate" \
  -backend-config="key=prod/terraform.tfstate"

# Backend config 파일
terraform init -backend-config="prod.backend.hcl"
```

### 생성되는 파일

```
.terraform/                    # Provider 바이너리, 캐시
├── providers/
└── modules/
.terraform.lock.hcl            # Dependency lock file
```

---

## 3. terraform validate

### 목적
구성 파일 문법 검증 (원격 API 호출 없음).

### 문법

```bash
terraform validate [options]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-json` | JSON 형식 출력 |
| `-no-color` | 색상 비활성화 |

### 예제

```bash
terraform validate
# Success! The configuration is valid.

terraform validate -json
# {"format_version":"1.0","valid":true,"error_count":0,...}
```

⚠️ `validate` 는 **문법**만 검증. 실제 AWS 리소스 존재 여부는 확인 안 함.

---

## 4. terraform fmt

### 목적
코드 포맷팅 (들여쓰기, 정렬).

### 문법

```bash
terraform fmt [options] [DIR]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-list=false` | 변경된 파일 목록 미출력 |
| `-write=false` | 파일 쓰기 안 함 (미리보기) |
| `-diff` | 변경사항 diff 표시 |
| `-check` | 변경 있으면 exit 1 (CI/CD) |
| `-recursive` | 하위 디렉토리 재귀 |

### 예제

```bash
terraform fmt

# 재귀
terraform fmt -recursive

# CI/CD 에서 검증만
terraform fmt -check -recursive
if [ $? -ne 0 ]; then
  echo "코드 포맷팅 필요"
  exit 1
fi

# Diff 미리보기
terraform fmt -diff -write=false
```

---

## 5. terraform plan

### 목적
실행 계획 생성 (변경사항 미리보기).

### 문법

```bash
terraform plan [options]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-out=FILE` | Plan 을 파일로 저장 |
| `-destroy` | 삭제 계획 (`destroy -plan` 대체) |
| `-refresh-only` | 리소스 변경 없이 state refresh 만 |
| `-refresh=false` | Refresh 건너뜀 |
| `-target=ADDRESS` | 특정 리소스만 |
| `-replace=ADDRESS` | 리소스 재생성 강제 (taint 대체) |
| `-var=KEY=VAL` | Variable 값 |
| `-var-file=FILE` | Variable 파일 |
| `-parallelism=N` | 병렬 처리 개수 (기본 10) |
| `-input=false` | 대화형 입력 비활성화 |
| `-no-color` | 색상 비활성화 |
| `-json` | JSON 출력 |
| `-detailed-exitcode` | 상세 exit code |

### Detailed Exit Codes

| Code | 의미 |
|------|------|
| 0 | 변경사항 없음 |
| 1 | 에러 |
| 2 | 변경사항 있음 |

### 예제

```bash
# 기본
terraform plan

# Plan 저장
terraform plan -out=tfplan

# 특정 리소스만
terraform plan -target=aws_instance.web

# 리소스 재생성 강제
terraform plan -replace=aws_instance.web

# Variable 오버라이드
terraform plan -var="instance_type=t3.large"

# Variable file
terraform plan -var-file="prod.tfvars"

# 삭제 계획
terraform plan -destroy

# Refresh 없이
terraform plan -refresh=false

# CI/CD 활용
terraform plan -detailed-exitcode
case $? in
  0) echo "변경 없음" ;;
  1) echo "에러 발생" ;;
  2) echo "변경사항 있음" ;;
esac
```

---

## 6. terraform apply

### 목적
Plan 을 실행하여 인프라 변경.

### 문법

```bash
terraform apply [options] [PLAN_FILE]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-auto-approve` | 승인 건너뜀 |
| `-refresh-only` | Refresh 만 (변경 없음) |
| `-refresh=false` | Refresh 건너뜀 |
| `-target=ADDRESS` | 특정 리소스만 |
| `-replace=ADDRESS` | 리소스 재생성 |
| `-destroy` | 삭제 |
| `-var=KEY=VAL` | Variable |
| `-var-file=FILE` | Variable 파일 |
| `-parallelism=N` | 병렬 처리 |
| `-input=false` | 대화형 입력 비활성화 |
| `-no-color` | 색상 비활성화 |
| `-lock-timeout=DURATION` | Lock 대기 시간 |

### 예제

```bash
# 기본
terraform apply

# 자동 승인
terraform apply -auto-approve

# Plan 파일 사용
terraform apply tfplan

# 특정 리소스만
terraform apply -target=aws_s3_bucket.data

# 재생성
terraform apply -replace=aws_instance.web

# Refresh only (drift 감지 후 state 동기화)
terraform apply -refresh-only

# CI/CD
terraform apply -input=false -auto-approve -no-color

# Lock 대기
terraform apply -lock-timeout=10m
```

---

## 7. terraform destroy

### 목적
관리 중인 모든 리소스 삭제.

### 문법

```bash
terraform destroy [options]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-auto-approve` | 승인 건너뜀 |
| `-target=ADDRESS` | 특정 리소스만 |
| `-var=KEY=VAL` | Variable |
| `-var-file=FILE` | Variable 파일 |
| `-parallelism=N` | 병렬 처리 |

### 예제

```bash
terraform destroy

terraform destroy -auto-approve

terraform destroy -target=aws_instance.old
```

⚠️ 대안: `terraform apply -destroy` (동일 동작).

---

## 8. terraform show

### 목적
Terraform state 또는 plan 파일 조회.

### 문법

```bash
terraform show [options] [PATH]
```

### 예제

```bash
# 현재 state
terraform show

# JSON 형식
terraform show -json

# Plan 파일 조회
terraform plan -out=tfplan
terraform show tfplan

# Plan 파일 JSON
terraform show -json tfplan | jq .
```

---

## 9. terraform output

### 목적
Output 값 조회.

### 문법

```bash
terraform output [options] [NAME]
```

### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `-json` | JSON 출력 |
| `-raw` | Raw 값 (스크립트용) |
| `-state=FILE` | 특정 state 파일 |
| `-no-color` | 색상 비활성화 |

### 예제

```bash
# 모든 output
terraform output

# 특정 output
terraform output instance_id

# JSON
terraform output -json

# Raw (변수에 저장)
BUCKET_NAME=$(terraform output -raw bucket_name)
```

---

## 10. terraform state 명령어

### state list

```bash
terraform state list
# aws_instance.web
# aws_s3_bucket.data
# module.vpc.aws_vpc.main

terraform state list "module.vpc.*"
```

### state show

```bash
terraform state show aws_instance.web
```

### state mv

```bash
terraform state mv aws_instance.old aws_instance.new

# Module 로 이동
terraform state mv aws_instance.web module.compute.aws_instance.web
```

### state rm

```bash
terraform state rm aws_instance.legacy
```

### state pull

```bash
terraform state pull > backup.tfstate
```

### state push

```bash
terraform state push backup.tfstate
```

### state replace-provider

```bash
terraform state replace-provider \
  registry.terraform.io/-/aws \
  registry.terraform.io/hashicorp/aws
```

자세한 내용은 [State 명령어 상세](/archive/06-state/state-commands/) 참고.

---

## 11. terraform import

### 목적
기존 인프라를 State 로 가져오기.

### 문법 (Terraform 1.5+, HCL 방식 권장)

```hcl
import {
  to = aws_instance.imported
  id = "i-1234567890abcdef0"
}

resource "aws_instance" "imported" {
  # config...
}
```

```bash
# Config 자동 생성
terraform plan -generate-config-out=generated.tf
terraform apply
```

### 기존 방식 (CLI)

```bash
terraform import aws_instance.example i-1234567890abcdef0

# Module 내 리소스
terraform import module.compute.aws_instance.web i-1234567890abcdef0
```

---

## 12. terraform workspace

### 목적
CLI Workspace 관리 (HCP Workspace 와 다름!)

### 명령어

```bash
terraform workspace list          # 목록
terraform workspace new dev       # 생성
terraform workspace select prod   # 전환
terraform workspace show          # 현재
terraform workspace delete dev    # 삭제
```

### terraform.workspace 변수

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "myapp-${terraform.workspace}"
}
```

⚠️ CLI Workspace 는 **State 만 분리**. HCP Workspace 는 **완전 독립 환경**.

---

## 13. terraform providers

### 목적
Provider 정보 조회 및 관리.

```bash
# 사용 중인 Provider
terraform providers

# Provider mirror 생성
terraform providers mirror /path/to/mirror

# Lock 파일 갱신
terraform providers lock \
  -platform=linux_amd64 \
  -platform=darwin_amd64
```

---

## 14. terraform graph

### 목적
의존성 그래프 생성.

```bash
terraform graph | dot -Tpng > graph.png

# Plan 그래프
terraform plan -out=tfplan
terraform graph -plan=tfplan | dot -Tsvg > plan.svg
```

---

## 15. terraform console

### 목적
대화형 표현식 평가.

```bash
terraform console
> var.region
"us-east-1"

> length([1, 2, 3])
3

> aws_instance.web.public_ip
"54.123.45.67"

> merge({a=1}, {b=2})
{
  "a" = 1
  "b" = 2
}

# 종료: exit 또는 Ctrl+D
```

---

## 16. terraform force-unlock

### 목적
State lock 강제 해제.

```bash
terraform force-unlock <LOCK_ID>
terraform force-unlock -force <LOCK_ID>   # 확인 건너뜀
```

⚠️ **위험**: 다른 사람이 apply 중일 때 해제하면 state 손상 위험.

---

## 17. terraform login / logout

### 목적
HCP Terraform 인증.

```bash
terraform login
terraform login app.terraform.io

terraform logout
```

Token 저장 위치: `~/.terraform.d/credentials.tfrc.json`

---

## 18. terraform test (1.6+)

### 목적
Module 테스트 실행.

**example.tftest.hcl:**
```hcl
run "verify_bucket" {
  command = plan

  assert {
    condition     = aws_s3_bucket.example.bucket == "expected-name"
    error_message = "Bucket name mismatch"
  }
}
```

```bash
terraform test
terraform test -filter=example.tftest.hcl
```

---

## 19. terraform version

```bash
terraform version
# Terraform v1.12.0
# on darwin_amd64
# + provider registry.terraform.io/hashicorp/aws v5.31.0

terraform version -json
```

---

## 20. Deprecated 명령어 (시험 필수!)

| 예전 명령어 | 현재 대체 |
|------------|----------|
| `terraform taint <resource>` | `terraform apply -replace=<resource>` |
| `terraform refresh` | `terraform apply -refresh-only` |

### terraform taint (deprecated)

```bash
# 사용 금지
terraform taint aws_instance.web

# 대체
terraform apply -replace=aws_instance.web
```

### terraform refresh (deprecated)

```bash
# 사용 금지
terraform refresh

# 대체
terraform apply -refresh-only
```

---

## 21. 환경 변수

| 변수 | 목적 |
|------|------|
| `TF_LOG` | 로그 레벨 (TRACE, DEBUG, INFO, WARN, ERROR) |
| `TF_LOG_PATH` | 로그 파일 경로 |
| `TF_LOG_CORE` | Core 로그 |
| `TF_LOG_PROVIDER` | Provider 로그 |
| `TF_VAR_*` | Variable 값 |
| `TF_CLI_CONFIG_FILE` | CLI 설정 파일 |
| `TF_DATA_DIR` | `.terraform/` 위치 변경 |
| `TF_INPUT` | 대화형 입력 (false=비활성화) |
| `TF_IN_AUTOMATION` | 자동화 환경 (출력 간소화) |
| `TF_WORKSPACE` | Workspace 선택 |
| `TF_PLUGIN_CACHE_DIR` | Plugin 캐시 |

### 예제

```bash
# 디버그
export TF_LOG=DEBUG
export TF_LOG_PATH=./terraform.log
terraform apply

# CI/CD
export TF_INPUT=false
export TF_IN_AUTOMATION=true
export TF_LOG=WARN
terraform apply -auto-approve

# Variable
export TF_VAR_region="us-west-2"
export TF_VAR_instance_count=5
```

---

## 22. Exit Codes

| Command | Success | Error |
|---------|---------|-------|
| `init`, `fmt`, `validate`, `apply`, `destroy` | 0 | 1 |
| `plan` | 0 (변경 없음) | 1 (에러) |
| `plan -detailed-exitcode` | 0 (변경 없음) / 2 (변경 있음) | 1 |
| `fmt -check` | 0 (포맷됨) | 3 (포맷 필요) |

---

## 23. CI/CD 통합 팁

### 안전한 CI/CD 스크립트

```bash
#!/bin/bash
set -euo pipefail

# 자동화 환경 표시
export TF_INPUT=false
export TF_IN_AUTOMATION=true

# 초기화
terraform init -no-color

# 포맷 검증
terraform fmt -check -recursive -no-color || {
  echo "포맷 오류. terraform fmt 실행 필요."
  exit 1
}

# 문법 검증
terraform validate -no-color

# Plan
terraform plan -no-color -out=tfplan -detailed-exitcode
PLAN_EXIT=$?

case $PLAN_EXIT in
  0) echo "변경사항 없음"; exit 0 ;;
  1) echo "Plan 에러"; exit 1 ;;
  2) echo "변경사항 있음, apply 진행" ;;
esac

# Apply (PR 병합 후)
if [ "$BRANCH" = "main" ]; then
  terraform apply -no-color -auto-approve tfplan
fi
```

---

## 24. 시험 자주 나오는 명령어

### 반드시 암기

- `terraform init` (특히 `-upgrade`, `-reconfigure`, `-migrate-state`)
- `terraform plan` (`-out`, `-target`, `-refresh=false`)
- `terraform apply` (`-auto-approve`, `-refresh-only`, `-replace`)
- `terraform destroy`
- `terraform state list/show/mv/rm`
- `terraform import`
- `terraform output` (`-json`, `-raw`)

### Deprecated 알기

- `terraform taint` → `apply -replace`
- `terraform refresh` → `apply -refresh-only`

### State 관련

- `terraform state mv` - 리소스 이름 변경
- `terraform state rm` - State 에서만 제거 (실제 인프라 유지)
- `terraform force-unlock` - Lock 해제

---

## 참고 자료

- [Terraform CLI Documentation](https://developer.hashicorp.com/terraform/cli)
- [Basic CLI Features](https://developer.hashicorp.com/terraform/cli/commands)
- [Environment Variables](https://developer.hashicorp.com/terraform/cli/config/environment-variables)
- 관련 문서: [Core Workflow](/archive/03-core-workflow/readme/), [State 명령어](/archive/06-state/state-commands/)
