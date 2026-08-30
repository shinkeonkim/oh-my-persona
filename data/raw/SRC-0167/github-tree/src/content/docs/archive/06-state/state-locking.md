---
title: "State Locking 심화"
description: "Legacy study material imported from 06-state/state-locking.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- State Locking 의 목적 및 원리
- Backend별 Locking 지원 여부
- DynamoDB Lock Table 설계
- Lock 획득 및 해제 프로세스
- force-unlock 사용법과 위험성
- Locking 문제 해결

---

## 1. State Locking 이란?

### 정의

**State Locking** 은 여러 사용자가 **동시에** Terraform 을 실행할 때 발생할 수 있는 **State 파일 충돌**을 방지하는 메커니즘입니다.

### 왜 필요한가?

**시나리오 (Locking 없음):**
```
Time  User A                          User B
────  ────────────────────────        ────────────────────────
T1    terraform apply 시작
T2    State 읽기
T3                                    terraform apply 시작
T4                                    State 읽기 (같은 상태)
T5    리소스 생성
T6    State 쓰기 (변경사항 A)
T7                                    리소스 생성
T8                                    State 쓰기 (변경사항 B)
                                       ← A의 변경사항 손실!
```

**결과:** State 손상, 리소스 중복, 인프라 불일치.

### Locking 원리

```
Time  User A                          User B
────  ────────────────────────        ────────────────────────
T1    Lock 획득
T2    State 읽기
T3                                    Lock 획득 시도 → 실패!
                                       Error: State locked
T4    작업 수행
T5    State 쓰기
T6    Lock 해제
T7                                    Lock 획득 성공
T8                                    작업 계속
```

---

## 2. Backend별 Locking 지원

### 지원 여부 표

| Backend | Locking 지원 | 방법 |
|---------|--------------|------|
| local | ✅ | 파일 시스템 |
| s3 | ⚠️ | **DynamoDB 필요** |
| azurerm | ✅ | Blob Lease (기본) |
| gcs | ✅ | 기본 제공 |
| consul | ✅ | Consul lock |
| http | 옵션 | HTTP API |
| kubernetes | ✅ | Kubernetes Lease |
| pg | ✅ | PostgreSQL advisory lock |
| HCP Terraform (cloud) | ✅ | 기본 제공 |
| etcdv3 | ❌ | - |
| oss | ⚠️ | Tablestore 필요 |

⚠️ **시험 필수:** S3 는 **DynamoDB 없이 Locking 불가능**.

---

## 3. S3 + DynamoDB Locking

### 3.1 DynamoDB Table 요구사항

**Schema:**
- Table Name: 자유
- Primary Key: `LockID` (String)

**최소 IAM 권한:**
- `GetItem`, `PutItem`, `DeleteItem`

### 3.2 Terraform 으로 DynamoDB 생성

```hcl
resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name    = "Terraform State Lock Table"
    Purpose = "State Locking"
  }
}
```

### 3.3 Billing Mode 선택

**PAY_PER_REQUEST (권장):**
- 요청당 과금
- 관리 불필요
- 소규모/불규칙 사용에 적합

**PROVISIONED:**
```hcl
resource "aws_dynamodb_table" "terraform_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### 3.4 Backend 설정

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"  # ⭐ 필수
  }
}
```

### 3.5 IAM 권한

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/terraform-state-lock"
    }
  ]
}
```

---

## 4. Lock 획득 프로세스

### 4.1 언제 Lock 이 획득되나?

**Lock 획득 명령어:**
- `terraform apply`
- `terraform destroy`
- `terraform plan -out=<file>` (선택)
- `terraform state <subcommand>` (일부)
- `terraform import`
- `terraform refresh` (deprecated)
- `terraform workspace <subcommand>`

**Lock 미획득:**
- `terraform plan` (기본, 저장 안 함)
- `terraform show`
- `terraform output`
- `terraform validate`
- `terraform fmt`

### 4.2 Lock Info 내용

**DynamoDB Item 예시:**
```json
{
  "LockID": {
    "S": "my-terraform-state/prod/terraform.tfstate-md5"
  },
  "Info": {
    "S": "{\"ID\":\"abc-123-def-456\",\"Operation\":\"OperationTypeApply\",\"Who\":\"user@hostname\",\"Version\":\"1.12.0\",\"Created\":\"2026-07-21T10:00:00Z\",\"Path\":\"my-terraform-state/prod/terraform.tfstate\"}"
  }
}
```

**필드:**
- `ID`: 고유 lock ID
- `Operation`: 수행 중인 작업
- `Who`: 사용자@호스트
- `Version`: Terraform 버전
- `Created`: Lock 획득 시각
- `Path`: State 파일 경로

### 4.3 Lock 자동 해제

- 정상 완료 시 자동 해제
- Terraform 프로세스 종료 시 해제 시도
- Crash / kill 시 해제 안 됨 (stale lock)

---

## 5. Lock 획득 실패 시나리오

### 시나리오 1: 다른 사용자가 apply 중

```bash
terraform apply

