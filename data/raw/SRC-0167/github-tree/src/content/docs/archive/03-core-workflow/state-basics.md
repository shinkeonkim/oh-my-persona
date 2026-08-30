---
title: "State 파일 기본 이해"
description: "Legacy study material imported from 03-core-workflow/state-basics.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- State 파일의 목적과 필요성 이해
- State 파일 구조 (JSON schema)
- State Refresh 메커니즘
- State 파일 보안 주의사항
- State 백업 전략

---

## 1. State 파일이란?

### 정의

**terraform.tfstate** 는 Terraform 이 관리하는 인프라의 **현재 상태**를 저장하는 JSON 파일입니다.

### 위치

- **Local Backend (기본):** 현재 디렉토리의 `terraform.tfstate`
- **Remote Backend:** S3, Azure Blob, GCS, HCP Terraform 등

---

## 2. State 는 왜 필요한가?

### 2.1 Configuration ↔ Real World 매핑

```
Terraform Configuration          Real World Infrastructure
─────────────────────────         ─────────────────────────
resource "aws_instance" "web"     AWS EC2 Instance
   ↓                                 ↓
  ID?                             i-1234567890abcdef0

         ↕
     State 파일이 이 매핑을 저장
```

**State 없다면:**
```hcl
resource "aws_instance" "web" {
  # ...
}
```
→ Terraform 은 어떤 EC2 인스턴스가 이 리소스인지 알 수 없음!

### 2.2 메타데이터 저장

- Resource ID
- 속성 값
- 종속성 관계
- Provider 정보

### 2.3 성능 최적화

- 매 실행마다 모든 리소스를 API 로 조회하면 **매우 느림**
- State 에 저장된 정보로 빠른 계획 생성
- 필요시에만 refresh (API 호출)

### 2.4 팀 협업

- Remote State 로 여러 사용자가 동일 인프라 관리
- State Locking 으로 동시 변경 방지

---

## 3. State 파일 구조

### 3.1 전체 구조

```json
{
  "version": 4,
  "terraform_version": "1.12.0",
  "serial": 12,
  "lineage": "3d5e9a45-abc1-...",
  "outputs": {
    "instance_ip": {
      "value": "54.123.45.67",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "web",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "id": "i-1234567890abcdef0",
            "ami": "ami-12345678",
            "instance_type": "t2.micro",
            "public_ip": "54.123.45.67",
            "private_ip": "10.0.1.10",
            "tags": {
              "Name": "WebServer"
            }
          },
          "dependencies": [
            "aws_security_group.web"
          ]
        }
      ]
    }
  ],
  "check_results": null
}
```

### 3.2 주요 필드 설명

| 필드 | 목적 |
|------|------|
| `version` | State schema 버전 (4가 최신) |
| `terraform_version` | 이 state 를 생성한 Terraform 버전 |
| `serial` | Increment 되는 순번 (변경마다 +1) |
| `lineage` | Unique state 식별자 |
| `outputs` | Output 값들 |
| `resources` | 관리 리소스들 |
| `check_results` | Check block 결과 (1.5+) |

### 3.3 Resource 필드

| 필드 | 설명 |
|------|------|
| `mode` | `managed` (resource) 또는 `data` (data source) |
| `type` | 리소스 타입 (예: `aws_instance`) |
| `name` | 리소스 이름 |
| `provider` | Provider 참조 |
| `instances` | 인스턴스 배열 (count/for_each 시 여러 개) |
| `attributes` | 실제 속성 값 |
| `dependencies` | 명시적/암묵적 종속성 |

---

## 4. State 파일 관련 파일들

### 4.1 terraform.tfstate

현재 State 파일.

### 4.2 terraform.tfstate.backup

이전 State 파일 (자동 백업).

```bash
ls -la terraform.tfstate*
# terraform.tfstate           # 현재
# terraform.tfstate.backup    # 직전 백업
```

