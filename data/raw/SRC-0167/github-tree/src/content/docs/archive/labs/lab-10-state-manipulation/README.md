---
title: "Lab 10: State 조작 마스터"
description: "Legacy study material imported from labs/lab-10-state-manipulation/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🔴 Advanced
**소요 시간:** 90분
**시험 도메인:** State Management (16%) + Maintain Infrastructure (10%)

### 학습 목표

- ✅ terraform import (신구 방식)
- ✅ terraform state mv (리소스 이름 변경)
- ✅ terraform state rm
- ✅ moved block (1.1+)
- ✅ removed block (1.7+)
- ✅ Drift 감지 및 해결

---

## 📖 시나리오 1: terraform import (CLI 방식)

### 사전: 기존 리소스 준비

```bash
aws s3 mb s3://my-import-test-bucket-$(date +%s)
BUCKET_NAME=$(aws s3 ls | grep my-import-test | awk '{print $3}')
```

### Import

**main.tf:**
```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "imported" {
  bucket = "PLACEHOLDER"  # import 후 수정
}
```

```bash
terraform init
terraform import aws_s3_bucket.imported $BUCKET_NAME

# State 확인
terraform state show aws_s3_bucket.imported
```

**Config 수정:**
```hcl
resource "aws_s3_bucket" "imported" {
  bucket = "실제-bucket-이름"
}
```

```bash
terraform plan  # No changes
```

---

## 📖 시나리오 2: import block (신방식, 1.5+)

**main.tf:**
```hcl
import {
  to = aws_s3_bucket.imported_v2
  id = "existing-bucket-name"
}

resource "aws_s3_bucket" "imported_v2" {
  bucket = "existing-bucket-name"
}
```

```bash
terraform plan
# aws_s3_bucket.imported_v2 will be imported

terraform apply
```

### Config 자동 생성

```hcl
import {
  to = aws_s3_bucket.imported_v3
  id = "another-bucket"
}
# resource 블록 없음
```

```bash
terraform plan -generate-config-out=generated.tf
# generated.tf 에 resource 블록 자동 생성
```

---

## 📖 시나리오 3: terraform state mv (이름 변경)

**Before:**
```hcl
resource "aws_s3_bucket" "web" {
  bucket = "my-web-bucket"
}
```

**Rename to:**
```hcl
resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-bucket"
}
```

**Manual approach:**
```bash
terraform state mv aws_s3_bucket.web aws_s3_bucket.web_assets
terraform plan  # No changes (rename 만)
```

---

## 📖 시나리오 4: moved block (선호 방식, 1.1+)

**main.tf:**
```hcl
moved {
  from = aws_s3_bucket.web
  to   = aws_s3_bucket.web_assets
}

resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-bucket"
}
```

```bash
terraform plan
# # aws_s3_bucket.web has moved to aws_s3_bucket.web_assets

terraform apply
```

---

## 📖 시나리오 5: Module 로 이동

**Before (root):**
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
```

**After (module):**
```hcl
module "network" {
  source = "./modules/network"
}

moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
```

**modules/network/main.tf:**
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
```

```bash
terraform plan
terraform apply
```

---

## 📖 시나리오 6: terraform state rm

### 목적: Terraform 관리 해제 (실제 인프라 유지)

```bash
terraform state rm aws_s3_bucket.legacy

# State 에서만 제거
# 실제 S3 bucket 은 그대로 유지
```

**검증:**
```bash
terraform state list | grep legacy
# (empty)

aws s3 ls
# my-legacy-bucket  ← 실제로는 존재
```

---

## 📖 시나리오 7: removed block (1.7+)

**main.tf:**
```hcl
removed {
  from = aws_s3_bucket.legacy

  lifecycle {
    destroy = false  # 실제 인프라 유지
  }
}
```

```bash
terraform plan
# aws_s3_bucket.legacy will be removed from state

terraform apply
```

---

## 📖 시나리오 8: Drift 감지 및 해결

### Drift 유발

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}
```

```bash
terraform apply

# AWS Console 에서 instance_type 을 t3.small 로 변경
aws ec2 modify-instance-attribute \
  --instance-id $(terraform output -raw instance_id) \
  --instance-type '{"Value": "t3.small"}'
```

### Drift 감지

```bash
terraform plan
# ~ instance_type = "t3.small" -> "t3.micro"
# Drift detected
```

### 해결 옵션

**Option 1: Terraform 우선 (config 로 복원)**
```bash
terraform apply
# t3.small → t3.micro 로 복원
```

**Option 2: 실제 상태 수용**
```hcl
resource "aws_instance" "web" {
  instance_type = "t3.small"  # config 업데이트
}
```

**Option 3: Refresh only (state 만 동기화)**
```bash
terraform apply -refresh-only
# State ← 실제 상태
```

---

## ✅ 검증

각 시나리오마다:
```bash
terraform state list
terraform state show <resource>
terraform plan  # No changes 확인
```

---

## 🎯 핵심 명령어

| 목적 | CLI 방식 | Block 방식 (신) |
|------|----------|----------------|
| Import | `terraform import` | `import` block (1.5+) |
| Rename | `terraform state mv` | `moved` block (1.1+) |
| Remove | `terraform state rm` | `removed` block (1.7+) |
| Recreate | `-` | `apply -replace=` |
| Refresh | `-` | `apply -refresh-only` |

---

## 📚 시험 관련

- `taint` deprecated → `apply -replace`
- `refresh` deprecated → `apply -refresh-only`
- `state rm` 은 인프라 유지, state 만 제거
- Import 후 config 는 수동 작성 (또는 -generate-config-out)
- moved/removed/import block 은 선언적 (권장)

---

## Cleanup

```bash
terraform destroy
```

---

## 참고

- [State 명령어](/archive/06-state/state-commands/)
- [Drift Detection](/archive/06-state/drift-detection/)
