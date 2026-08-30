---
title: "Drift Detection 및 해결"
description: "Legacy study material imported from 06-state/drift-detection.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Drift 개념 및 발생 원인
- Drift 감지 방법
- Drift 해결 전략 4가지
- HCP Terraform Health Assessments
- lifecycle ignore_changes 활용
- Continuous drift 대응

---

## 1. Drift 란?

### 정의

**Drift** 는 Terraform State 와 **실제 인프라** 간의 불일치를 의미합니다.

```
Terraform State (t3.micro)  ≠  Real Infrastructure (t3.small)
                              ↑
                          Drift!
```

### 발생 원인

**1. AWS Console 에서 수동 변경**
```
User → AWS Console → EC2 → Change instance_type
```

**2. 다른 IaC 도구 사용**
```
CloudFormation, Pulumi, Ansible 등이 같은 리소스 관리
```

**3. 자동화 스크립트**
```
Auto Scaling, Lambda, Cost optimizer
```

**4. 외부 사용자/시스템**
```
Backup automation, Compliance tools
```

**5. 프로바이더 버그**
```
드물지만 발생 가능
```

---

## 2. Drift 감지 방법

### 2.1 terraform plan (자동)

```bash
terraform plan

# Note: Objects have changed outside of Terraform
#
# Terraform detected the following changes made outside of Terraform since the last "terraform apply":
#
#   # aws_instance.web has been updated in-place
#   ~ resource "aws_instance" "web" {
#         id = "i-1234567890abcdef0"
#       ~ instance_type = "t3.micro" -> "t3.small"
#     }
#
# Unless you have made equivalent changes to your configuration, or ignored the relevant attributes using ignore_changes, the following plan may include actions to undo or respond to these changes.
```

Terraform 이 자동으로:
1. State 를 refresh (실제 조회)
2. State vs Config 비교
3. 차이점 표시

### 2.2 terraform apply -refresh-only

```bash
terraform apply -refresh-only

# Note: Objects have changed outside of Terraform
# ~ instance_type = "t3.micro" -> "t3.small"
#
# Would you like to update the Terraform state to reflect these detected changes?
#   Enter a value: yes
```

**동작:**
- 리소스 변경 없이 **State 만 최신화**
- 실제 인프라 상태를 State 에 반영

### 2.3 terraform show

```bash
terraform show

# 현재 state 확인
```

### 2.4 HCP Terraform Health Assessments

**설정:**
- Workspace → Settings → Health
- Enable Drift Detection
- Schedule: Daily / Weekly

**동작:**
```
매일 새벽 → 자동 plan 실행 → drift 감지 → 알림
```

**결과:**
```
Health: Drift Detected

Drifted Resources: 3
├── aws_instance.web       (instance_type changed)
├── aws_security_group.sg  (ingress rule added)
└── aws_s3_bucket.data     (tag modified)
```

---

## 3. Drift 종류

### 3.1 Attribute Drift

**가장 흔한 유형:** 속성 값이 변경됨.

```hcl
# Config:
instance_type = "t3.micro"

# Real: "t3.small"
```

### 3.2 Resource 삭제 (외부)

**시나리오:** 누군가 AWS Console 에서 삭제.

```
State: aws_instance.web (i-1234...)
Real:  (존재 안 함)
```

**Plan 출력:**
```
  # aws_instance.web has been deleted
  # (external change, view details in the "External Changes" section)
```

### 3.3 Resource 추가 (외부)

**시나리오:** 다른 도구가 리소스 생성. Terraform 은 모름.

```
State: (없음)
Real:  aws_instance.other (i-5678...)
```

**Terraform 은 알 수 없음** → State 밖 리소스.

### 3.4 Configuration vs Real 불일치

```hcl
# Config: 새로운 태그 추가
tags = {
  Name = "web"
  NewTag = "value"  # 추가
}

# State: 이전 상태
# Real: 이전 상태
```

**Plan:**
```
~ tags = {
    + "NewTag" = "value"
    "Name" = "web"
  }
```

---

## 4. Drift 해결 전략 (4가지)

### 전략 1: Terraform 구성 우선 (Reconcile)

**상황:** Config 가 진실. 실제 인프라를 config 로 복원.

```bash
terraform plan
# ~ instance_type = "t3.small" -> "t3.micro"

terraform apply
# 실제 인프라를 t3.micro 로 복원
```

**사용 케이스:**
- 무단 변경 감지
- Compliance 강제
- Config as source of truth

### 전략 2: 실제 상태 수용 (Accept)

**상황:** 실제 변경이 의도된 것. Config 를 업데이트.

**Config 업데이트:**
```hcl
resource "aws_instance" "web" {
  instance_type = "t3.small"  # 변경사항 수용
}
```

```bash
terraform plan
# No changes

terraform apply
# 아무것도 안 함
```