### 4.3 .terraform.tfstate.lock.info

State lock 정보 (locking 활성화 시).

```json
{
  "ID": "abc-123-def-456",
  "Operation": "OperationTypeApply",
  "Info": "",
  "Who": "user@hostname",
  "Version": "1.12.0",
  "Created": "2026-07-21T10:00:00Z",
  "Path": "terraform.tfstate"
}
```

---

## 5. State Refresh

### 5.1 Refresh 란?

Real world 인프라 상태를 조회하여 State 를 최신화하는 과정.

### 5.2 자동 Refresh

```bash
terraform plan     # 시작 시 자동 refresh
terraform apply    # 시작 시 자동 refresh
```

### 5.3 Refresh 비활성화

```bash
terraform plan -refresh=false
terraform apply -refresh=false
```

**사용 케이스:**
- API 호출 최소화 (매우 큰 인프라)
- Rate limit 회피
- CI/CD 속도 향상

### 5.4 Refresh Only

```bash
terraform apply -refresh-only
```

- 리소스 변경 없이 State 만 최신화
- Drift 감지 및 반영에 유용

⚠️ Deprecated: `terraform refresh` → 사용하지 마세요.

---

## 6. State 에 저장되는 민감 정보

### 6.1 저장되는 정보

- 데이터베이스 비밀번호
- API 키
- Private 키
- Sensitive variable 값 (**평문!**)

### 6.2 위험

```hcl
variable "db_password" {
  type      = string
  sensitive = true  # CLI 출력만 마스킹
}

resource "aws_db_instance" "example" {
  password = var.db_password
}
```

**State 파일에는 평문 저장:**
```json
{
  "attributes": {
    "password": "MyActualPassword123!"
  }
}
```

### 6.3 보호 방법

1. **Remote Backend + 암호화**
   ```hcl
   terraform {
     backend "s3" {
       bucket  = "my-tfstate"
       key     = "prod.tfstate"
       encrypt = true
     }
   }
   ```

2. **접근 제어 (IAM/RBAC)**

3. **State 파일 .gitignore**
   ```
   *.tfstate
   *.tfstate.*
   *.tfstate.backup
   ```

4. **Ephemeral Values 활용 (Terraform 1.10+)**
   ```hcl
   variable "api_token" {
     ephemeral = true  # State 저장 안 됨
   }
   ```

5. **Write-only Arguments (Terraform 1.11+)**
   ```hcl
   resource "aws_db_instance" "example" {
     password_wo         = var.password
     password_wo_version = 1
   }
   ```

자세한 내용은 [Sensitive Data 관리](/archive/07-lifecycle/sensitive-data/) 참고.

---

## 7. State 파일 관리 원칙

### ✅ DO

- **Remote Backend 사용** (팀 협업)
- **State Locking 활성화** (DynamoDB, HCP)
- **암호화 적용** (SSE, KMS)
- **Versioning 활성화** (S3 bucket)
- **정기 백업**
- **.gitignore 로 로컬 state 제외**
- **State 조작은 terraform 명령어로만** (state mv, rm)

### ❌ DON'T

- **수동으로 state 파일 편집** ❌❌❌
- Git 에 state 파일 커밋
- State 파일을 여러 사람이 공유 (로컬 backend)
- State 파일 삭제 (인프라 관리 불가능해짐!)
- 무단으로 force-unlock

---

## 8. State 파일 손상 시 복구

### 8.1 백업 활용

```bash
cp terraform.tfstate.backup terraform.tfstate
```

### 8.2 S3 Versioning 활용

```bash
aws s3api list-object-versions \
  --bucket my-tfstate \
  --prefix prod.tfstate

# 이전 버전 복구
aws s3api get-object \
  --bucket my-tfstate \
  --key prod.tfstate \
  --version-id <VERSION_ID> \
  terraform.tfstate
```

### 8.3 State 재구성 (최후 수단)

