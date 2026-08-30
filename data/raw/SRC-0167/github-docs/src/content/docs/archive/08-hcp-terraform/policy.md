---
title: "Policy as Code (Sentinel & OPA) 완전 가이드"
description: "Legacy study material imported from 08-hcp-terraform/policy.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Policy as Code 개념
- Sentinel 언어 기초
- OPA (Rego) 기초
- Enforcement Levels
- Cost Estimation
- Run Tasks

---

## 1. Policy as Code 개요

**목적:** 인프라 변경을 자동으로 검증하여 조직 정책 강제.

**질문 예시:**
- "모든 EC2 는 태그 필수"
- "프로덕션 DB 는 암호화 필수"
- "특정 인스턴스 타입만 허용"
- "월 $10,000 초과 금지"

**HCP Terraform 지원:**
- **Sentinel** (HashiCorp)
- **OPA** (Open Policy Agent)

---

## 2. Policy Workflow

```
1. terraform plan
2. Cost Estimation (자동)
3. Policy Check (Sentinel/OPA) ← 여기!
4. Manual Approval (선택)
5. terraform apply
```

**시험 필수:** Plan → Cost → Policy → Apply 순서.

---

## 3. Sentinel

### 특징

- HashiCorp 자체 언어
- Terraform, Vault, Consul 등에 사용
- HCL 과 유사한 문법
- Import 로 데이터 접근

### 기본 구조

```python
import "tfplan/v2" as tfplan

allowed_types = ["t2.micro", "t3.micro", "t3.small"]

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_instance" implies
      rc.change.after.instance_type in allowed_types
  }
}
```

### Import 종류

- `tfplan/v2` - Plan 데이터
- `tfconfig/v2` - Config 데이터
- `tfstate/v2` - State 데이터
- `tfrun` - Run 메타데이터

### 실전 Policy 예제

**예제 1: 인스턴스 타입 제한**
```python
import "tfplan/v2" as tfplan

allowed = ["t2.micro", "t3.micro", "t3.small"]

instances = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_instance" and
  rc.change.actions is not ["delete"]
}

main = rule {
  all instances as _, i {
    i.change.after.instance_type in allowed
  }
}
```

**예제 2: 태그 필수화**
```python
import "tfplan/v2" as tfplan

required_tags = ["Environment", "Owner", "CostCenter"]

taggable = ["aws_instance", "aws_s3_bucket", "aws_db_instance"]

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type in taggable implies
      all required_tags as tag {
        tag in keys(rc.change.after.tags)
      }
  }
}
```

**예제 3: S3 암호화 강제**
```python
import "tfplan/v2" as tfplan

buckets = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_s3_bucket_server_side_encryption_configuration"
}

main = rule {
  all buckets as _, b {
    b.change.after.rule[0].apply_server_side_encryption_by_default[0].sse_algorithm in ["AES256", "aws:kms"]
  }
}
```

**예제 4: 특정 리전 강제**
```python
import "tfplan/v2" as tfplan

allowed_regions = ["us-east-1", "us-west-2"]

main = rule {
  tfplan.terraform_version matches "1\\..*" and
  all tfplan.variables as name, v {
    name is "region" implies v.value in allowed_regions
  }
}
```

---

## 4. Enforcement Levels

### 3가지 수준

| Level | 실패 시 |
|-------|--------|
| **Advisory** | 경고만, apply 진행 |
| **Soft Mandatory** | Override 가능 (권한 필요) |
| **Hard Mandatory** | 반드시 통과, override 불가 |

### 예제

**Advisory:**
```
✋ Policy Warning: Missing tags
Would you like to proceed anyway?
[Continue]
```

**Soft Mandatory:**
```
❌ Policy Failed: Instance type not allowed
Override requires "Manage Policy Overrides" permission.
[Request Override]
```

**Hard Mandatory:**
```
❌ Policy Failed: S3 must be encrypted
This policy cannot be overridden.
[Cancel Run]
```

