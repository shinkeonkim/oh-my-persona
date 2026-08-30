---
title: "Remote Backend 설정 완전 정복"
description: "Legacy study material imported from 06-state/remote-backend.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Backend 종류 및 특징
- S3, Azure, GCS Backend 설정
- HCP Terraform (cloud block) 설정
- Backend Migration 전략
- Backend 보안 Best Practices

---

## 1. Backend 개요

### Backend 란?

**Backend** 는 Terraform state 를 **어떻게 저장하고 접근할지** 결정합니다.

### Backend 종류

**Standard Backends:**
- `local` (기본)
- `s3` (AWS)
- `azurerm` (Azure)
- `gcs` (Google Cloud)
- `consul`
- `etcdv3`
- `http`
- `kubernetes`
- `oss` (Alibaba)
- `pg` (PostgreSQL)

**Enhanced Backend:**
- `cloud` (HCP Terraform) - 새 방식
- `remote` (Deprecated, cloud block 사용 권장)

### 특징 비교

| Backend | Locking | 암호화 | 팀 협업 | 비용 |
|---------|---------|--------|---------|------|
| local | ❌ | ❌ | ❌ | 무료 |
| s3 (+ DynamoDB) | ✅ | ✅ | ✅ | 저렴 |
| azurerm | ✅ | ✅ | ✅ | 저렴 |
| gcs | ✅ | ✅ | ✅ | 저렴 |
| HCP Terraform | ✅ | ✅ | ✅ | Free/Paid |
| consul | ✅ | 옵션 | ✅ | 자체 호스팅 |

---

## 2. Local Backend

### 기본값

```hcl
# backend 블록 없음 = local backend
terraform {
  required_providers {
    aws = { ... }
  }
}
```

**State 위치:** `terraform.tfstate`

### 명시적 정의

```hcl
terraform {
  backend "local" {
    path = "path/to/terraform.tfstate"
  }
}
```

### 사용 시나리오

- ✅ 개인 학습
- ✅ 프로토타입
- ❌ 팀 협업 (금지)
- ❌ 프로덕션

---

## 3. S3 Backend (AWS)

### 3.1 기본 설정

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### 3.2 주요 Arguments

| Argument | 필수 | 설명 |
|----------|------|------|
| `bucket` | ✅ | S3 bucket 이름 |
| `key` | ✅ | State 파일 경로 |
| `region` | ✅ | Bucket 리전 |
| `encrypt` | 권장 | SSE 활성화 |
| `dynamodb_table` | 권장 | State locking |
| `kms_key_id` | 선택 | KMS 키 (SSE-KMS) |
| `profile` | 선택 | AWS Profile |
| `role_arn` | 선택 | Assume Role |
| `workspace_key_prefix` | 선택 | Workspace prefix |
| `endpoint` | 선택 | Custom endpoint |
| `sse_algorithm` | 선택 | AES256 또는 aws:kms |

### 3.3 Backend 인프라 부트스트랩

Chicken-and-egg 문제: State bucket 을 Terraform 으로 만들 때, State 는 어디에?

**해결 방법:**

```hcl
# bootstrap.tf (로컬 state 사용)
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  # backend 없음 → local
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state-bucket-unique"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

**실행:**
```bash
terraform init
terraform apply

# 이제 bootstrap.tf 를 s3 backend 로 마이그레이션
```

### 3.4 IAM 권한

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::my-terraform-state"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::my-terraform-state/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/terraform-state-lock"
    }
  ]
}
```

### 3.5 KMS 암호화

```hcl
terraform {
  backend "s3" {
    bucket     = "my-terraform-state"
    key        = "prod/terraform.tfstate"
    region     = "us-east-1"
    encrypt    = true
    kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/abc-123"
    dynamodb_table = "terraform-state-lock"
  }
}
```

---

## 4. Azure Backend (azurerm)

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-rg"
    storage_account_name = "terraformstate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

