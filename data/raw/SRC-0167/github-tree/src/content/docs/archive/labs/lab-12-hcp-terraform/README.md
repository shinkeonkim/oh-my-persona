---
title: "Lab 12: HCP Terraform 워크플로우"
description: "Legacy study material imported from labs/lab-12-hcp-terraform/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

:::danger[Do not copy static credentials]
이 historical guide의 static AWS access key 절차를 사용하지 마세요. 비용 없는 remote-run 실습과 dynamic credential guidance는 [canonical Lab 12](/labs/12-hcp-terraform/)를 사용합니다.
:::

## 📋 개요

**난이도:** 🔴 Advanced
**소요 시간:** 120분
**시험 도메인:** HCP Terraform (6%)

### 학습 목표

- ✅ HCP Terraform 계정 생성
- ✅ CLI-driven Workspace
- ✅ VCS-driven Workspace
- ✅ Variable Sets
- ✅ Run Triggers
- ✅ Manual Approval + Cost Estimation

---

## 📖 Setup: HCP Terraform 무료 계정

1. **가입:** https://app.terraform.io/signup
2. **Organization 생성**
3. **Email 인증**

---

## 📖 Part 1: CLI-driven Workspace

### Step 1: Terraform 인증

```bash
terraform login
# Token 발급 → 붙여넣기
```

### Step 2: cloud block 설정

**main.tf:**
```hcl
terraform {
  required_version = ">= 1.12.0"

  cloud {
    organization = "your-org-name"

    workspaces {
      name = "lab-12-cli"
    }
  }

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

resource "aws_s3_bucket" "lab" {
  bucket = "hcp-tf-lab-${random_id.suffix.hex}"
}

resource "random_id" "suffix" {
  byte_length = 4
}

output "bucket_name" {
  value = aws_s3_bucket.lab.id
}
```

### Step 3: 초기화

```bash
terraform init
# HCP Terraform 자동 감지, Workspace 생성
```

### Step 4: AWS Credentials 설정 (HCP UI)

**Workspace → Variables → Add variable**

```
Category: Environment
Key: AWS_ACCESS_KEY_ID
Value: AKIAxxxxxxxxxxxx
Sensitive: [✓]

Category: Environment
Key: AWS_SECRET_ACCESS_KEY
Value: xxxxxxxxxxxxxxxx
Sensitive: [✓]
```

### Step 5: Remote Execution

```bash
terraform plan
# Running plan in Terraform Cloud
# Output will stream here...

terraform apply
# UI 에서 Confirm & Apply 클릭
```

---

## 📖 Part 2: VCS-driven Workspace

### Step 1: GitHub Repo 준비

```bash
# GitHub 에 my-terraform-lab repo 생성
git init
git remote add origin https://github.com/YOUR_USER/my-terraform-lab.git
```

**main.tf (별도 브랜치):**
```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "vcs_lab" {
  bucket = "vcs-lab-${random_id.suffix.hex}"
}

resource "random_id" "suffix" { byte_length = 4 }
```

```bash
git add .
git commit -m "Initial infra"
git push origin main
```

### Step 2: VCS Provider 연결

**HCP: Settings → VCS Providers → Add**
- GitHub OAuth 인증

### Step 3: Workspace 생성 (VCS-driven)

**Workspaces → New workspace**
```
Workflow: Version control workflow
VCS Provider: GitHub
Repository: YOUR_USER/my-terraform-lab
Workspace Name: lab-12-vcs
```

### Step 4: 자동 Plan on Push

```bash
# main branch 에 변경 후 push
git push origin main

# HCP UI 에서 자동 Plan 확인
```

---

## 📖 Part 3: Variable Sets

### 목적: 여러 Workspace 에 공유

### Step 1: Variable Set 생성

**Settings → Variable Sets → Create**

```
Name: AWS Credentials
Scope: Apply to specific workspaces
  ├── lab-12-cli
  └── lab-12-vcs

Variables:
  Category: Environment
  ├── AWS_ACCESS_KEY_ID (sensitive)
  └── AWS_SECRET_ACCESS_KEY (sensitive)
```

### Step 2: 이제 두 Workspace 모두 credentials 공유

---

## 📖 Part 4: Run Triggers

### 시나리오: Network → App

### Step 1: 두 Workspace 준비

- `network-workspace`
- `app-workspace`

### Step 2: Run Trigger 설정

**app-workspace → Settings → Run Triggers**
```
Add Source Workspace:
└── network-workspace
```

### Step 3: 테스트

```bash
# network-workspace 에서 apply
terraform apply

# app-workspace 에서 자동 plan 트리거됨
```

---

## 📖 Part 5: Manual Approval + Cost Estimation

### Step 1: Auto Apply 비활성화

**Workspace → Settings → Auto Apply: [ ] Disabled**

### Step 2: Apply 요청

```bash
terraform apply
# Plan 완료 → UI 대기
```

### Step 3: UI 에서 Cost Estimation 확인

```
Cost Estimation:
  + aws_s3_bucket.lab
      $0.023/mo (S3 Standard)

  Total delta: +$0.023/mo
```

### Step 4: Confirm & Apply

- 팀원 리뷰
- Add comment
- Confirm & Apply 클릭

---

## 📖 Part 6: (선택) Sentinel Policy

### Step 1: Policy 작성

**require-tags.sentinel:**
```python
import "tfplan/v2" as tfplan

required_tags = ["Environment", "Owner"]

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket" implies
      all required_tags as tag {
        tag in keys(rc.change.after.tags)
      }
  }
}
```

### Step 2: Policy Set 생성

**Settings → Policy Sets → Create**
- Policies 첨부
- Enforcement: Soft Mandatory
- Workspaces 적용

---

## ✅ 검증

- ✅ Remote execution 동작
- ✅ VCS 연동
- ✅ Variable Sets 공유
- ✅ Run Trigger 자동화
- ✅ Manual Approval 확인
- ✅ Cost Estimation 표시

---

## 🎯 핵심 개념

### Run Workflow (시험 중요!)

```
Plan → Cost Estimation → Policy Check → Apply
```

### Workspace Types

- CLI-driven: 로컬 CLI + Remote state
- VCS-driven: Git 자동화
- API-driven: 완전 자동화

---

## 📚 시험 관련

- cloud block (backend "remote" 대신)
- Variable Sets (Global/Project/Workspace)
- Run Triggers 방향 (Destination 에서 Source 지정)
- Cost Estimation (AWS, Azure, GCP)
- Sentinel Enforcement (Advisory, Soft, Hard Mandatory)

---

## Cleanup

```bash
terraform destroy
# 각 workspace 마다
```

---

## 참고

- [Workspaces & Projects](/archive/08-hcp-terraform/workspaces-projects/)
- [Variable Sets](/archive/08-hcp-terraform/variables-triggers/)
- [Policy](/archive/08-hcp-terraform/policy/)
- [Collaboration](/archive/08-hcp-terraform/collaboration/)
