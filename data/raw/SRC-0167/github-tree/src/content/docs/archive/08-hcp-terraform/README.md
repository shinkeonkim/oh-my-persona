---
title: "Week 8: HCP Terraform & 최종 복습"
description: "Legacy study material imported from 08-hcp-terraform/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- HCP Terraform (구 Terraform Cloud) 이해
- Workspaces vs Projects 구분
- VCS-driven vs CLI-driven Workflow
- Remote Execution 및 협업 기능
- Policy as Code (Sentinel/OPA)
- 최종 시험 대비 복습

---

## 1. HCP Terraform이란?

### 정의

**HCP Terraform** (HashiCorp Cloud Platform Terraform)은 Terraform을 위한 **협업 플랫폼**입니다.

**구 명칭:** Terraform Cloud, Terraform Enterprise

### 주요 기능

**1. Remote State Management**
- 자동 암호화
- 버전 관리
- State Locking 기본 제공
- 접근 제어

**2. Remote Execution**
- 중앙화된 실행 환경
- 일관된 Terraform 버전
- Private Registry 접근

**3. 협업 기능**
- Team & Organization 관리
- Role-based Access Control
- Workspace 권한

**4. 거버넌스**
- Policy as Code (Sentinel/OPA)
- Cost Estimation
- Drift Detection
- Health Assessments

**5. VCS 통합**
- GitHub, GitLab, Bitbucket 등
- 자동 Plan/Apply
- PR 통합

---

## 2. Workspaces vs Projects

### HCP Terraform Workspace

**정의:** 독립적인 Terraform 실행 환경

**특징:**
- 별도의 State
- 고유한 Variables
- 독립적인 실행

**예시:**
```
Organization: my-company
├── Workspace: prod-us-east-1
├── Workspace: prod-us-west-2
├── Workspace: staging-global
└── Workspace: dev-playground
```

### HCP Terraform Project

**정의:** 관련 Workspaces의 논리적 그룹

**특징:**
- Workspace 조직화
- 공유 설정
- Team 권한 관리

**예시:**
```
Organization: my-company
│
├── Project: Infrastructure
│   ├── Workspace: vpc-prod
│   ├── Workspace: vpc-staging
│   └── Workspace: vpc-dev
│
├── Project: Applications
│   ├── Workspace: app-frontend
│   └── Workspace: app-backend
│
└── Project: Security
    ├── Workspace: iam-policies
    └── Workspace: security-groups
```

### CLI Workspaces vs HCP Workspaces

| CLI Workspace | HCP Workspace |
|---------------|---------------|
| 동일 구성, 다른 State | 독립적인 환경 |
| `terraform.tfstate.d/` | 완전히 분리된 Workspace |
| 간단한 환경 분리 | 복잡한 인프라 관리 |
| 로컬 개념 | 원격 협업 플랫폼 |

---

## 3. HCP Terraform 설정

### 계정 생성

**1. 가입:**
- https://app.terraform.io/signup
- GitHub/GitLab/Email 인증

**2. Organization 생성:**
```
Organization Name: my-company
Email: team@example.com
```

### Terraform 구성

**terraform.tf:**
```hcl
terraform {
  cloud {
    organization = "my-company"

    workspaces {
      name = "my-app-prod"
    }
  }
}
```

**또는 tags 사용:**
```hcl
terraform {
  cloud {
    organization = "my-company"

    workspaces {
      tags = ["app", "production"]
    }
  }
}
```

### 로그인

```bash
terraform login

terraform login app.terraform.io
```

**Token 생성:**
- Settings → Tokens → Create API Token

**~/.terraform.d/credentials.tfrc.json:**
```json
{
  "credentials": {
    "app.terraform.io": {
      "token": "xxxxxxxxxxxxxx.atlasv1.yyyyyyyyyyyyyy"
    }
  }
}
```

---

## 4. Workspace 생성 및 관리

### UI에서 생성

**1. Workspaces → New Workspace**

**2. Workflow 선택:**
- **VCS-driven**: GitHub 등 연동
- **CLI-driven**: 로컬 Terraform CLI
- **API-driven**: API로 자동화

**3. 설정:**
- Workspace Name
- Project (선택)
- Description

### CLI에서 초기화

```bash
terraform init

Initializing Terraform Cloud...
Workspace "my-app-prod" already exists.
```

### Workspace 전환

```bash
terraform workspace list

terraform workspace select my-app-staging

terraform workspace new my-app-dev
```

---

## 5. Variables 관리

### Workspace Variables

**Terraform Variables:**
```hcl
variable "instance_type" {
  type = string
}
```
→ HCP Terraform UI에서 값 설정

**Environment Variables:**
```bash
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

### Variable Sets

**여러 Workspace에 공유되는 변수 집합**

**예시:**
```
Variable Set: AWS Credentials
├── AWS_ACCESS_KEY_ID (env)
├── AWS_SECRET_ACCESS_KEY (env, sensitive)
└── AWS_DEFAULT_REGION (env)

