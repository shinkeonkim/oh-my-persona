---
title: "HCP Terraform 협업 워크플로우"
description: "Legacy study material imported from 08-hcp-terraform/collaboration.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Organization, Team, User 관리
- Role-based Access Control (RBAC)
- VCS 통합 (GitHub, GitLab 등)
- Pull Request 자동화
- API Tokens 관리
- Private Registry
- HCP Terraform 요금제

---

## 1. Organization 관리

### 구조

```
Organization: my-company
├── Users (Members)
├── Teams
├── Projects
├── Workspaces
└── Registries (Modules, Providers)
```

### Organization Roles

| Role | 권한 |
|------|------|
| **Owners** | 모든 권한 (Billing 포함) |
| **Members** | Team/Workspace 참여 |

Owner 는 소수 (2-3명) 로 유지.

---

## 2. Teams

### Team 생성

```
Settings → Teams → Create Team
Name: DevOps
Description: DevOps 팀
```

### 특수 Team

- **owners** - 자동 생성, Org owners
- **Team members** - 사용자 초대

### Team Tokens

```
Teams → DevOps → Team API Token → Generate

Token: xxxxxxxxxxxxxx
```

**용도:** CI/CD 자동화, Team 권한으로 API 호출.

---

## 3. Permissions

### Organization Permissions

| Permission | 설명 |
|-----------|------|
| **Manage Policies** | Sentinel/OPA policies 관리 |
| **Manage Policy Overrides** | Soft mandatory override |
| **Manage Workspaces** | Workspace 생성 |
| **Manage VCS Settings** | VCS provider 설정 |
| **Manage Providers** | Provider registry |
| **Manage Modules** | Module registry |
| **Manage Run Tasks** | Run task 관리 |
| **Manage Membership** | 사용자/팀 관리 |

### Project Roles

| Role | 권한 |
|------|------|
| **Admin** | 모든 project 권한 |
| **Maintain** | Workspace CRUD |
| **Write** | Workspace 실행 |
| **Read** | State 조회 |

### Workspace Permissions

| Permission | 설명 |
|-----------|------|
| **Read** | State, Variables 조회 |
| **Plan** | Plan 실행 가능 |
| **Write** | Apply 실행 가능 |
| **Admin** | 설정 변경 가능 |

### Custom Permissions

```
Read Runs: [✓]
Read Variables: [✓]
Read State: [✓]
Read State Outputs: [✓]
Queue Plans: [✓]
Apply Runs: [ ]
Manage Variables: [ ]
Manage Runs: [ ]
Lock/Unlock: [ ]
```

---

## 4. VCS 통합

### 지원 Provider

- ✅ GitHub / GitHub Enterprise
- ✅ GitLab (Cloud, EE)
- ✅ Bitbucket (Cloud, Server)
- ✅ Azure DevOps

### 설정

**1. VCS Provider 추가**
```
Settings → VCS Providers → Add
├── Provider: GitHub
├── OAuth: Authorize
└── Save
```

**2. Workspace 연결**
```
Workspace → Settings → Version Control
├── VCS Provider: GitHub
├── Repository: my-org/terraform-infra
├── Branch: main
├── Working Directory: infrastructure/prod
├── Auto Apply: [ ]
└── Trigger Patterns: infrastructure/prod/**/*.tf
```

---

## 5. Pull Request Workflow

### 자동 Plan

```
GitHub PR 생성
   ↓ (Webhook)
HCP Terraform: Speculative Plan
   ↓
Plan 결과 PR comment 로 표시
```

**PR Comment 예:**
```
Terraform Cloud Plan
Workspace: prod-app
Status: Plan finished

Plan: 3 to add, 1 to change, 0 to destroy

+ aws_instance.new_web
~ aws_s3_bucket.data (tags)

Details: https://app.terraform.io/...
```

### 자동 Apply (Merge 시)

```
PR Approved & Merged
   ↓
HCP Terraform: Full Plan + Apply
   ↓
Slack 알림
```

**설정:**
```
Workspace → Settings → Auto Apply: [✓]
```

⚠️ **Production 은 Auto Apply 비권장** (수동 승인 유지).

### Manual Approval

```
Plan 완료
   ↓
UI: "Confirm & Apply" 버튼
   ↓
Approver 클릭
   ↓
Apply 시작
```

### Draft PR / Speculative Plan

**Draft PR:** Plan 만 실행, Apply 대기.

---

## 6. Comments & Discussions

Workspace 페이지에서 팀원과 소통.

```
Run 상세 페이지
├── Plan 결과
├── Cost Estimation
├── Policy Check
├── Comments:
│   ├── @alice: LGTM
│   ├── @bob: Cost 확인했습니다
│   └── Approver: Approved by @alice
└── Actions: Approve | Discard
```

---

## 7. Notification 설정

### 지원 채널

- Slack
- Microsoft Teams
- Email
- Generic Webhook

### 이벤트

- Runs planning
- Runs needs attention
- Runs applying
- Runs completed
- Runs errored
- Assessment drift detected
- Assessment failed
- Assessment health

---

## 8. Audit Logging

### Organization Audit Trail

**Settings → Audit Trail** (Enterprise only)

**기록되는 이벤트:**
- User login
- Team membership change
- Workspace CRUD
- Variable change
- Run 실행
- Policy override

**Export:**
- JSON, CSV
- SIEM 연동

---

## 9. API Tokens

### 3가지 유형

**1. User Token**
- 개인 사용자
- 사용자 권한 상속

**2. Team Token**
- Team 대신 실행
- Team 권한 상속
- CI/CD 에 적합

**3. Organization Token**
- Organization 관리
- 최고 권한 (owners)
- 신중히 사용