# Error: Error acquiring the state lock
# 
# Error message: ConditionalCheckFailedException: The conditional request failed
# 
# Lock Info:
#   ID:        abc-123-def-456
#   Path:      my-terraform-state/prod/terraform.tfstate
#   Operation: OperationTypeApply
#   Who:       alice@laptop
#   Version:   1.12.0
#   Created:   2026-07-21 10:00:00 +0000 UTC
```

**해결:** 기다림 (Alice 의 작업 완료 후 자동 해제).

### 시나리오 2: Lock Timeout

```bash
# 기본: 즉시 실패
terraform apply

# Lock 이 해제될 때까지 대기
terraform apply -lock-timeout=10m
```

**옵션:**
- `-lock-timeout=0s` : 즉시 실패 (기본)
- `-lock-timeout=5m` : 5분 대기
- `-lock-timeout=1h` : 1시간 대기

### 시나리오 3: Stale Lock (프로세스 죽음)

**증상:** Lock 이 해제되지 않고 남음.

**진단:**
```bash
aws dynamodb scan --table-name terraform-state-lock

# 오래된 Created 시간 확인
```

**해결:**
```bash
terraform force-unlock <LOCK_ID>
```

---

## 6. force-unlock

### 6.1 목적

Lock 을 강제로 해제.

### 6.2 문법

```bash
terraform force-unlock <LOCK_ID>
terraform force-unlock -force <LOCK_ID>   # 확인 건너뜀
```

### 6.3 Lock ID 확인

**Error 메시지에서:**
```
Lock Info:
  ID:        abc-123-def-456   # ← 이 값
```

**DynamoDB 조회:**
```bash
aws dynamodb scan \
  --table-name terraform-state-lock \
  --output json | jq -r '.Items[].Info.S | fromjson | .ID'
```

### 6.4 사용 시나리오

✅ **안전한 경우:**
- 프로세스가 죽음 (crash, kill)
- 네트워크 단절로 Lock 해제 실패
- Terraform 이 hang

❌ **위험한 경우:**
- 다른 사용자가 **실제로 apply 중**
- Lock 획득한 사용자와 협의 없이

### 6.5 위험성

**시나리오:**
```
User A: terraform apply 중 (Lock 획득)
User B: force-unlock 실행
User B: terraform apply 시작
User A: State 쓰기
User B: State 쓰기 → 충돌!
```

**결과:** State 손상, 리소스 불일치.

### 6.6 Best Practice

```bash
# 1. Slack/Teams 에 확인
# "누가 terraform apply 중인가요?"

# 2. DynamoDB Item 확인
aws dynamodb scan --table-name terraform-state-lock

# 3. Lock 시간 확인 (오래됐는지)
# Created: 2 hours ago → stale

# 4. 확실할 때만 force-unlock
terraform force-unlock abc-123-def-456
```

---

## 7. Concurrent Operations

### 7.1 여러 State 파일

각 state 는 **독립적으로 lock**.

```
Backend: s3
├── prod/network/terraform.tfstate      (Lock A)
├── prod/compute/terraform.tfstate      (Lock B)
└── prod/database/terraform.tfstate     (Lock C)
```

**Alice:** `network/` 작업 (Lock A 획득)
**Bob:** `compute/` 작업 (Lock B 획득) → 동시 가능

### 7.2 CI/CD 안전 실행

```yaml
# GitHub Actions
jobs:
  terraform:
    concurrency:
      group: terraform-${{ github.ref }}
      cancel-in-progress: false  # 이전 job 완료 대기
    steps:
      - run: terraform apply -auto-approve
```

---

## 8. HCP Terraform Locking

### 8.1 기본 제공

HCP Terraform 은 Workspace 수준에서 자동 lock.

### 8.2 Lock 이유

```hcl
terraform {
  cloud {
    organization = "my-org"
    workspaces { name = "prod" }
  }
}
```

**UI 에서 확인:**
- Workspace → Settings → Locking
- Lock reason 표시

### 8.3 수동 Lock

Workspace 를 명시적으로 lock (변경 방지):

```bash
terraform login
terraform workspace lock -reason="Prod maintenance"
```

**해제:**
```bash
terraform workspace unlock
```

---

## 9. State Lock 없이 실행

### -lock=false 옵션

```bash
terraform apply -lock=false
```

⚠️ **매우 위험:** 절대 프로덕션에서 사용 금지.

**허용되는 경우:**
- CI/CD 에서 read-only 작업 (plan)
- Backend 가 locking 미지원 (예: etcdv3)

---

## 10. Backend 별 Locking 상세

### Azure Blob Storage

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-rg"
    storage_account_name = "tfstate"
    container_name       = "state"
    key                  = "prod.tfstate"
  }
}
```