```bash
# 1. State 초기화
rm terraform.tfstate

# 2. 각 리소스 수동 import
terraform import aws_instance.web i-1234567890abcdef0
terraform import aws_s3_bucket.data my-bucket-name

# 3. Plan 으로 검증
terraform plan
```

---

## 9. State Refresh vs Drift

### Refresh
```
State ← Real Infrastructure
```
State 를 실제 인프라 상태로 업데이트.

### Drift
```
State ≠ Real Infrastructure
```
Terraform 밖에서 변경된 상태.

### 예제

**Terraform Config:**
```hcl
resource "aws_instance" "web" {
  instance_type = "t2.micro"
}
```

**State:**
```
instance_type = "t2.micro"
```

**Real Infrastructure (AWS Console 에서 수동 변경):**
```
instance_type = "t2.small"
```

### plan 실행

```bash
terraform plan

# Note: Objects have changed outside of Terraform
# 
# aws_instance.web has been updated in-place
# Resource actions are indicated with the following symbols:
#   ~ update in-place
# 
#   # aws_instance.web will be updated in-place
#   ~ resource "aws_instance" "web" {
#         id            = "i-1234567890abcdef0"
#       ~ instance_type = "t2.small" -> "t2.micro"
#     }
```

→ **Drift 감지**! Config 로 복원 예정.

자세한 내용은 [Drift Detection](/archive/06-state/drift-detection/) 참고.

---

## 10. State 관련 명령어 요약

```bash
terraform state list                # 리소스 목록
terraform state show <resource>     # 상세 조회
terraform state mv <src> <dst>      # 이름 변경
terraform state rm <resource>       # State 에서 제거
terraform state pull                # Remote → 로컬 (백업)
terraform state push <file>         # 로컬 → Remote (위험!)
```

자세한 내용은 [State 명령어 상세](/archive/06-state/state-commands/) 참고.

---

## 11. 시험 자주 나오는 함정

### 함정 1: sensitive 의 한계

```
Q: sensitive = true 변수는 State 에 암호화되나요?
A: ❌ NO. State 에는 평문 저장. CLI 출력만 마스킹.
```

### 함정 2: State 수동 편집

```
Q: State 파일을 직접 수정해도 되나요?
A: ❌ NO. 절대 하지 마세요. terraform state 명령어 사용.
```

### 함정 3: State 삭제

```
Q: terraform.tfstate 를 삭제하면?
A: 인프라와의 연결 상실. destroy 불가. 수동 import 필요.
```

### 함정 4: State Locking Backend

```
Q: 어떤 Backend 가 Locking 을 지원하나요?
A: S3 + DynamoDB, Azure Blob, GCS, HCP Terraform, Consul.
   S3 alone: ❌ NO (DynamoDB 필요)
```

### 함정 5: refresh 명령어

```
Q: terraform refresh 를 사용해도 되나요?
A: ❌ Deprecated. terraform apply -refresh-only 사용.
```

---

## 12. Best Practices

1. **Remote Backend 필수** (팀 협업)
2. **State Locking 활성화**
3. **암호화 (at rest, in transit)**
4. **정기 백업 + Versioning**
5. **접근 제어 최소화**
6. **State 파일은 절대 Git 에 커밋 X**
7. **State 조작은 명령어로만**
8. **Sensitive 데이터는 Ephemeral/Write-only 활용**

---

## 참고 자료

- [Terraform State](https://developer.hashicorp.com/terraform/language/state)
- [State Purpose](https://developer.hashicorp.com/terraform/language/state/purpose)
- [Sensitive Data in State](https://developer.hashicorp.com/terraform/language/state/sensitive-data)
- 관련 문서: [Remote Backend](/archive/06-state/remote-backend/), [State Locking](/archive/06-state/state-locking/), [State 명령어](/archive/06-state/state-commands/), [Drift Detection](/archive/06-state/drift-detection/)
