---
title: "도메인별 집중 연습 문제"
description: "Legacy study material imported from practice-exams/domain-specific-questions.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

이 문서는 각 도메인별로 추가 연습 문제를 제공합니다. 취약한 도메인을 집중적으로 보완하는 데 활용하세요.

---

## Domain 1: Infrastructure as Code Concepts

### Quick Review Questions

1. **IaC의 주요 이점을 3가지 나열하세요**
   <details>
   <summary>답</summary>
   
   1. 재현성 (Reproducibility)
   2. 버전 관리 (Version Control)
   3. 자동화 (Automation)
   </details>

2. **Declarative vs Imperative 차이는?**
   <details>
   <summary>답</summary>
   
   - **Declarative**: "무엇을" 원하는지 명시 (Terraform, Kubernetes)
   - **Imperative**: "어떻게" 만들지 명시 (Bash scripts)
   </details>

3. **Terraform이 지원하는 환경 유형 3가지는?**
   <details>
   <summary>답</summary>
   
   1. Public Cloud (AWS, Azure, GCP)
   2. On-Premises (VMware, OpenStack)
   3. SaaS (GitHub, Datadog)
   </details>

---

## Domain 2: Terraform Fundamentals

### Quick Review Questions

1. **`.terraform.lock.hcl` 파일의 목적은?**
   <details>
   <summary>답</summary>
   
   Provider 버전과 체크섬을 고정하여 팀 전체가 동일한 버전 사용 보장
   </details>

2. **Provider Alias를 사용하는 시나리오 2가지는?**
   <details>
   <summary>답</summary>
   
   1. 여러 AWS 계정 관리
   2. 다중 리전 배포
   </details>

3. **`terraform init`이 하는 일 3가지는?**
   <details>
   <summary>답</summary>
   
   1. Provider 플러그인 다운로드
   2. Backend 초기화
   3. Child 모듈 다운로드
   </details>

---

## Domain 3: Core Terraform Workflow

### Quick Review Questions

1. **Terraform 기본 워크플로우 순서는?**
   <details>
   <summary>답</summary>
   
   ```
   init → validate → plan → apply
   ```
   </details>

2. **`terraform plan`과 `terraform apply`의 주요 차이 2가지는?**
   <details>
   <summary>답</summary>
   
   1. plan은 읽기 전용, apply는 인프라 수정
   2. plan은 승인 불필요, apply는 승인 필요 (기본)
   </details>

3. **State를 자동으로 refresh하는 명령어 2개는?**
   <details>
   <summary>답</summary>
   
   1. `terraform plan`
   2. `terraform apply`
   </details>

---

## Domain 4: Terraform Configuration

### Quick Review Questions

1. **Resource와 Data Source의 차이는?**
   <details>
   <summary>답</summary>
   
   - **Resource**: 인프라 생성/관리
   - **Data Source**: 기존 인프라 조회
   </details>

2. **`sensitive = true`가 하는 일은?**
   <details>
   <summary>답</summary>
   
   CLI 출력에서만 값을 숨김 (State 파일에는 평문 저장)
   </details>

3. **count vs for_each 중요한 차이는?**
   <details>
   <summary>답</summary>
   
   - **count**: 인덱스 기반, 중간 제거 시 재생성 위험
   - **for_each**: 키 기반, 안전한 제거
   </details>

4. **Variable Precedence 순서 (높음→낮음) 5단계는?**
   <details>
   <summary>답</summary>
   
   1. `-var` (명령줄)
   2. `-var-file`
   3. `terraform.tfvars`
   4. 환경 변수 `TF_VAR_*`
   5. `default` 값
   </details>

---

## Domain 5: Terraform Modules

### Quick Review Questions

1. **Module의 주요 목적 3가지는?**
   <details>
   <summary>답</summary>
   
   1. 재사용성
   2. 조직화
   3. 표준화
   </details>

2. **Module Source 5가지 유형은?**
   <details>
   <summary>답</summary>
   
   1. Local path
   2. Terraform Registry
   3. GitHub
   4. Generic Git
   5. S3
   </details>

3. **Module Output 참조 형식은?**
   <details>
   <summary>답</summary>
   
   ```
   module.<module_name>.<output_name>
   ```
   </details>

---

## Domain 6: State Management

### Quick Review Questions

1. **State 파일의 주요 역할 4가지는?**
   <details>
   <summary>답</summary>
   
   1. 리소스 매핑
   2. 메타데이터 저장
   3. 성능 향상
   4. 협업 지원
   </details>

2. **S3 Backend에서 State Locking을 제공하는 서비스는?**
   <details>
   <summary>답</summary>
   
   DynamoDB (S3 단독으로는 불가능)
   </details>

3. **`terraform state` 관련 명령어 5개는?**
   <details>
   <summary>답</summary>
   
   1. `terraform state list`
   2. `terraform state show`
   3. `terraform state mv`
   4. `terraform state rm`
   5. `terraform state pull/push`
   </details>

4. **Infrastructure Drift란?**
   <details>
   <summary>답</summary>
   
   State 파일과 실제 인프라 간의 불일치 (수동 변경 등으로 발생)
   </details>