---

## 5. Policy Sets

### 목적

**여러 Policy 를 논리적으로 묶어 workspace 에 적용.**

### 생성

**Settings → Policy Sets → Create**

```
Name: production-security
Policies:
  ├── require-tags.sentinel (hard-mandatory)
  ├── restrict-instance-types.sentinel (soft-mandatory)
  └── enforce-encryption.sentinel (hard-mandatory)

Scope:
  ○ All workspaces
  ● Selected workspaces
    - prod-app
    - prod-db
```

### VCS 연동

```
Repository: my-org/sentinel-policies
Branch: main

Structure:
├── sentinel.hcl (policies list)
├── policies/
│   ├── require-tags.sentinel
│   └── restrict-types.sentinel
```

**sentinel.hcl:**
```hcl
policy "require-tags" {
  source            = "./policies/require-tags.sentinel"
  enforcement_level = "hard-mandatory"
}

policy "restrict-types" {
  source            = "./policies/restrict-types.sentinel"
  enforcement_level = "soft-mandatory"
}
```

---

## 6. OPA (Open Policy Agent)

### 특징

- CNCF Graduated 프로젝트
- Rego 언어
- 범용 (Kubernetes, API Gateway 등에도 사용)

### 기본 구조

```text
package terraform

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_instance"
  not resource.change.after.tags.Environment
  msg := sprintf("Instance %s missing Environment tag", [resource.address])
}
```

### 실전 예제

**예제 1: Instance Type 제한**
```text
package terraform

allowed_types := {"t3.micro", "t3.small", "t3.medium"}

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_instance"
  not resource.change.after.instance_type in allowed_types
  msg := sprintf(
    "Instance %s uses disallowed type %s",
    [resource.address, resource.change.after.instance_type]
  )
}
```

**예제 2: Region 제한**
```text
package terraform

allowed_regions := {"us-east-1", "us-west-2"}

deny[msg] {
  input.variables.region.value
  not input.variables.region.value in allowed_regions
  msg := sprintf(
    "Region %s not allowed",
    [input.variables.region.value]
  )
}
```

### Sentinel vs OPA

| | Sentinel | OPA |
|-|----------|-----|
| 벤더 | HashiCorp | CNCF |
| 언어 | Sentinel | Rego |
| HCP Support | ✅ Native | ✅ Native |
| 범용성 | Terraform 위주 | Kubernetes, 등 |
| 학습 곡선 | 낮음 (HCL 유사) | 중간 |

---

## 7. Cost Estimation

### 자동 계산

```
Plan 실행 시 자동으로 예상 비용 계산.
```

**출력 예:**
```
Cost Estimation:
  Resources: 5 to add, 0 to change, 0 to destroy

  + aws_instance.web
      $8.03/mo   (730 hours × $0.011)

  + aws_rds_instance.db
      $72.00/mo  (db.t3.micro)

  Total delta: +$80.03/mo
  New monthly total: $150.00
```

### 지원 Provider

- ✅ AWS
- ✅ Azure
- ✅ Google Cloud

### Policy 와 연동

```python
import "tfrun"

max_cost = 500  # $500/month

main = rule {
  tfrun.cost_estimate.proposed_monthly_cost < max_cost
}
```

---

## 8. Run Tasks

### 목적

**외부 서비스와 통합** (Snyk, Checkov, HashiCorp Vault 등).

### Workflow

```
Plan → Cost → Policy → Run Task (Pre-apply) → Apply → Run Task (Post-apply)
```

### 지원 통합

- **Snyk** - 보안 취약점 스캔
- **Checkov** - IaC 정적 분석
- **JFrog Xray** - 라이선스/보안
- **Custom** - HTTP endpoint

### 설정

**1. Organization → Settings → Run Tasks → Create**
```
Name: snyk-scan
Endpoint URL: https://snyk-terraform-hook.example.com
HMAC Key: (선택, 인증용)
```