Applied to:
├── Workspace: prod-us-east-1
├── Workspace: prod-us-west-2
└── Workspace: staging
```

**생성:**
- Settings → Variable Sets → Create
- Scope: Global / Specific Projects / Specific Workspaces

---

## 6. VCS-driven Workflow

### GitHub 연동

**1. VCS Provider 추가:**
- Settings → VCS Providers → Add
- GitHub OAuth 인증

**2. Workspace 생성:**
- Workflow: VCS-driven
- Repository: `myorg/terraform-infra`
- VCS Branch: `main`

**3. 자동화:**
```
GitHub PR 생성
  ↓
HCP Terraform Plan 자동 실행
  ↓
Plan 결과 PR에 코멘트
  ↓
PR Merge
  ↓
HCP Terraform Apply 자동 실행
```

### 설정

**Workspace Settings → VCS:**
- **Automatic Plan**: PR 시 자동 Plan
- **Auto Apply**: Merge 시 자동 Apply
- **Working Directory**: Terraform 코드 경로
- **Trigger Patterns**: 특정 경로만

**예시:**
```
Working Directory: infrastructure/production
Trigger Patterns: 
  - infrastructure/production/**/*
  - modules/**/*
```

---

## 7. CLI-driven Workflow

### 로컬 실행, 원격 State

```bash
terraform init

terraform plan

terraform apply
```

**동작:**
- Local: CLI 명령 실행
- Remote: State 저장, Locking

### Remote Execution

```hcl
terraform {
  cloud {
    organization = "my-company"

    workspaces {
      name = "my-app"
    }
  }
}
```

```bash
terraform init

terraform plan
```

**동작:**
- Local: `terraform plan` 명령
- Remote: **실제 실행**은 HCP Terraform

**확인:**
```
Running plan in Terraform Cloud.

Output will stream here...

Plan: 5 to add, 0 to change, 0 to destroy.
```

---

## 8. Run Workflow

### HCP Terraform Run Lifecycle

```
1. Queue
   ↓
2. Plan
   ↓
3. Cost Estimation
   ↓
4. Policy Check (Sentinel/OPA)
   ↓
5. Apply (Manual/Auto)
   ↓
6. Complete
```

**중요:** 시험에서 순서 확인!

### Run 종류

**1. Plan-only:**
```bash
terraform plan
```

**2. Plan and Apply:**
```bash
terraform apply
```

**3. Destroy:**
```bash
terraform destroy
```

### Manual Approval

**Workspace Settings:**
- **Auto Apply**: Disabled (기본)

**실행:**
```bash
terraform apply
```
→ HCP Terraform UI에서 "Confirm & Apply" 클릭 필요

---

## 9. Run Triggers

### 목적

**Workspace 간 의존성 자동화**

**시나리오:**
```
Workspace: networking (VPC)
  ↓ (Run Trigger)
Workspace: applications (EC2, RDS)
```

### 설정

**1. Source Workspace (networking):**
- Settings → Run Triggers → Add

**2. Destination Workspace 선택:**
- `applications`

**3. 동작:**
```
networking에서 Apply 성공
  ↓
applications에서 자동 Plan 실행
```

### 예시

```
Workspace: base-network
├─ Run Trigger → web-tier
├─ Run Trigger → app-tier
└─ Run Trigger → data-tier
```

---

## 10. Policy as Code

### Sentinel (HashiCorp)

**목적:** 거버넌스 정책 강제

**예시: EC2 인스턴스 타입 제한**
```hcl
import "tfplan/v2" as tfplan

allowed_types = ["t2.micro", "t2.small", "t3.micro", "t3.small"]

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_instance" implies
      rc.change.after.instance_type in allowed_types
  }
}
```

**정책 수준:**
- **Advisory**: 경고만 (실패해도 Apply 가능)
- **Soft Mandatory**: Override 가능 (권한 필요)
- **Hard Mandatory**: 반드시 통과해야 Apply

### OPA (Open Policy Agent)

**예시: 태그 필수화**
```text
package terraform

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_instance"
  not resource.change.after.tags.Environment
  msg := sprintf("Instance %s missing Environment tag", [resource.address])
}
```

---

## 11. Cost Estimation

### 기능

**Plan 실행 시 예상 비용 표시**

```
Resources: 5 to add, 0 to change, 0 to destroy.

Cost Estimation:
  + aws_instance.web
      $8.03 /mo   (730 hours)
  
  + aws_rds_instance.db
      $72.00 /mo

  Monthly cost change: $0 → $80.03
  % change: +$80.03
```

### 지원 Provider

- AWS
- Azure
- Google Cloud

---

## 12. Drift Detection

### 자동 Drift 감지

**Workspace Settings:**
- **Health Assessments**: Enabled
- **Schedule**: Daily / Weekly

**동작:**
```
매일 자동 Plan 실행
  ↓
State vs 실제 인프라 비교
  ↓
Drift 발견 시 알림
```

**결과:**
```
Drift Detected!

~ aws_instance.web
  ~ instance_type = "t2.small" -> "t2.micro"
