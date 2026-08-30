---
title: "Lab 06: Remote State 설정"
description: "Legacy study material imported from labs/lab-06-remote-state/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

:::caution[Current Terraform 1.12 path]
이 historical guide의 DynamoDB locking 절차 대신 [canonical Lab 06](/labs/06-remote-state/)의 S3 `use_lockfile` 절차를 사용하세요. DynamoDB-based locking은 deprecated입니다.
:::

## 📋 개요

**난이도:** 🟡 Intermediate  
**소요 시간:** 60분  
**시험 도메인:** State Management (16%)

### 학습 목표
- ✅ Local State → Remote State 마이그레이션
- ✅ S3 Backend 설정
- ✅ DynamoDB State Locking
- ✅ State 암호화 및 보안

### 실습 시나리오
기존 로컬 State를 S3 + DynamoDB를 사용하는 Remote Backend로 마이그레이션하고, State Locking을 테스트합니다.

---

## 📖 Part 1: S3 Backend 인프라 준비

### Step 1: Backend 인프라 생성

**디렉토리: `backend-infrastructure/`**

**파일: `backend-setup.tf`**
```hcl
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

resource "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state-YOUR_INITIALS-20260720"

  tags = {
    Name        = "Terraform State Bucket"
    Environment = "Lab"
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
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Lock Table"
    Environment = "Lab"
  }
}

output "state_bucket_name" {
  value = aws_s3_bucket.terraform_state.id
}

output "lock_table_name" {
  value = aws_dynamodb_table.terraform_lock.name
}
```

### Step 2: Backend 인프라 배포

```bash
cd backend-infrastructure
terraform init
terraform apply -auto-approve

export STATE_BUCKET=$(terraform output -raw state_bucket_name)
export LOCK_TABLE=$(terraform output -raw lock_table_name)

echo "State Bucket: $STATE_BUCKET"
echo "Lock Table: $LOCK_TABLE"
```

---

## 📖 Part 2: Remote Backend로 마이그레이션

### Step 3: 로컬 State로 시작

**디렉토리: `../main-project/`**

**파일: `main.tf`**
```hcl
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

resource "aws_s3_bucket" "example" {
  bucket = "example-app-YOUR_INITIALS-20260720"

  tags = {
    Name = "Example Application Bucket"
  }
}

output "bucket_name" {
  value = aws_s3_bucket.example.id
}
```

### Step 4: 로컬 State로 배포

```bash
cd ../main-project
terraform init
terraform apply -auto-approve

ls -la terraform.tfstate
cat terraform.tfstate | jq '.resources'
```

**확인:**
- `terraform.tfstate` 파일 존재
- 로컬 파일 시스템에 State 저장됨

---

### Step 5: Remote Backend 구성 추가

**main.tf에 backend 블록 추가:**
```hcl
terraform {
  required_version = ">= 1.12.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "terraform-state-YOUR_INITIALS-20260720"
    key            = "main-project/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### Step 6: State 마이그레이션

```bash
terraform init -migrate-state
```

**대화형 프롬프트:**
```
Do you want to copy existing state to the new backend?
  Enter a value: yes
```

**예상 출력:**
```
Initializing the backend...
Do you want to copy existing state to the new backend?
  Pre-existing state was found while migrating the previous "local" backend to the
  newly configured "s3" backend. No existing state was found in the newly
  configured "s3" backend. Do you want to copy this state to the new "s3"
  backend? Enter "yes" to copy and "no" to start with an empty state.

  Enter a value: yes

Successfully configured the backend "s3"! Terraform will automatically
use this backend unless the backend configuration changes.
```

### Step 7: Remote State 확인

```bash
ls -la terraform.tfstate*

aws s3 ls s3://terraform-state-YOUR_INITIALS-20260720/main-project/

aws s3 cp s3://terraform-state-YOUR_INITIALS-20260720/main-project/terraform.tfstate - | jq .
```

**확인 사항:**
- ✅ 로컬 State 파일 삭제됨
- ✅ S3에 State 업로드됨
- ✅ Versioning 활성화
- ✅ 암호화 적용

---

## 📖 Part 3: State Locking 테스트

### Step 8: State Locking 동작 확인

**터미널 1:**
```bash
terraform apply
```

**터미널 2 (동시 실행):**
```bash
terraform apply
```

**예상 결과:**
```
Error: Error locking state: Error acquiring the state lock:
ConditionalCheckFailedException: The conditional request failed
Lock Info:
  ID:        abc123-def456-ghi789
  Path:      terraform-state-YOUR_INITIALS-20260720/main-project/terraform.tfstate
  Operation: OperationTypeApply
  Who:       user@hostname
  Version:   1.12.0
  Created:   2026-07-20 10:00:00.123456789 +0000 UTC
  Info:      