**2. Workspace 에 연결**
```
Workspace → Settings → Run Tasks → Add
├── snyk-scan
│   ├── Stage: Pre-apply
│   └── Enforcement: Mandatory
```

**3. 결과 예**
```
🔍 Snyk Scan
├── High: 2 vulnerabilities
├── Medium: 5
└── Low: 12

Enforcement: Mandatory
Run blocked. Fix vulnerabilities.
```

---

## 9. Policy Failure Workflow

### Soft Mandatory Override

```
1. Policy 실패
2. UI: "Override" 버튼 표시 (권한 있는 사용자)
3. Override 이유 입력 (필수)
4. Audit log 에 기록
5. Apply 진행
```

**필요 권한:** Manage Policy Overrides

### Hard Mandatory

```
1. Policy 실패
2. Run 취소
3. Config 수정 필요
4. 재실행
```

---

## 10. 실전 시나리오

### 시나리오: Production 안전 정책

```python
# policies/prod-safety.sentinel
import "tfplan/v2" as tfplan
import "tfrun"

# Prod workspace 만 적용
is_prod = tfrun.workspace.name matches "prod-.*"

# 1. Prevent destroy of critical resources
critical_types = ["aws_rds_instance", "aws_dynamodb_table"]

no_destroy_critical = rule {
  all tfplan.resource_changes as _, rc {
    (rc.type in critical_types and is_prod) implies
      "delete" not in rc.change.actions
  }
}

# 2. Require encryption
require_encryption = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_db_instance" implies
      rc.change.after.storage_encrypted is true
  }
}

# 3. Restrict instance types
prod_types = ["t3.large", "t3.xlarge", "m5.large", "m5.xlarge"]

restrict_types = rule {
  all tfplan.resource_changes as _, rc {
    (rc.type is "aws_instance" and is_prod) implies
      rc.change.after.instance_type in prod_types
  }
}

main = rule {
  no_destroy_critical and
  require_encryption and
  restrict_types
}
```

**sentinel.hcl:**
```hcl
policy "prod-safety" {
  source            = "./policies/prod-safety.sentinel"
  enforcement_level = "hard-mandatory"
}
```

---

## 11. Best Practices

### ✅ DO

- **점진적 도입** (Advisory → Soft → Hard)
- **테스트 환경에서 먼저 검증**
- **Policy 를 VCS 로 관리**
- **문서화** (왜 이 정책인가)
- **팀과 협의** 후 Hard Mandatory
- **Cost Estimation 활용**

### ❌ DON'T

- 처음부터 Hard Mandatory
- 이해되지 않는 정책 강제
- Override 를 남용
- 정책 없이 프로덕션 운영

---

## 12. 시험 자주 나오는 함정

### 함정 1: Enforcement Levels 순서

```
Q: Enforcement level 3가지는?
A: Advisory (경고), Soft Mandatory (override 가능), Hard Mandatory (강제).
```

### 함정 2: HCP Terraform Run Order

```
Q: Run 워크플로우 순서는?
A: Plan → Cost Estimation → Policy Check → Apply
```

### 함정 3: Sentinel vs OPA

```
Q: HCP Terraform 은 두 정책 엔진 지원?
A: ✅ YES. Sentinel + OPA.
```

### 함정 4: Cost Estimation 지원 Provider

```
Q: Cost Estimation 은 어떤 provider 지원?
A: AWS, Azure, GCP.
```

---

## 참고 자료

- [Sentinel](https://developer.hashicorp.com/sentinel)
- [OPA in HCP Terraform](https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement/opa)
- [Cost Estimation](https://developer.hashicorp.com/terraform/cloud-docs/cost-estimation)
- [Run Tasks](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-tasks)
- 관련: [Workspaces & Projects](/archive/08-hcp-terraform/workspaces-projects/), [Collaboration](/archive/08-hcp-terraform/collaboration/)
