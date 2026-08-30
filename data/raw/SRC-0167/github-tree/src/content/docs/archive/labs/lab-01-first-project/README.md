---
title: "Lab 01: 첫 번째 Terraform 프로젝트"
description: "Legacy study material imported from labs/lab-01-first-project/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟢 Beginner  
**소요 시간:** 30-45분  
**시험 도메인:** Core Terraform Workflow (16%)

### 학습 목표

이 실습을 완료하면 다음을 할 수 있습니다:
- ✅ Terraform 기본 워크플로우 이해 (`init → plan → apply → destroy`)
- ✅ 간단한 리소스 생성 및 관리
- ✅ State 파일의 역할 파악
- ✅ Terraform 구성 파일 (.tf) 작성

### 실습 시나리오

AWS S3 Bucket을 Terraform으로 생성하고 관리하는 기본 워크플로우를 익힙니다.

---

## 🔧 사전 준비

### 필수 요구사항

1. **Terraform 설치 (1.12 이상)**
   ```bash
   terraform version
   # Terraform v1.12.0 이상
   ```

2. **AWS CLI 설정**
   ```bash
   aws configure
   # AWS Access Key ID: [YOUR_ACCESS_KEY]
   # AWS Secret Access Key: [YOUR_SECRET_KEY]
   # Default region: us-east-1
   # Default output format: json
   ```

3. **텍스트 에디터**
   - VS Code (권장)
   - Vim, Nano, Sublime 등

### 디렉토리 구조

```
lab-01-first-project/
├── README.md           # 이 파일
├── instructions/
│   └── step-by-step.md # 단계별 지침
├── starter/
│   └── .gitkeep        # 시작 템플릿 (빈 디렉토리)
└── solution/
    ├── main.tf         # 완성된 솔루션
    ├── providers.tf
    └── outputs.tf
```

---

## 📖 단계별 실습

### Step 1: 작업 디렉토리 생성 (2분)

```bash
# 실습 디렉토리 생성
mkdir -p ~/terraform-labs/lab-01
cd ~/terraform-labs/lab-01

# 현재 디렉토리 확인
pwd
```

**예상 출력:**
```
/Users/yourname/terraform-labs/lab-01
```

---

### Step 2: Provider 설정 (5분)

**파일 생성: `providers.tf`**

```bash
cat > providers.tf << 'EOF'
terraform {
  required_version = ">= 1.12.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
EOF
```

**설명:**
- `required_version`: Terraform 버전 제약
- `required_providers`: 사용할 Provider 및 버전
- `provider "aws"`: AWS Provider 설정 (리전 지정)

**파일 확인:**
```bash
cat providers.tf
```

---

### Step 3: Terraform 초기화 (3분)

```bash
terraform init
```

**예상 출력:**
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.31.0...
- Installed hashicorp/aws v5.31.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!
```

**확인:**
```bash
# .terraform 디렉토리 생성 확인
ls -la