---

## Domain 7: Maintain Infrastructure

### Quick Review Questions

1. **Deprecated 명령어와 대체 명령어는?**
   <details>
   <summary>답</summary>
   
   - `terraform taint` → `terraform apply -replace=`
   - `terraform refresh` → `terraform apply -refresh-only`
   </details>

2. **`terraform import`가 자동 생성하는 것은?**
   <details>
   <summary>답</summary>
   
   아무것도 자동 생성 안 함 (State만 업데이트, 구성 파일은 수동 작성)
   </details>

3. **Verbose logging 활성화 방법은?**
   <details>
   <summary>답</summary>
   
   ```bash
   export TF_LOG=DEBUG
   export TF_LOG_PATH=./terraform.log
   ```
   </details>

---

## Domain 8: HCP Terraform

### Quick Review Questions

1. **HCP Terraform의 주요 기능 4가지는?**
   <details>
   <summary>답</summary>
   
   1. Remote State Management
   2. 협업 기능
   3. Policy as Code
   4. Remote Execution
   </details>

2. **HCP Terraform Run Workflow 순서는?**
   <details>
   <summary>답</summary>
   
   ```
   Plan → Cost Estimation → Policy Check → Apply
   ```
   </details>

3. **HCP Workspaces vs CLI Workspaces 차이는?**
   <details>
   <summary>답</summary>
   
   - **HCP**: 독립적인 인프라 환경
   - **CLI**: 동일 구성의 State 분리
   </details>

---

## 실전 시나리오 문제

### Scenario 1: State 관리

**상황:**
팀원이 AWS Console에서 EC2 인스턴스의 instance_type을 `t2.micro`에서 `t2.small`로 변경했습니다.

**질문:**
1. `terraform plan` 실행 시 어떤 변경이 감지되나요?
2. 이 상황을 어떻게 해결해야 하나요?

<details>
<summary>답</summary>

**1. terraform plan 결과:**
```
~ resource "aws_instance" "web" {
    ~ instance_type = "t2.small" -> "t2.micro"
  }
```
→ Drift 감지!

**2. 해결 방법:**

**Option A: Terraform 구성 우선 (권장)**
```bash
terraform apply
```
→ instance_type을 t2.micro로 복원

**Option B: 수동 변경 수용**
```hcl
resource "aws_instance" "web" {
  instance_type = "t2.small"
}
```
→ 구성 파일 업데이트 후 apply
</details>

---

### Scenario 2: count vs for_each

**상황:**
3개의 S3 Bucket을 count로 생성했습니다:
```hcl
variable "buckets" {
  default = ["alpha", "beta", "gamma"]
}

resource "aws_s3_bucket" "app" {
  count  = length(var.buckets)
  bucket = var.buckets[count.index]
}
```

**질문:**
"beta" 버킷만 제거하려면 어떻게 해야 하나요?

<details>
<summary>답</summary>

**문제:**
```hcl
variable "buckets" {
  default = ["alpha", "gamma"]
}
```
→ `gamma`가 index 2 → 1로 변경되어 재생성됨!

**해결:**
for_each로 변경
```hcl
variable "buckets" {
  default = toset(["alpha", "beta", "gamma"])
}

resource "aws_s3_bucket" "app" {
  for_each = var.buckets
  bucket   = each.key
}
```

이제 "beta"만 안전하게 제거:
```hcl
variable "buckets" {
  default = toset(["alpha", "gamma"])
}
```
</details>

---

### Scenario 3: Remote State

**상황:**
팀원 2명이 동시에 `terraform apply`를 실행하려 합니다.

**질문:**
1. State Locking이 없으면 어떤 문제가 발생하나요?
2. S3 Backend에서 Locking을 활성화하려면?

<details>
<summary>답</summary>

**1. Locking 없을 때 문제:**
- State 파일 손상 가능
- 동시 변경으로 충돌
- 리소스 중복 생성/삭제

**2. S3 Locking 활성화:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

DynamoDB 테이블 생성:
```hcl
resource "aws_dynamodb_table" "terraform_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```
</details>

---

## 빠른 복습 체크리스트

### 시험 전 마지막 점검

**Core Workflow:**
- [ ] init → validate → plan → apply 순서
- [ ] plan은 읽기 전용
- [ ] fmt는 포맷팅만

**State:**
- [ ] State는 리소스 매핑
- [ ] S3 + DynamoDB = Locking
- [ ] import는 State만 업데이트

**Configuration:**
- [ ] count = 인덱스, for_each = 키
- [ ] sensitive는 CLI만 숨김
- [ ] Variable precedence 순서

**Modules:**
- [ ] module.<name>.<output>
- [ ] Registry, Git, Local 가능

**Lifecycle:**
- [ ] create_before_destroy
- [ ] prevent_destroy
- [ ] depends_on (명시적)

**HCP Terraform:**
- [ ] Plan → Cost → Policy → Apply
- [ ] Workspaces ≠ CLI workspaces

---

**도메인별 연습 완료! 실전 모의고사로 최종 점검하세요.**