**4. Agent Token**
- Terraform Agent 인증
- Agent Pool 마다 별도

### 생성

```
User Settings → Tokens → Create API Token

# 저장 (한번만 표시)
```

### 사용

```bash
export TFC_TOKEN=xxxxxxxxxxxxxx

curl \
  --header "Authorization: Bearer $TFC_TOKEN" \
  https://app.terraform.io/api/v2/organizations/my-org/workspaces
```

---

## 10. Private Module Registry

### Module 게시

**1. Repository 준비**
```
Naming: terraform-<PROVIDER>-<NAME>
예: terraform-aws-mymodule

Structure:
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
└── examples/

Tags: Semantic version (v1.0.0)
```

**2. HCP Terraform 등록**
```
Registry → Modules → Publish
├── Provider: GitHub
├── Repository: my-org/terraform-aws-mymodule
└── Save
```

**3. 사용**
```hcl
module "mymodule" {
  source  = "app.terraform.io/my-org/mymodule/aws"
  version = "1.0.0"
}
```

---

## 11. Private Provider Registry

### 자체 Provider 게시

```hcl
terraform {
  required_providers {
    custom = {
      source  = "app.terraform.io/my-org/custom"
      version = "~> 1.0"
    }
  }
}
```

**용도:** 내부 API 를 Terraform Provider 로 노출.

---

## 12. HCP Terraform 요금제

### Free Tier

- Users: 최대 500명
- Concurrent runs: 제한
- State storage: 무제한
- Private modules: 무제한
- Remote execution: 500분/월

### Standard

- Unlimited runs
- Team RBAC
- HCP Vault Secrets integration

### Plus

- Sentinel
- OPA
- Cost estimation
- Drift detection
- Advanced RBAC
- Concurrent runs

### Enterprise (Self-hosted)

- Air-gapped
- SSO/SAML
- Audit logging
- 자체 인프라 배포

---

## 13. 실전 협업 시나리오

### 시나리오 1: 소규모 팀 (5명)

```
Organization: startup-inc
├── Team: developers (5명)
│   ├── Read-write on all workspaces
│   └── Policy override 없음

Workflow:
├── PR → Auto Plan
├── Team review
├── Merge → Auto Apply (dev, staging)
└── Manual Apply (prod)
```

### 시나리오 2: 중규모 팀 (여러 프로젝트)

```
Organization: my-company
├── Teams:
│   ├── infrastructure-team (10명) - VPC, IAM
│   ├── backend-team (15명) - Backend apps
│   ├── frontend-team (10명) - Frontend apps
│   └── ops-team (5명) - 모든 것 admin

├── Projects:
│   ├── Infrastructure (infrastructure-team: admin)
│   ├── Backend Apps (backend-team: admin)
│   └── Frontend Apps (frontend-team: admin)

├── Variable Sets:
│   ├── AWS Credentials (per project)
│   └── Common Tags (global)

├── Notifications:
│   ├── #infra-alerts
│   ├── #backend-alerts
│   └── #frontend-alerts
```

### 시나리오 3: Enterprise (거버넌스 강화)

```
Organization: enterprise-corp
├── SSO: SAML
├── Audit: SIEM integration

├── Teams (수십 개, 각 팀 read-only + specific write)

├── Policies (Hard Mandatory):
│   ├── Tag enforcement
│   ├── Encryption enforcement
│   ├── Region restriction
│   └── Instance type restriction

├── Policy Overrides: manager-team only

├── Run Tasks:
│   ├── Snyk (security scan)
│   ├── Checkov (IaC compliance)
│   └── Custom cost gate

├── Drift Detection: Daily
└── Notifications: PagerDuty for errors
```

---

## 14. Migration (Self-managed → HCP)

### 단계

**1. HCP Terraform 계정 생성**
**2. Organization 생성**
**3. Workspace 생성** (workflow: CLI-driven)
**4. VCS Provider 연결** (선택)
**5. Backend 마이그레이션**

```hcl
# Before
terraform {
  backend "s3" { ... }
}

# After
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

---

## 15. Best Practices

### ✅ DO

- **RBAC 최소 권한**
- **Team 단위 권한 부여** (개인 X)
- **Variable Sets 로 secrets 관리**
- **VCS-driven workflow**
- **Notification 필수 설정**
- **Audit logs 정기 검토**
- **Prod 은 Manual Apply**

### ❌ DON'T

- 모두를 Admin 으로
- Organization token 남용
- Prod 에 Auto Apply
- Audit 없이 운영

---

## 16. 시험 자주 나오는 함정

### 함정 1: Team Token vs User Token

```
Q: CI/CD 에는 어떤 token?
A: Team Token (개인 사용자 종속성 없음).
```

### 함정 2: Speculative Plan

```
Q: PR 시 실행되는 plan 은?
A: Speculative Plan (실행 계획만, apply 안 됨).
```

### 함정 3: Auto Apply 위치

```
Q: Auto Apply 는 어디 설정?
A: Workspace → Settings → Auto Apply.
```

### 함정 4: Free Tier

```
Q: Free tier 는 몇 명까지?
A: 500 users.
```

---

## 참고 자료

- [HCP Terraform Users, Teams, Organizations](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations)
- [VCS Integration](https://developer.hashicorp.com/terraform/cloud-docs/vcs)
- [API Tokens](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens)
- [Private Registry](https://developer.hashicorp.com/terraform/cloud-docs/registry)
- 관련: [Workspaces & Projects](/archive/08-hcp-terraform/workspaces-projects/), [Variable Sets](/archive/08-hcp-terraform/variables-triggers/), [Policy](/archive/08-hcp-terraform/policy/)