**특징:**
- ✅ 기본 Locking (Storage Blob lease)
- ✅ 암호화 (기본)
- ✅ Versioning

---

## 5. GCS Backend (Google Cloud)

```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "prod"
  }
}
```

**특징:**
- ✅ 기본 Locking
- ✅ 암호화 (기본)
- ✅ Versioning

---

## 6. HCP Terraform (cloud block)

### 6.1 새 방식 (권장)

```hcl
terraform {
  cloud {
    organization = "my-org"

    workspaces {
      name = "prod-app"
    }
  }
}
```

### 6.2 Tags 기반

```hcl
terraform {
  cloud {
    organization = "my-org"

    workspaces {
      tags = ["app", "production"]
    }
  }
}
```

### 6.3 옛 방식 (remote backend, deprecated)

```hcl
terraform {
  backend "remote" {
    organization = "my-org"

    workspaces {
      name = "prod-app"
    }
  }
}
```

→ 새 프로젝트는 `cloud` block 사용.

### 6.4 인증

```bash
terraform login
```

---

## 7. Partial Backend Configuration

### 목적

Backend 설정을 외부화 (다른 환경에서 재사용).

### 방법 1: -backend-config 옵션

**main.tf:**
```hcl
terraform {
  backend "s3" {
    # 값 없음 (partial)
  }
}
```

```bash
terraform init \
  -backend-config="bucket=my-tfstate" \
  -backend-config="key=prod/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=terraform-lock" \
  -backend-config="encrypt=true"
```

### 방법 2: Backend Config 파일

**prod.backend.hcl:**
```hcl
bucket         = "my-tfstate"
key            = "prod/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "terraform-lock"
encrypt        = true
```

```bash
terraform init -backend-config="prod.backend.hcl"
```

### 방법 3: 여러 환경별 파일

```
project/
├── main.tf                     # backend "s3" {}
├── dev.backend.hcl
├── staging.backend.hcl
└── prod.backend.hcl
```

```bash
# Dev 환경
terraform init -backend-config="dev.backend.hcl"
terraform apply

# Prod 환경 (다른 디렉토리 또는 -reconfigure)
terraform init -reconfigure -backend-config="prod.backend.hcl"
```

---

## 8. Backend Migration

### 8.1 Local → S3

**Before:**
```hcl
terraform {
  # backend 없음 → local
}
```

**After:**
```hcl
terraform {
  backend "s3" {
    bucket = "my-tfstate"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
```

**실행:**
```bash
terraform init -migrate-state

# 프롬프트:
# Do you want to copy existing state to the new backend?
#   Enter a value: yes
```

### 8.2 S3 → S3 (다른 bucket)

```hcl
terraform {
  backend "s3" {
    bucket = "new-tfstate"  # 변경
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
```

```bash
terraform init -migrate-state
```

### 8.3 S3 → HCP Terraform

**Before:**
```hcl
terraform {
  backend "s3" { ... }
}
```

**After:**
```hcl
terraform {
  cloud {
    organization = "my-org"
    workspaces { name = "prod" }
  }
}
```

```bash
terraform login
terraform init -migrate-state
```

### 8.4 Backend 재구성 (마이그레이션 없이)

```bash
terraform init -reconfigure
```

⚠️ **위험:** 기존 state 는 잊혀짐. 데이터 손실 가능.

### 8.5 Migration vs Reconfigure

| | -migrate-state | -reconfigure |
|-|----------------|--------------|
| State 이동 | ✅ | ❌ |
| Backend 변경 | ✅ | ✅ |
| 데이터 손실 위험 | 낮음 | 높음 |
| 사용 시점 | Backend 변경 | Config 만 변경 |

---

## 9. Backend 보안

### 9.1 암호화

**At Rest:**
```hcl
terraform {
  backend "s3" {
    bucket  = "my-tfstate"
    encrypt = true
    kms_key_id = "arn:aws:kms:..."  # 선택 (KMS)
  }
}
```

**In Transit:** 자동 (HTTPS/TLS)

### 9.2 접근 제어