**사용 케이스:**
- 긴급 대응 (수동 변경 후 config 반영)
- 필요한 변경이었음
- Legacy 통합

### 전략 3: Refresh Only (State 동기화)

**상황:** State 만 최신화 (config 변경 없이).

```bash
terraform apply -refresh-only
```

**동작:**
- State ← Real Infrastructure
- Config 는 다음 plan 에서 처리

**사용 케이스:**
- 대량 drift 정리
- State 감사

### 전략 4: Import (외부 리소스 흡수)

**상황:** 외부에서 생성된 리소스를 Terraform 관리로.

```hcl
import {
  to = aws_instance.imported
  id = "i-5678..."
}

resource "aws_instance" "imported" {
  # config...
}
```

```bash
terraform apply
```

**사용 케이스:**
- 기존 인프라 Terraform 화
- 다른 도구에서 마이그레이션

---

## 5. HCP Terraform Health Assessments

### 5.1 Continuous Validation

**목적:** 자동으로 drift 및 config 문제 감지.

### 5.2 설정

```
Workspace → Settings → Health
├── Drift Detection: Enabled
├── Assessment Schedule: Every 24 hours
└── Notifications: Slack, Email
```

### 5.3 자동 Plan 실행

```
매일 새벽:
1. Refresh state
2. Compare with configuration
3. Report drift + assertion failures
4. Send notifications
```

### 5.4 Drift Report

**UI 표시:**
```
Health Status: Drift Detected

Detected Changes:
├── aws_instance.web
│   ~ instance_type: "t3.micro" → "t3.small"
│   
├── aws_security_group.web
│   + New ingress rule: port 8080
│   
└── aws_s3_bucket.logs
    - Missing tag: "CostCenter"

Last Assessment: 2 hours ago
Next Assessment: In 22 hours
```

### 5.5 Alerting

**Slack:**
```
🚨 Drift Detected: workspace/prod-app
3 resources have drifted from configuration.
View: https://app.terraform.io/...
```

---

## 6. lifecycle ignore_changes

### 목적
특정 속성의 변경을 **의도적으로 무시**.

### 6.1 특정 속성 무시

```hcl
resource "aws_autoscaling_group" "web" {
  min_size         = 1
  max_size         = 10
  desired_capacity = 2

  lifecycle {
    ignore_changes = [
      desired_capacity  # Auto Scaling 이 조정하는 값
    ]
  }
}
```

**결과:**
- ASG 가 desired_capacity 를 6으로 조정해도
- Terraform 은 2로 되돌리지 않음

### 6.2 태그 일부 무시

```hcl
resource "aws_instance" "web" {
  tags = {
    Name = "WebServer"
  }

  lifecycle {
    ignore_changes = [
      tags["LastModified"],
      tags["AutoUpdatedAt"]
    ]
  }
}
```

### 6.3 모든 속성 무시

```hcl
lifecycle {
  ignore_changes = all
}
```

⚠️ **거의 사용 안 함:** 리소스를 Terraform 이 관리 안 하는 것과 같음.

### 6.4 실전 예제

**RDS 비밀번호:**
```hcl
resource "aws_db_instance" "main" {
  password = var.initial_password

  lifecycle {
    ignore_changes = [password]  # 이후 수동 rotation
  }
}
```

**Auto Scaling:**
```hcl
resource "aws_autoscaling_group" "web" {
  min_size         = 2
  max_size         = 20
  desired_capacity = 4

  lifecycle {
    ignore_changes = [desired_capacity]
  }
}
```

**Lambda 코드 (CI/CD 관리):**
```hcl
resource "aws_lambda_function" "app" {
  function_name    = "my-app"
  filename         = "initial-code.zip"
  source_code_hash = filebase64sha256("initial-code.zip")

  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash
    ]
  }
}
```

---

## 7. Drift 방지

### 7.1 IAM 정책 (권한 최소화)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "ec2:ModifyInstance*",
        "ec2:TerminateInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalTag/Team": "DevOps"
        }
      }
    }
  ]
}
```

### 7.2 CloudTrail 감사

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=i-1234567890abcdef0 \
  --max-items 10
```

### 7.3 Config Rules

AWS Config 로 규칙 위반 감지:
```
Rule: ec2-instance-managed-by-terraform
├── Resource: aws_instance
├── Condition: Must have tag "ManagedBy=Terraform"
└── Non-compliant: Auto-remediate or alert
```

### 7.4 Policy as Code (Sentinel/OPA)

```
# 프로덕션에서 무단 변경 차단
```

자세한 내용은 [Policy as Code](/archive/08-hcp-terraform/policy/) 참고.

---

## 8. 실전 시나리오

### 시나리오 1: 급한 Console 변경 → Config 동기화

**상황:** Alice 가 응급 상황으로 Console 에서 인스턴스 타입 변경.