```

→ **State Locking이 정상 작동!**

### Step 9: DynamoDB Lock Table 확인

```bash
aws dynamodb scan \
  --table-name terraform-state-lock \
  --output json | jq .
```

**Apply 중일 때 출력:**
```json
{
  "Items": [
    {
      "LockID": {
        "S": "terraform-state-YOUR_INITIALS-20260720/main-project/terraform.tfstate-md5"
      },
      "Info": {
        "S": "{\"ID\":\"abc123...\",\"Operation\":\"OperationTypeApply\"}"
      }
    }
  ]
}
```

---

## 📖 Part 4: State 버전 관리

### Step 10: State Versioning 테스트

**리소스 수정:**
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "example-app-YOUR_INITIALS-20260720"

  tags = {
    Name        = "Example Application Bucket"
    Environment = "Production"
  }
}
```

```bash
terraform apply -auto-approve
```

### Step 11: S3 Versioning 확인

```bash
aws s3api list-object-versions \
  --bucket terraform-state-YOUR_INITIALS-20260720 \
  --prefix main-project/ \
  --output json | jq '.Versions'
```

**예상 출력:**
```json
[
  {
    "Key": "main-project/terraform.tfstate",
    "VersionId": "abc123...",
    "IsLatest": true,
    "LastModified": "2026-07-20T10:05:00.000Z"
  },
  {
    "Key": "main-project/terraform.tfstate",
    "VersionId": "def456...",
    "IsLatest": false,
    "LastModified": "2026-07-20T10:00:00.000Z"
  }
]
```

### Step 12: 이전 버전 복구 (선택)

```bash
OLD_VERSION_ID="def456..."

aws s3api get-object \
  --bucket terraform-state-YOUR_INITIALS-20260720 \
  --key main-project/terraform.tfstate \
  --version-id $OLD_VERSION_ID \
  old-state.tfstate

cat old-state.tfstate | jq .
```

---

## 📖 Part 5: 팀 협업 시나리오

### Step 13: 다른 작업 디렉토리에서 동일 State 접근

```bash
mkdir -p ../team-member-workspace
cd ../team-member-workspace
```

**파일: `main.tf`**
```hcl
terraform {
  required_version = ">= 1.12.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "terraform-state-YOUR_INITIALS-20260720"
    key            = "main-project/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = "us-east-1"
}
```

```bash
terraform init

terraform state list

terraform show
```

**확인:**
- ✅ 동일한 State 접근
- ✅ 팀원이 같은 인프라 관리
- ✅ Locking으로 충돌 방지

---

## ✅ Cleanup

```bash
cd ../main-project
terraform destroy -auto-approve

cd ../backend-infrastructure
terraform destroy -auto-approve
```

---

## 🎯 핵심 개념

### Local vs Remote Backend

| Local Backend | Remote Backend |
|---------------|----------------|
| `terraform.tfstate` | S3, Consul, etc. |
| 로컬 파일 | 중앙 저장소 |
| 팀 협업 어려움 | 팀 협업 용이 |
| Locking 없음 | Locking 지원 |
| 보안 취약 | 암호화/접근제어 |

### S3 Backend 설정

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "path/to/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    workspace_key_prefix = "workspaces"
  }
}
```

### Backend 마이그레이션

```bash
terraform init -migrate-state

terraform init -reconfigure

terraform init -backend-config="bucket=new-bucket"
```

---

## 🐛 문제 해결

### State Lock 해제

```bash
terraform force-unlock <LOCK_ID>
```

### Backend 변경

```bash
terraform init -reconfigure
```

### State 복구

```bash
terraform state pull > backup.tfstate

terraform state push backup.tfstate
```

---

## 📚 시험 관련 포인트

**자주 나오는 질문:**
1. S3 Backend에서 Locking 제공? → ❌ (DynamoDB 필요)
2. State 파일 암호화? → `encrypt = true`
3. State 버전 관리? → S3 Versioning
4. 동시 apply 방지? → State Locking (DynamoDB)

**참고:**
- [S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3)
- [State Locking](https://developer.hashicorp.com/terraform/language/state/locking)

---

**완성된 솔루션은 `solution/` 폴더를 참고하세요.**
