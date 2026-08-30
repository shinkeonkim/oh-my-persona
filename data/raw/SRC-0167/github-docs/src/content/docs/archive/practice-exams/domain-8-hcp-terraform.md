---
title: "Domain 8 문제 20개 / HCP Terraform"
description: "Twenty Terraform Associate 004 HCP Terraform practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 8 문제 20개입니다. Workspace, project, credential, policy 경계는 [HCP 책임 경계](/reference/hcp-boundaries/)를 함께 확인하세요.

## 📚 도메인 개요

HCP Terraform (구 Terraform Cloud) - Workspaces, VCS, Policy, Cost Estimation, 협업.

---

## 📝 연습 문제

### 문제 1: 🟢 Easy

HCP Terraform 의 이전 이름은?

- A) Terraform Enterprise
- B) Terraform Cloud
- C) Terraform Studio
- D) Terraform Hub

<details><summary>정답 및 해설</summary>

**정답: B**

Terraform Cloud → HCP Terraform 으로 rebranding.
</details>

### 문제 2: 🔴 Hard

HCP Workspace vs CLI Workspace 차이는?

- A) 같은 개념
- B) HCP 는 독립 환경, CLI 는 동일 config 의 state 분리
- C) HCP 는 무료, CLI 는 유료
- D) HCP 는 로컬, CLI 는 원격

<details><summary>정답 및 해설</summary>

**정답: B**

**시험 필수:** 완전히 다른 개념.
</details>

### 문제 3: 🔴 Hard

HCP Terraform Run 워크플로우 순서는?

- A) Plan → Apply → Cost → Policy
- B) Plan → Cost → Policy → Apply
- C) Cost → Plan → Policy → Apply
- D) Policy → Plan → Cost → Apply

<details><summary>정답 및 해설</summary>

**정답: B**

**시험 필수:** Plan → Cost Estimation → Policy Check → Apply.
</details>

### 문제 4: 🟡 Medium

Terraform 코드에서 HCP Terraform 사용 (최신 방식):

- A) `backend "remote" { ... }`
- B) `cloud { ... }` block
- C) `terraform-cloud { ... }`
- D) `hcp { ... }`

<details><summary>정답 및 해설</summary>

**정답: B**

`cloud` block이 HCP Terraform의 권장 integration 방식입니다. `backend "remote"`는 여전히 지원되지만 Terraform 1.1부터 built-in cloud integration이 권장됩니다.
</details>

### 문제 5: 🟢 Easy

HCP Terraform 인증 명령어:

- A) `terraform auth`
- B) `terraform login`
- C) `terraform connect`
- D) `terraform init -cloud`

<details><summary>정답 및 해설</summary>

**정답: B**

`terraform login` → token 발급.
</details>

### 문제 6: 🟡 Medium

Variable Sets Scope 3가지는?

- A) Global, Project, Workspace
- B) User, Team, Organization
- C) Public, Private, Shared
- D) Read, Write, Admin

<details><summary>정답 및 해설</summary>

**정답: A**
</details>

### 문제 7: 🔴 Hard

Run Trigger 의 방향은?

- A) Source 에서 destination 지정
- B) Destination 에서 source 지정
- C) 양방향
- D) Organization 수준에서

<details><summary>정답 및 해설</summary>

**정답: B**

Destination workspace 의 설정에서 source workspace 지정.
</details>

### 문제 8: 🟡 Medium

Sentinel Policy Enforcement Level 3가지는?

- A) Advisory, Soft Mandatory, Hard Mandatory
- B) Warning, Error, Critical
- C) Low, Medium, High
- D) Public, Private, Internal

<details><summary>정답 및 해설</summary>

**정답: A**

- Advisory: 경고
- Soft Mandatory: Override 가능
- Hard Mandatory: 강제
</details>

### 문제 9: 🟢 Easy

**True / False:** Sentinel 은 HashiCorp 자체 언어이다.

<details><summary>정답 및 해설</summary>

**정답: True**

Sentinel 은 HashiCorp. OPA (Rego) 는 CNCF.
</details>

### 문제 10: 🔴 Hard

Cost Estimation 이 지원하는 provider 는? (**Select THREE**)

- A) AWS
- B) Azure
- C) GCP
- D) Alibaba
- E) DigitalOcean

<details><summary>정답 및 해설</summary>

**정답: A, B, C**

AWS, Azure, GCP 만 공식 지원.
</details>

### 문제 11: 🟡 Medium

VCS-driven Workspace 의 특징이 **아닌** 것은?

- A) PR 시 자동 plan
- B) Merge 시 자동 apply (설정 시)
- C) 로컬에서 CLI 실행
- D) Trigger patterns 지원