```

---

## 13. 팀 협업

### Organization Roles

| Role | 권한 |
|------|------|
| **Owners** | 모든 권한 |
| **Administrators** | 거의 모든 권한 (Billing 제외) |
| **Members** | Workspace 생성/관리 |

### Team Management

**Team 생성:**
```
Team: DevOps
├── Members: alice, bob, charlie
└── Workspace Access:
    ├── prod-* (Plan)
    ├── staging-* (Write)
    └── dev-* (Admin)
```

**Workspace Permissions:**
- **Read**: State, Variables 조회만
- **Plan**: Plan 실행 가능
- **Write**: Apply 가능
- **Admin**: 설정 변경 가능

---

## 14. Private Registry

### Module Registry

**Private Modules 공유:**

**1. Module 등록:**
- Registry → Modules → Publish
- VCS Repository 연결

**2. 사용:**
```hcl
module "vpc" {
  source  = "app.terraform.io/my-company/vpc/aws"
  version = "1.0.0"

  cidr_block = "10.0.0.0/16"
}
```

### Provider Registry

**Private Providers:**
```hcl
terraform {
  required_providers {
    custom = {
      source  = "app.terraform.io/my-company/custom"
      version = "~> 1.0"
    }
  }
}
```

---

## 15. 실전 시나리오

### 시나리오 1: VCS-driven Workflow

```
1. GitHub에 PR 생성
2. HCP Terraform이 자동 Plan 실행
3. Plan 결과가 PR에 코멘트로 추가
4. 팀원들이 Plan 검토
5. PR Approve 및 Merge
6. HCP Terraform이 자동 Apply
7. Slack 알림
```

### 시나리오 2: Multi-Environment

```hcl
terraform {
  cloud {
    organization = "my-company"

    workspaces {
      tags = ["app", var.environment]
    }
  }
}
```

```bash
terraform workspace select prod

terraform apply
```

### 시나리오 3: Policy 적용

```
1. Sentinel Policy 작성
2. Policy Set 생성
3. Workspace에 적용
4. terraform apply 실행
5. Policy Check 실패 시 Apply 차단
```

---

## 16. 최종 시험 복습

### 8주 핵심 요약

**Week 1-2: IaC 기초**
- ✅ Declarative vs Imperative
- ✅ Terraform Provider 아키텍처
- ✅ 기본 워크플로우

**Week 3: Core Workflow**
- ✅ init → validate → plan → apply
- ✅ State 파일 역할
- ✅ 각 명령어 차이점

**Week 4: Configuration**
- ✅ Variables, Outputs
- ✅ Data Sources
- ✅ Built-in Functions
- ✅ count vs for_each

**Week 5: Modules**
- ✅ Module 구조
- ✅ Module Sources
- ✅ Input/Output

**Week 6: State**
- ✅ Local vs Remote Backend
- ✅ State Locking (S3 + DynamoDB)
- ✅ terraform import
- ✅ Drift Detection

**Week 7: Lifecycle (004)**
- ✅ create_before_destroy
- ✅ depends_on
- ✅ Custom Conditions
- ✅ Validation

**Week 8: HCP Terraform**
- ✅ Workspaces vs Projects
- ✅ Run Workflow 순서
- ✅ VCS-driven vs CLI-driven

### 시험 당일 체크리스트

**Deprecated 명령어:**
- ❌ `terraform taint` → ✅ `terraform apply -replace=`
- ❌ `terraform refresh` → ✅ `terraform apply -refresh-only`

**핵심 암기:**
```
HCP Terraform Run Order:
Plan → Cost Estimation → Policy Check → Apply

S3 Backend Locking:
S3 alone: NO
S3 + DynamoDB: YES

sensitive = true:
CLI output: Hidden
State file: Plain text (주의!)

count vs for_each:
count: Index-based [0], [1]
for_each: Key-based ["web"], ["api"]
```

---

## 17. 핵심 요약

### HCP Terraform 주요 기능

- ✅ Remote State + Locking
- ✅ Remote Execution
- ✅ VCS 통합
- ✅ Policy as Code
- ✅ Cost Estimation
- ✅ Drift Detection
- ✅ 팀 협업

### Workspaces vs Projects

| Workspace | Project |
|-----------|---------|
| 독립 실행 환경 | Workspace 그룹 |
| 별도 State | 공유 설정 |
| 고유 Variables | Team 권한 관리 |

### Run Workflow

```
Plan → Cost Estimation → Policy Check → Apply
```

---

## 최종 점검

**시험 준비 완료 기준:**
- ✅ Mock Exam Set 1: 80% 이상
- ✅ 모든 도메인 70% 이상
- ✅ Labs 5개 이상 완료
- ✅ 핵심 암기사항 숙지

**시험 신청:**
https://www.hashicorp.com/certification/terraform-associate

---

**Good luck! 🎉**

---

## 참고 자료

- [HCP Terraform](https://developer.hashicorp.com/terraform/cloud-docs)
- [Workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)
- [Projects](https://developer.hashicorp.com/terraform/cloud-docs/projects)
- [Run Workflow](https://developer.hashicorp.com/terraform/cloud-docs/run/states)
- [Policy as Code](https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement)
