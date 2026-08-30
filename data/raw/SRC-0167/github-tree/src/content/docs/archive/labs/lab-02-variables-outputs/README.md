---
title: "Lab 02: Variables와 Outputs"
description: "Legacy study material imported from labs/lab-02-variables-outputs/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟢 Beginner  
**소요 시간:** 45-60분  
**시험 도메인:** Terraform Configuration (26%)

### 학습 목표

- ✅ Input Variables 정의 및 사용
- ✅ Variable 타입 이해 (string, number, list, map, object)
- ✅ Variable 기본값 및 검증
- ✅ Outputs를 통한 정보 노출
- ✅ 환경별 구성 관리

### 실습 시나리오

Variables를 활용하여 재사용 가능한 S3 Bucket 구성을 만들고, 여러 환경(dev/staging/prod)에서 동일한 코드를 사용합니다.

---

## 📖 단계별 실습

### Step 1: 작업 디렉토리 생성

```bash
mkdir -p ~/terraform-labs/lab-02
cd ~/terraform-labs/lab-02
```

### Step 2: Variables 정의

**파일: `variables.tf`**

```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

variable "bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
  default     = "myapp"
}

variable "enable_versioning" {
  description = "Enable bucket versioning"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

### Step 3: Main 구성

**파일: `main.tf`**

```hcl
resource "aws_s3_bucket" "app_bucket" {
  bucket = "${var.bucket_prefix}-${var.environment}-${random_id.bucket_suffix.hex}"

  tags = merge(
    {
      Name        = "${var.bucket_prefix}-${var.environment}"
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "versioning" {
  count  = var.enable_versioning ? 1 : 0
  bucket = aws_s3_bucket.app_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
```

### Step 4: Outputs 정의

**파일: `outputs.tf`**

```hcl
output "bucket_name" {
  description = "Full bucket name"
  value       = aws_s3_bucket.app_bucket.id
}

output "bucket_arn" {
  description = "Bucket ARN"
  value       = aws_s3_bucket.app_bucket.arn
}

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

output "versioning_enabled" {
  description = "Is versioning enabled"
  value       = var.enable_versioning
}
```

### Step 5: Variable 값 제공 방법

**방법 1: terraform.tfvars**

```hcl
environment        = "dev"
bucket_prefix      = "mycompany"
enable_versioning  = true
tags = {
  Team    = "DevOps"
  Project = "WebApp"
}
```

**방법 2: 명령줄**

```bash
terraform apply \
  -var="environment=staging" \
  -var="bucket_prefix=myapp"
```

**방법 3: 환경 변수**

```bash
export TF_VAR_environment="prod"
export TF_VAR_bucket_prefix="production-app"
terraform apply
```

### Step 6: 실습 시나리오

**Dev 환경 배포:**

```bash
cat > dev.tfvars << 'EOF'
environment       = "dev"
bucket_prefix     = "myapp"
enable_versioning = false
tags = {
  CostCenter = "Engineering"
  Owner      = "DevTeam"
}
EOF

terraform apply -var-file="dev.tfvars"
```

**Prod 환경 배포:**

```bash
cat > prod.tfvars << 'EOF'
environment       = "prod"
bucket_prefix     = "myapp"
enable_versioning = true
tags = {
  CostCenter = "Production"
  Owner      = "OpsTeam"
  Backup     = "Required"
}
EOF

terraform apply -var-file="prod.tfvars"
```

---

## ✅ 검증

```bash
terraform output
terraform output -json
terraform output bucket_name
```

---

## 🎯 학습 포인트

### Variable Types

| Type | Example | Use Case |
|------|---------|----------|
| `string` | `"us-east-1"` | 단일 문자열 값 |
| `number` | `10` | 숫자 값 |
| `bool` | `true` | 참/거짓 |
| `list(string)` | `["a", "b"]` | 순서있는 컬렉션 |
| `map(string)` | `{key = "val"}` | 키-값 쌍 |
| `object({...})` | 복잡한 구조 | 중첩 속성 |

### Variable Precedence

우선순위 (높음 → 낮음):
1. 명령줄 `-var`
2. `-var-file`
3. `terraform.tfvars`
4. 환경 변수 `TF_VAR_*`
5. `default` 값

---

**완성된 Lab 02 솔루션은 `solution/` 폴더를 참고하세요.**