<details><summary>정답 및 해설</summary>

**정답: C**

VCS-driven 은 원격 실행. Local CLI 는 CLI-driven.
</details>

### 문제 12: 🟢 Easy

Workspace Permissions 4가지는?

- A) Read, Plan, Write, Admin
- B) Read, Write, Delete, Admin
- C) View, Edit, Manage, Owner
- D) Guest, Member, Manager, Owner

<details><summary>정답 및 해설</summary>

**정답: A**
</details>

### 문제 13: 🔴 Hard

Sentinel Policy 예제:

```python
import "tfplan/v2" as tfplan

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_instance" implies
      rc.change.after.instance_type is "t3.micro"
  }
}
```

이 정책의 목적은?

- A) 모든 리소스를 검증
- B) EC2 인스턴스는 t3.micro 만 허용
- C) t3.micro 인스턴스만 생성
- D) EC2 삭제 방지

<details><summary>정답 및 해설</summary>

**정답: B**

모든 aws_instance 에 대해 t3.micro 인지 검증.
</details>

### 문제 14: 🟡 Medium

Team Token vs User Token 의 차이는?

- A) Team Token 은 team 권한, User Token 은 개인
- B) Team Token 은 더 강력
- C) 동일
- D) Team Token 만 CI/CD 에 사용 가능

<details><summary>정답 및 해설</summary>

**정답: A**

CI/CD 에는 Team Token 권장 (사용자 종속성 없음).
</details>

### 문제 15: 🟢 Easy

**True / False:** HCP Terraform 은 자체 State Locking 을 제공한다.

<details><summary>정답 및 해설</summary>

**정답: True**

기본 제공. 별도 설정 불필요.
</details>

### 문제 16: 🔴 Hard

HCP Terraform 무료 티어의 특징이 **아닌** 것은?

- A) 500 users
- B) 무제한 workspace
- C) Sentinel 정책
- D) Remote state

<details><summary>정답 및 해설</summary>

**정답: C**

Sentinel 은 Plus tier+.
</details>

### 문제 17: 🟡 Medium

Speculative Plan 이란?

- A) 실행 후 취소 가능한 plan
- B) PR 시 실행되는 plan (apply 불가)
- C) 미래 예측 plan
- D) Draft plan

<details><summary>정답 및 해설</summary>

**정답: B**

PR 검토용. Apply 되지 않음.
</details>

### 문제 18: 🟢 Easy

Project 의 목적은?

- A) Workspace 그룹화
- B) State 저장
- C) Variable 저장
- D) Provider 관리

<details><summary>정답 및 해설</summary>

**정답: A**

관련 Workspace 들을 논리적으로 묶어 관리.
</details>

### 문제 19: 🔴 Hard

`cloud` block 에서 tags 방식 사용:

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

동작은?

- A) 새 태그 생성
- B) 태그 매칭 workspace 사용
- C) 오류
- D) 무시됨

<details><summary>정답 및 해설</summary>

**정답: B**

Tags 로 여러 workspace 필터.
</details>

### 문제 20: 🟡 Medium

Run Trigger 는 Source apply 후 destination 에서 무엇을 실행?

- A) 자동 Apply
- B) 자동 Plan
- C) 자동 Destroy
- D) Notification 만

<details><summary>정답 및 해설</summary>

**정답: B**

**자동 Plan**. Apply 는 destination workspace 설정에 따름.
</details>

---

## 🎯 핵심 개념 정리

1. **HCP Workspace ≠ CLI Workspace** (완전히 다름!)
2. **Run 순서:** Plan → Cost Estimation → Policy Check → Apply
3. **cloud block** (권장) vs backend "remote" (지원되지만 cloud integration 권장)
4. **Variable Sets scope:** Global, Project, Workspace
5. **Enforcement Levels:** Advisory, Soft Mandatory, Hard Mandatory
6. **Policy engines:** Sentinel (HashiCorp), OPA (CNCF)
7. **Run Trigger:** Destination 에서 source 지정, 자동 Plan
8. **Cost Estimation:** AWS, Azure, GCP
9. **Team Token** for CI/CD

---

## 📚 관련 학습 자료

- [HCP Terraform](/archive/08-hcp-terraform/readme/)
- [Workspaces & Projects](/archive/08-hcp-terraform/workspaces-projects/)
- [Variable Sets & Run Triggers](/archive/08-hcp-terraform/variables-triggers/)
- [Policy as Code](/archive/08-hcp-terraform/policy/)
- [Collaboration](/archive/08-hcp-terraform/collaboration/)
- [Lab 12: HCP Terraform](/archive/labs/lab-12-hcp-terraform/readme/)