**Locking:** Blob Lease (60초 자동 갱신).

### GCS

```hcl
terraform {
  backend "gcs" {
    bucket = "my-tfstate"
    prefix = "prod"
  }
}
```

**Locking:** GCS object lock.

### Consul

```hcl
terraform {
  backend "consul" {
    address = "consul.example.com:8500"
    scheme  = "https"
    path    = "terraform/prod"
    lock    = true  # 기본 true
  }
}
```

---

## 11. 실전 시나리오

### 시나리오 1: 팀 협업

```
Alice:    terraform apply → Lock 획득
          ↓ (30초 소요)
          Lock 해제

Bob:      Alice 완료 후 terraform apply
```

**옵션 1: Alice 완료 대기**
```bash
# Bob:
terraform apply -lock-timeout=10m
```

**옵션 2: 확인 후 실행**
```bash
# Slack:
# Alice: "prod apply 중"
# Bob:   "완료되면 알려주세요"
```

### 시나리오 2: CI/CD 파이프라인

```yaml
# .github/workflows/terraform.yml
name: Terraform
on: push

concurrency:
  group: terraform-prod
  cancel-in-progress: false

jobs:
  apply:
    steps:
      - run: |
          terraform init
          terraform apply -auto-approve -lock-timeout=15m
```

### 시나리오 3: Stale Lock 복구

```bash
# 1. 문제 인지: 30분 전 시작된 apply 가 hang
terraform apply
# Error: Error acquiring the state lock (Created: 30 minutes ago)

# 2. 팀에 확인
# Slack: "@channel: 30분 전 prod apply 하신 분?"
# → 응답: "Alice, 네트워크 문제로 죽음"

# 3. force-unlock
aws dynamodb scan --table-name terraform-state-lock
# LockID 확인

terraform force-unlock abc-123-def-456
# Do you really want to force-unlock?
#   Enter a value: yes

# 4. 재시도
terraform apply
```

---

## 12. Monitoring

### DynamoDB Lock 모니터링

```bash
# 현재 활성 lock 조회
aws dynamodb scan \
  --table-name terraform-state-lock \
  --output json | jq '.Items[] | {
    LockID: .LockID.S,
    Info: (.Info.S | fromjson)
  }'
```

**CloudWatch Alarm (오래된 lock 감지):**
- Item 개수 > 0 이 30분 이상 지속 → Alert

---

## 13. Best Practices

### ✅ DO

- **DynamoDB Lock table 필수** (S3 backend)
- **Locking 지원 backend 만 사용** (프로덕션)
- **Lock timeout 설정** (`-lock-timeout=10m`)
- **CI/CD concurrency control**
- **Stale lock 은 확인 후 force-unlock**

### ❌ DON'T

- S3 만 사용 (DynamoDB 없이)
- `-lock=false` 프로덕션 사용
- 무단 force-unlock
- Lock 해제 없이 프로세스 kill

---

## 14. 시험 자주 나오는 함정

### 함정 1: S3 자체 Locking

```
Q: S3 backend 는 자체적으로 locking 을 제공하나요?
A: ❌ NO. DynamoDB 필요.
```

### 함정 2: DynamoDB Schema

```
Q: DynamoDB table 의 primary key 이름은?
A: LockID (String)
```

### 함정 3: force-unlock 위험성

```
Q: force-unlock 은 언제 사용해야 하나요?
A: Stale lock 인 확실할 때만. 다른 사람 apply 중이면 위험!
```

### 함정 4: local backend Locking

```
Q: local backend 도 locking 을 지원하나요?
A: ✅ YES (파일 시스템 기반, 단일 사용자용).
```

### 함정 5: HCP Terraform Locking

```
Q: HCP Terraform 은 별도 설정이 필요한가요?
A: ❌ NO. 기본 제공.
```

---

## 참고 자료

- [State Locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [force-unlock](https://developer.hashicorp.com/terraform/cli/commands/force-unlock)
- [S3 Backend Locking](https://developer.hashicorp.com/terraform/language/settings/backends/s3#dynamodb-state-locking)
- 관련 문서: [Remote Backend](/archive/06-state/remote-backend/), [State 명령어](/archive/06-state/state-commands/)