# Lock 파일 확인
cat .terraform.lock.hcl
```

**생성된 파일/디렉토리:**
- `.terraform/` - Provider 플러그인 저장
- `.terraform.lock.hcl` - Dependency lock file

---

### Step 4: S3 Bucket 리소스 정의 (5분)

**파일 생성: `main.tf`**

```bash
cat > main.tf << 'EOF'
# S3 Bucket 리소스
resource "aws_s3_bucket" "my_first_bucket" {
  bucket = "terraform-lab-01-bucket-YOUR_INITIALS-20260720"

  tags = {
    Name        = "My First Terraform Bucket"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}

# Bucket Versioning 활성화
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.my_first_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
EOF
```

**⚠️ 중요:**
- `bucket` 이름은 **전 세계적으로 고유**해야 합니다
- `YOUR_INITIALS`를 본인 이니셜로 변경 (예: `jhk`)
- 날짜도 현재 날짜로 변경

**수정 예시:**
```bash
# 에디터로 main.tf 열기
nano main.tf

# bucket 이름 변경
bucket = "terraform-lab-01-bucket-jhk-20260720"
```

---

### Step 5: 구성 검증 (3분)

**1. 포맷팅 확인:**
```bash
terraform fmt
```

**예상 출력:** (변경된 파일이 있으면 표시)
```
main.tf
providers.tf
```

**2. 구성 검증:**
```bash
terraform validate
```

**예상 출력:**
```
Success! The configuration is valid.
```

**오류 발생 시:**
```bash
Error: Invalid reference

  on main.tf line 15, in resource "aws_s3_bucket_versioning" "versioning":
  15:   bucket = aws_s3_bucket.my_first_bucket.id
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# 해결: 리소스 이름 확인, 구문 오류 수정
```

---

### Step 6: 실행 계획 생성 (5분)

```bash
terraform plan
```

**예상 출력:**
```
Terraform used the selected providers to generate the following execution plan.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_s3_bucket.my_first_bucket will be created
  + resource "aws_s3_bucket" "my_first_bucket" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "terraform-lab-01-bucket-jhk-20260720"
      + bucket_domain_name          = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags                        = {
          + "Environment" = "Learning"
          + "ManagedBy"   = "Terraform"
          + "Name"        = "My First Terraform Bucket"
        }
      + tags_all                    = {
          + "Environment" = "Learning"
          + "ManagedBy"   = "Terraform"
          + "Name"        = "My First Terraform Bucket"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)
    }

  # aws_s3_bucket_versioning.versioning will be created
  + resource "aws_s3_bucket_versioning" "versioning" {
      + bucket = (known after apply)
      + id     = (known after apply)

      + versioning_configuration {
          + mfa_delete = (known after apply)
          + status     = "Enabled"
        }
    }

Plan: 2 to add, 0 to change, 0 to destroy.
```

**Plan 출력 기호:**
- `+` : 생성될 리소스
- `~` : 수정될 리소스
- `-` : 삭제될 리소스
- `-/+` : 재생성될 리소스 (삭제 후 생성)

**Plan 저장 (선택):**
```bash
terraform plan -out=tfplan

# 저장된 plan 확인
terraform show tfplan
```

---

### Step 7: 인프라 생성 (5분)

```bash
terraform apply
```

**대화형 프롬프트:**
```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes    # 'yes' 입력
```

**자동 승인 (주의해서 사용):**
```bash
terraform apply -auto-approve
```

**예상 출력:**
```
aws_s3_bucket.my_first_bucket: Creating...
aws_s3_bucket.my_first_bucket: Creation complete after 2s [id=terraform-lab-01-bucket-jhk-20260720]
aws_s3_bucket_versioning.versioning: Creating...
aws_s3_bucket_versioning.versioning: Creation complete after 1s [id=terraform-lab-01-bucket-jhk-20260720]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

---

### Step 8: State 파일 확인 (5분)

**State 파일 생성 확인:**
```bash
ls -la terraform.tfstate*
```

**출력:**
```
-rw-r--r--  1 user  staff  1234 Jul 20 10:00 terraform.tfstate
```

**State 내용 확인:**
```bash
cat terraform.tfstate | jq '.'

# 또는
terraform show
```

**State의 주요 정보:**
```json
{
  "version": 4,
  "terraform_version": "1.12.0",
  "serial": 1,
  "lineage": "...",
  "outputs": {},
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "my_first_bucket",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 0,
          "attributes": {
            "id": "terraform-lab-01-bucket-jhk-20260720",
            "arn": "arn:aws:s3:::terraform-lab-01-bucket-jhk-20260720",
            "bucket": "terraform-lab-01-bucket-jhk-20260720",
            "region": "us-east-1",
            "tags": {
              "Environment": "Learning",
              "ManagedBy": "Terraform",
              "Name": "My First Terraform Bucket"
            }
          }
        }
      ]
    }
  ]
}
```

**State 조회 명령어:**
```bash
# 모든 리소스 목록
terraform state list

# 출력:
# aws_s3_bucket.my_first_bucket
# aws_s3_bucket_versioning.versioning

# 특정 리소스 상세 정보
terraform state show aws_s3_bucket.my_first_bucket
```

---

### Step 9: 실제 인프라 확인 (3분)

**AWS CLI로 확인:**
```bash
# S3 Bucket 목록
aws s3 ls | grep terraform-lab-01

# Bucket 상세 정보
aws s3api get-bucket-versioning \
  --bucket terraform-lab-01-bucket-jhk-20260720
```