**S3 Bucket Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::my-tfstate/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

### 9.3 Versioning

```hcl
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}
```

**이점:**
- 실수로 삭제 시 복구
- 이전 버전 참조

### 9.4 MFA Delete

```hcl
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Enabled"
  }
}
```

---

## 10. 실전 시나리오

### 시나리오 1: Multi-Environment (dev/staging/prod)

**옵션 1: Workspace 사용**
```hcl
terraform {
  backend "s3" {
    bucket = "my-tfstate"
    key    = "app/terraform.tfstate"  # 단일 key
    region = "us-east-1"
  }
}
```

```bash
terraform workspace new prod
terraform workspace select prod
# State 위치: app/env:/prod/terraform.tfstate
```

**옵션 2: Key Prefix**
```
key = "dev/terraform.tfstate"
key = "staging/terraform.tfstate"
key = "prod/terraform.tfstate"
```

### 시나리오 2: Multi-Region

```hcl
terraform {
  backend "s3" {
    bucket = "my-tfstate-us-east-1"
    key    = "us-east-1/prod/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "terraform-lock-us-east-1"
  }
}
```

**각 리전마다 별도 bucket + DynamoDB.**

### 시나리오 3: Cross-Account

```hcl
terraform {
  backend "s3" {
    bucket   = "shared-tfstate"
    key      = "app/terraform.tfstate"
    region   = "us-east-1"
    role_arn = "arn:aws:iam::999999999999:role/TerraformStateAccess"
  }
}
```

---

## 11. Troubleshooting

### 오류 1: Access Denied

```
Error: error using credentials to get account ID
```

**해결:**
```bash
aws sts get-caller-identity
# IAM 권한 확인
```

### 오류 2: State Lock

```
Error: Error locking state
```

**해결:**
```bash
terraform force-unlock <LOCK_ID>
```

### 오류 3: Backend 변경 후 오류

```
Error: Backend configuration changed
```

**해결:**
```bash
terraform init -reconfigure
# 또는
terraform init -migrate-state
```

---

## 12. Best Practices

### ✅ DO

- **Remote Backend 사용** (프로덕션)
- **State Locking 활성화** (DynamoDB, Blob Lease)
- **암호화 적용** (SSE, KMS)
- **Versioning 활성화**
- **Backend infrastructure 는 별도 관리**
- **IAM 권한 최소화**
- **Partial config 로 환경별 재사용**

### ❌ DON'T

- 프로덕션에서 local backend
- State bucket 을 public 하게 노출
- 하드코딩된 credentials
- 무단으로 backend 변경 (팀 공유 필수)

---

## 13. 시험 자주 나오는 함정

### 함정 1: S3 Backend 만으로 Locking?

```
Q: S3 backend 는 자체 locking 을 지원하나요?
A: ❌ NO. DynamoDB 필요.
```

### 함정 2: -migrate-state vs -reconfigure

```
Q: Backend 변경 시 어떤 옵션?
A: State 를 옮기려면 -migrate-state.
   기존 state 잊고 새로 시작하려면 -reconfigure (위험!).
```

### 함정 3: cloud block vs backend "remote"

```
Q: HCP Terraform 용 최신 방식은?
A: cloud block. backend "remote" 는 deprecated.
```

### 함정 4: Partial Config

```
Q: Backend 블록에 값이 없어도 되나요?
A: ✅ YES. Partial config → init 시 -backend-config 로 제공.
```

---

## 참고 자료

- [Backend Configuration](https://developer.hashicorp.com/terraform/language/settings/backends/configuration)
- [S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3)
- [HCP Terraform cloud block](https://developer.hashicorp.com/terraform/language/settings/terraform-cloud)
- 관련 문서: [State Locking](/archive/06-state/state-locking/), [State 명령어](/archive/06-state/state-commands/), [Drift Detection](/archive/06-state/drift-detection/)
- 실습: [Lab 06: Remote State](/archive/labs/lab-06-remote-state/readme/)
