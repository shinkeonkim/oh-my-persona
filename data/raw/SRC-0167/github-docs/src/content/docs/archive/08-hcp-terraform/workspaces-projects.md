---
title: "Workspaces vs Projects 심화"
description: "Legacy study material imported from 08-hcp-terraform/workspaces-projects.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- HCP Terraform Workspace vs CLI Workspace 구분
- Project 로 Workspace 조직화
- Execution Modes 이해
- Workspace 조직화 전략

---

## 1. 개념 구분 (핵심!)

### HCP Terraform Workspace

- **독립적인 인프라 실행 환경**
- 별도 State, Variables, Execution
- Team 협업 지원
- Web UI + CLI + API

### CLI Workspace

- **동일 config 의 State 분리**
- `terraform.tfstate.d/` 디렉토리
- 단일 사용자 개념
- **HCP Workspace 와 완전히 다름!**

### 비교

| | HCP Workspace | CLI Workspace |
|-|---------------|---------------|
| 목적 | 독립 환경 | State 분리 |
| Config | 완전 독립 | 동일 |
| Variables | 완전 독립 | 공유 |
| Execution | 원격 (선택) | 로컬 |
| Team | ✅ | ❌ |
| 시험 관련 | ⭐⭐⭐ | ⭐ |

---

## 2. HCP Terraform 조직 계층

```
Organization
├── Project A
│   ├── Workspace A1
│   ├── Workspace A2
│   └── Workspace A3
├── Project B
│   ├── Workspace B1
│   └── Workspace B2
└── (Workspaces without Project)
```

**예시:**
```
Organization: my-company
├── Project: Infrastructure
│   ├── vpc-prod
│   ├── vpc-staging
│   └── vpc-dev
├── Project: Applications
│   ├── app-frontend-prod
│   ├── app-backend-prod
│   └── app-mobile-prod
└── Project: Security
    ├── iam-policies
    └── security-groups
```

---

## 3. Workspace 생성

### 3.1 UI 기반

**Workspace → New Workspace**

**Workflow 선택:**
1. **VCS-driven** - GitHub/GitLab 연동 자동 실행
2. **CLI-driven** - 로컬 CLI 로 실행
3. **API-driven** - API 로 자동화

### 3.2 CLI 기반 (cloud block)

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

**초기화:**
```bash
terraform login
terraform init
# Workspace 자동 생성 또는 연결
```

### 3.3 Tags 기반

```hcl
terraform {
  cloud {
    organization = "my-org"

    workspaces {
      tags = ["app", "prod"]
    }
  }
}
```

여러 workspace 를 tag 로 필터.

---

## 4. Workspace 설정

### 주요 설정

| 설정 | 설명 |
|------|------|
| **Name** | Workspace 이름 |
| **Description** | 설명 |
| **Project** | 소속 프로젝트 |
| **Terraform Version** | 사용 버전 |
| **Execution Mode** | Remote/Local/Agent |
| **Auto Apply** | 자동 apply 여부 |
| **Working Directory** | Terraform 실행 디렉토리 |
| **Trigger Patterns** | 트리거 파일 패턴 |
| **VCS Repository** | 연결된 저장소 |

### Execution Modes

**1. Remote (기본)**
- Terraform 실행이 HCP Terraform 에서
- 사용자는 CLI/UI 로 트리거만

**2. Local**
- 실행은 로컬 (사용자 머신)
- State 만 HCP Terraform 에

**3. Agent**
- 자체 인프라의 Agent 가 실행
- Private network 리소스 접근 가능

---

## 5. Project

### 목적

관련 Workspace 들을 **논리적으로 그룹화**.

### 이점

- **조직화:** 100+ workspace 관리 용이
- **Team 권한 관리:** Project 수준 role 부여
- **Variable Sets:** Project 별 공유 변수
- **Search/Filter:** UI 에서 필터링

### 생성

**Organization → Projects → New Project**

```
Name: Infrastructure
Description: Core infrastructure (VPC, IAM, DNS)
```