**AWS Console 확인:**
1. https://console.aws.amazon.com/s3 접속
2. "terraform-lab-01-bucket-..." 검색
3. Bucket 속성 확인:
   - Tags 확인
   - Versioning 상태 확인 (Enabled)

---

### Step 10: Outputs 추가 (5분)

**파일 생성: `outputs.tf`**

```bash
cat > outputs.tf << 'EOF'
output "bucket_id" {
  description = "The name of the bucket"
  value       = aws_s3_bucket.my_first_bucket.id
}

output "bucket_arn" {
  description = "The ARN of the bucket"
  value       = aws_s3_bucket.my_first_bucket.arn
}

output "bucket_region" {
  description = "The region of the bucket"
  value       = aws_s3_bucket.my_first_bucket.region
}
EOF
```

**Apply로 outputs 활성화:**
```bash
terraform apply -auto-approve
```

**Outputs 확인:**
```bash
terraform output
```

**예상 출력:**
```
bucket_arn    = "arn:aws:s3:::terraform-lab-01-bucket-jhk-20260720"
bucket_id     = "terraform-lab-01-bucket-jhk-20260720"
bucket_region = "us-east-1"
```

**특정 output만 조회:**
```bash
terraform output bucket_arn

# 출력:
# "arn:aws:s3:::terraform-lab-01-bucket-jhk-20260720"

# JSON 형식으로
terraform output -json
```

---

### Step 11: 리소스 수정 (5분)

**main.tf 수정:**
```bash
nano main.tf
```

**Tags에 새 태그 추가:**
```hcl
resource "aws_s3_bucket" "my_first_bucket" {
  bucket = "terraform-lab-01-bucket-jhk-20260720"

  tags = {
    Name        = "My First Terraform Bucket"
    Environment = "Learning"
    ManagedBy   = "Terraform"
    Lab         = "Lab-01"           # 새로운 태그
    Updated     = "2026-07-20"        # 새로운 태그
  }
}
```

**변경 사항 확인:**
```bash
terraform plan
```

**예상 출력:**
```
aws_s3_bucket.my_first_bucket: Refreshing state... [id=terraform-lab-01-bucket-jhk-20260720]

Terraform will perform the following actions:

  # aws_s3_bucket.my_first_bucket will be updated in-place
  ~ resource "aws_s3_bucket" "my_first_bucket" {
        id                          = "terraform-lab-01-bucket-jhk-20260720"
      ~ tags                        = {
          + "Lab"         = "Lab-01"
          + "Updated"     = "2026-07-20"
            # (3 unchanged elements hidden)
        }
      ~ tags_all                    = {
          + "Lab"         = "Lab-01"
          + "Updated"     = "2026-07-20"
            # (3 unchanged elements hidden)
        }
        # (8 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

**변경 적용:**
```bash
terraform apply -auto-approve
```

---

### Step 12: 인프라 삭제 (Cleanup) (3분)

**⚠️ 중요: 실습 후 반드시 리소스 삭제**

```bash
terraform destroy
```

**확인 프롬프트:**
```
Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes    # 'yes' 입력
```

**예상 출력:**
```
aws_s3_bucket_versioning.versioning: Destroying... [id=terraform-lab-01-bucket-jhk-20260720]
aws_s3_bucket_versioning.versioning: Destruction complete after 1s
aws_s3_bucket.my_first_bucket: Destroying... [id=terraform-lab-01-bucket-jhk-20260720]
aws_s3_bucket.my_first_bucket: Destruction complete after 2s

Destroy complete! Resources: 2 destroyed.
```

**검증:**
```bash
# State 확인 (빈 리소스)
terraform state list
# (아무것도 출력되지 않음)