```bash
# 1. Drift 감지
terraform plan
# ~ instance_type = "t3.small" -> "t3.micro"

# 2. Alice 에게 확인
# → "긴급 스케일업이었어요. 유지해주세요"

# 3. Config 업데이트
vim main.tf
# instance_type = "t3.small"

# 4. Plan 확인 (변경 없어야)
terraform plan
# No changes

# 5. State 정리 (선택)
terraform apply -refresh-only
```

### 시나리오 2: Auto Scaling drift 지속

**상황:** ASG desired_capacity 가 매번 drift.

```hcl
resource "aws_autoscaling_group" "web" {
  desired_capacity = 4

  lifecycle {
    ignore_changes = [desired_capacity]
  }
}
```

**결과:**
```bash
terraform plan
# No changes  ← ASG 가 값을 바꿔도 무시
```

### 시나리오 3: 대량 Drift 정리

**상황:** 여러 리소스가 drift. 실제 상태를 그대로 수용.

```bash
# 1. Refresh only
terraform apply -refresh-only

# 2. Config 업데이트 (수동 or 자동 생성)
terraform plan  # 여전히 diff 표시
# → 각 diff 를 config 에 반영

# 3. 최종 확인
terraform plan
# No changes
```

### 시나리오 4: 외부 리소스 흡수 (Import)

**상황:** Console 에서 만든 인스턴스를 Terraform 으로.

```hcl
# 1. Import 블록 추가
import {
  to = aws_instance.imported
  id = "i-5678..."
}

resource "aws_instance" "imported" {
  # 최소한의 필드 (구체는 apply 후 확인)
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

# 2. Config 생성
terraform plan -generate-config-out=imported.tf

# 3. Apply
terraform apply

# 4. Config 정리
# generated.tf 검토, main.tf 로 이동
```

### 시나리오 5: HCP Terraform 알림 대응

**Slack 알림:**
```
🚨 Drift in prod-app workspace
- aws_instance.web: instance_type changed
Action: https://app.terraform.io/...
```

**대응:**
```bash
# 1. Terraform 로컬 실행
terraform login
terraform init

# 2. Plan 으로 확인
terraform plan

# 3. 원인 조사 (CloudTrail)
# → 누가 언제 변경?

# 4. 결정
# → 롤백: terraform apply
# → 수용: config 업데이트
```

---

## 9. Continuous Drift 대응 프로세스

### Weekly Drift Review

```
Monday:
├── HCP Terraform → All workspaces → Drift status
├── 각 drift 원인 조사
├── 해결 방안 결정 (rollback/accept/import)
└── PR 생성

Wednesday:
├── PR 리뷰 및 merge
└── Apply

Friday:
├── Drift status 재확인
└── 개선 액션 (권한 조정, 프로세스)
```

### Monthly Audit

```
1. Drift 발생 빈도 통계
2. Top drift-prone resources 식별
3. Prevention 개선 (IAM, Policy)
4. 문서 업데이트
```

---

## 10. Best Practices

### ✅ DO

- **정기적 drift 감지** (HCP Health Assessment)
- **CloudTrail 로 변경 추적**
- **ignore_changes 를 신중히 사용**
- **IAM 권한 최소화**
- **Policy as Code 적용**
- **팀 프로세스 문서화**

### ❌ DON'T

- Drift 무시
- 자동 apply 로 강제 rollback (위험)
- `ignore_changes = all` 남용
- Console 에서 무단 변경 (팀 문화)

---

## 11. 시험 자주 나오는 함정

### 함정 1: Drift 감지 명령어

```
Q: Drift 는 어떻게 감지하나요?
A: terraform plan 실행 시 자동 감지.
   또는 terraform apply -refresh-only.
```

### 함정 2: refresh 명령어

```
Q: terraform refresh 는 살아있나요?
A: ❌ Deprecated. terraform apply -refresh-only 사용.
```

### 함정 3: ignore_changes 효과

```
Q: ignore_changes 는 실제 인프라를 변경 방지하나요?
A: ❌ NO. Terraform 이 변경을 감지 안 함.
   실제 변경은 그대로 유지.
```

### 함정 4: -refresh-only 동작

```
Q: apply -refresh-only 는 리소스를 변경하나요?
A: ❌ NO. State 만 업데이트.
```

### 함정 5: HCP Terraform Drift

```
Q: HCP Terraform 은 자동으로 drift 를 감지하나요?
A: ✅ Health Assessments 활성화 시.
   설정 필요 (자동 아님).
```

---

## 참고 자료

- [Detect Drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)
- [HCP Terraform Drift Detection](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/health)
- [ignore_changes](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle#ignore_changes)
- 관련 문서: [State 기본](/archive/03-core-workflow/state-basics/), [State 명령어](/archive/06-state/state-commands/), [Lifecycle](/archive/07-lifecycle/readme/)
- 실습: [Lab 10: State 조작](/archive/labs/lab-10-state-manipulation/readme/)