### Project 권한

| Role | 권한 |
|------|------|
| **Admin** | Project 및 Workspace 관리 |
| **Maintain** | Workspace CRUD |
| **Write** | Workspace 실행 |
| **Read** | State 조회 |

---

## 6. Workspace 조직화 전략

### 6.1 Environment 기반

```
├── app-dev
├── app-staging
└── app-prod
```

**장점:** 명확한 환경 분리
**단점:** Cross-env 종속성 관리 필요

### 6.2 Region 기반

```
├── app-us-east-1
├── app-us-west-2
└── app-eu-west-1
```

**장점:** 지역별 격리
**단점:** Global 리소스 별도 관리

### 6.3 Component 기반

```
├── network-prod
├── compute-prod
├── database-prod
└── monitoring-prod
```

**장점:** 관심사 분리, 병렬 배포
**단점:** Cross-workspace 종속성

### 6.4 Team 기반

```
├── team-a-service1
├── team-a-service2
├── team-b-service1
└── team-b-service2
```

### 6.5 Hybrid (권장)

```
Project: Infrastructure
├── network-prod-us-east-1
├── network-prod-us-west-2
├── network-staging-us-east-1

Project: Applications
├── app-frontend-prod
├── app-backend-prod
└── app-mobile-prod
```

**Environment + Component + Region 조합.**

---

## 7. Naming Conventions

### 권장 패턴

```
<service>-<environment>-<region>
├── vpc-prod-use1
├── app-prod-use1
├── vpc-prod-usw2
└── vpc-staging-use1
```

### Tag 활용

```
Tags:
- app: myapp
- env: prod
- region: us-east-1
- team: backend
```

---

## 8. CLI Workspace (별도!)

### 명령어

```bash
terraform workspace list           # 목록
terraform workspace new dev        # 생성
terraform workspace select prod    # 전환
terraform workspace show           # 현재
terraform workspace delete dev     # 삭제
```

### 변수 활용

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "myapp-${terraform.workspace}"
}
```

### State 분리

```
terraform.tfstate.d/
├── dev/
│   └── terraform.tfstate
├── staging/
│   └── terraform.tfstate
└── prod/
    └── terraform.tfstate
```

⚠️ HCP Workspace 와 다른 개념!

---

## 9. State Migration (Local → HCP)

```hcl
# Before: local state
terraform {
  # backend 없음
}

# After: HCP Terraform
terraform {
  cloud {
    organization = "my-org"
    workspaces { name = "prod-app" }
  }
}
```

```bash
terraform login
terraform init
# Do you want to migrate to Terraform Cloud?
#   Enter a value: yes
```

---

## 10. 시험 자주 나오는 함정

### 함정 1: Workspace 개념 구분

```
Q: HCP Workspace 와 CLI Workspace 는 같은가요?
A: ❌ NO. 완전히 다른 개념!
- HCP: 독립 환경 (config, state, vars 모두 별도)
- CLI: 동일 config 의 state 분리
```

### 함정 2: cloud block vs backend

```
Q: HCP Terraform 최신 방식은?
A: cloud block. backend "remote" 는 deprecated.
```

### 함정 3: Project 없이 Workspace?

```
Q: Workspace 는 Project 에 속해야 하나요?
A: 선택. Default project 또는 지정 project.
```

### 함정 4: Execution Mode

```
Q: Local execution mode 는 무엇을 로컬로?
A: Terraform 명령어 실행이 로컬.
   State 는 여전히 HCP.
```

---

## 참고 자료

- [HCP Terraform Workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)
- [Projects](https://developer.hashicorp.com/terraform/cloud-docs/projects)
- [cloud block](https://developer.hashicorp.com/terraform/cli/cloud/settings)
- 관련: [Variable Sets & Run Triggers](/archive/08-hcp-terraform/variables-triggers/), [Collaboration](/archive/08-hcp-terraform/collaboration/)
- 실습: [Lab 12: HCP Terraform](/archive/labs/lab-12-hcp-terraform/readme/)