# AWS CLI로 확인
aws s3 ls | grep terraform-lab-01
# (없음)
```

---

## ✅ 실습 검증

### 체크리스트

- [ ] `terraform init` 성공적으로 실행
- [ ] `.terraform.lock.hcl` 파일 생성됨
- [ ] `terraform validate` 통과
- [ ] `terraform plan` 에서 2개 리소스 생성 예정 확인
- [ ] `terraform apply` 성공 (2 added)
- [ ] `terraform.tfstate` 파일 생성 확인
- [ ] AWS Console에서 S3 Bucket 확인
- [ ] `terraform output` 에서 3개 값 출력 확인
- [ ] Tags 수정 후 `terraform plan` 에서 변경 감지
- [ ] `terraform destroy` 성공 (2 destroyed)
- [ ] AWS Console에서 Bucket 삭제 확인

---

## 🎯 학습 포인트

### 1. Terraform Core Workflow

```
Write → Init → Validate → Plan → Apply → Destroy
```

| 단계 | 명령어 | 설명 |
|------|--------|------|
| Write | (에디터) | .tf 파일 작성 |
| Init | `terraform init` | Provider 다운로드, Backend 초기화 |
| Validate | `terraform validate` | 구문 검증 (로컬만) |
| Plan | `terraform plan` | 실행 계획 생성 (API 호출) |
| Apply | `terraform apply` | 인프라 변경 적용 |
| Destroy | `terraform destroy` | 모든 리소스 삭제 |

### 2. State 파일의 역할

- **매핑**: Configuration ↔ Real Infrastructure
- **메타데이터**: 리소스 종속성, 속성 값
- **성능**: API 호출 최소화 (대규모 인프라)
- **협업**: Remote State로 팀 작업

### 3. Plan vs Apply

| terraform plan | terraform apply |
|----------------|-----------------|
| **읽기 전용** | **쓰기 작업** |
| 변경 계획만 생성 | 실제 인프라 변경 |
| State Refresh | State 업데이트 |
| API 조회만 | API 생성/수정/삭제 |

---

## 🐛 문제 해결

### 문제 1: Bucket 이름 충돌

**오류:**
```
Error: creating S3 Bucket: BucketAlreadyExists
```

**해결:**
```bash
# main.tf의 bucket 이름을 고유하게 변경
bucket = "terraform-lab-01-bucket-DIFFERENT-NAME-20260720"
```

### 문제 2: AWS Credentials 오류

**오류:**
```
Error: No valid credential sources found
```

**해결:**
```bash
# AWS CLI 재설정
aws configure

# Credentials 확인
aws sts get-caller-identity
```

### 문제 3: Provider 다운로드 실패

**오류:**
```
Error: Failed to query available provider packages
```

**해결:**
```bash
# 캐시 삭제
rm -rf .terraform .terraform.lock.hcl

# 재초기화
terraform init -upgrade
```

### 문제 4: State Lock 오류

**오류:**
```
Error: Error locking state
```

**해결:**
```bash
# Local backend는 lock이 없으므로 발생 안 함
# Remote backend 사용 시: force unlock
terraform force-unlock <LOCK_ID>
```

---

## 📚 추가 학습

### 다음 실습
- [Lab 02: Variables와 Outputs](/archive/labs/lab-02-variables-outputs/readme/)

### 관련 문서
- [Terraform CLI Commands](https://developer.hashicorp.com/terraform/cli/commands)
- [AWS Provider - S3 Bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)
- [Terraform State](https://developer.hashicorp.com/terraform/language/state)

### 시험 관련 문제
- [Core Workflow 예상문제](/archive/practice-exams/mock-exam-set-1/#domain-3-core-terraform-workflow-16--9-questions)

---

## 📝 실습 노트

### 배운 개념
- [ ] `terraform init`의 역할
- [ ] Provider와 Plugin의 관계
- [ ] `.terraform.lock.hcl`의 목적
- [ ] `terraform plan`과 `terraform apply`의 차이
- [ ] State 파일이 저장하는 정보
- [ ] Outputs의 활용

### 실무 적용
- 모든 인프라 변경 전 `terraform plan` 필수
- State 파일은 버전 관리에서 제외 (.gitignore)
- 프로덕션에서는 Remote State 사용
- `terraform destroy` 신중하게 사용

---

**축하합니다! 첫 번째 Terraform 실습을 완료했습니다! 🎉**

다음 실습에서는 Variables와 Outputs를 활용한 재사용 가능한 구성을 만들어봅니다.
