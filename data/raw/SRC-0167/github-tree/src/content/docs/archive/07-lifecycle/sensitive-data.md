---
title: "Sensitive Data 관리 완전 가이드"
description: "Legacy study material imported from 07-lifecycle/sensitive-data.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- sensitive = true 의 한계 이해
- Ephemeral Values (Terraform 1.10+, 004 신규!)
- Write-Only Arguments (Terraform 1.11+, 004 신규!)
- Secret Management 통합
- State 파일 보안

---

## 1. 핵심 문제

**Terraform State 파일에는 민감 정보가 평문으로 저장됩니다.**

```hcl
variable "db_password" {
  type      = string
  sensitive = true  # CLI 출력만 마스킹!
}

resource "aws_db_instance" "main" {
  password = var.db_password
}
```

**State 파일:**
```json
{
  "attributes": {
    "password": "MyActualPassword123!"  ← 평문!
  }
}
```

---

## 2. sensitive = true

### CLI 출력 마스킹

```hcl
variable "api_key" {
  type      = string
  sensitive = true
}

output "app_config" {
  value = {
    api_key = var.api_key
  }
  sensitive = true
}
```

**CLI:**
```
app_config = <sensitive>
```

### 한계

- ❌ State 파일: **평문 저장**
- ❌ Plan 파일: **평문 저장**
- ❌ 실제 보안: **없음**

### nonsensitive() 함수

```hcl
output "processed" {
  value = nonsensitive(var.some_sensitive)  # 명시적 해제
}
```

---

## 3. Ephemeral Values (Terraform 1.10+, 004 신규!)

### 목적

**State/Plan 에 저장 안 되는** 값.

### Ephemeral Variables

```hcl
variable "api_token" {
  type      = string
  ephemeral = true
}
```

**특징:**
- ✅ State 저장 안 됨
- ✅ Plan 파일 저장 안 됨
- ✅ 실행 중에만 존재
- ❌ Output 으로 노출 불가 (ephemeral output 만 가능)

### Ephemeral Outputs (Terraform 1.11+)

```hcl
output "temp_token" {
  value     = ephemeral_random.token.result
  ephemeral = true
}
```

### Ephemeral Resources

```hcl
ephemeral "random_password" "db" {
  length = 32
}

resource "aws_db_instance" "main" {
  password = ephemeral.random_password.db.result
}
```

### 사용 사례

- 임시 API 토큰
- 세션 자격증명
- OAuth token
- 단기 인증서

---

## 4. Write-Only Arguments (Terraform 1.11+, 004 신규!)

### 목적

Resource attribute 를 **State 에 저장하지 않음**.

### 예제: RDS Password

```hcl
resource "aws_db_instance" "main" {
  identifier = "mydb"
  # ...

  password_wo         = var.db_password    # State 저장 X
  password_wo_version = 1                   # 버전 관리
}
```

**Version 관리:**
```hcl
password_wo_version = 2  # 값 변경 시 증가
```

### 지원 리소스 (일부)

- `aws_db_instance.password_wo`
- `aws_rds_cluster.master_password_wo`
- `aws_secretsmanager_secret_version.secret_string_wo`
- 기타 provider 지원 확대 중

### password vs password_wo

| | password | password_wo |
|-|----------|-------------|
| State 저장 | ✅ 평문 | ❌ |
| Drift 감지 | ✅ | ❌ |
| Version 관리 | ❌ | ✅ (password_wo_version) |
| 값 변경 감지 | 값 비교 | Version 비교 |

---

## 5. Secret Management 통합

### 5.1 AWS Secrets Manager

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "main" {
  password_wo         = data.aws_secretsmanager_secret_version.db_password.secret_string
  password_wo_version = 1
}
```

### 5.2 HashiCorp Vault

```hcl
provider "vault" {
  address = "https://vault.example.com"
}

data "vault_kv_secret_v2" "db" {
  mount = "secret"
  name  = "database"
}

resource "aws_db_instance" "main" {
  password_wo = data.vault_kv_secret_v2.db.data["password"]
}
```

### 5.3 AWS SSM Parameter Store

```hcl
data "aws_ssm_parameter" "db_password" {
  name = "/prod/db/password"
}

resource "aws_db_instance" "main" {
  password_wo = data.aws_ssm_parameter.db_password.value
}
```

### 5.4 Azure Key Vault

```hcl
data "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  key_vault_id = data.azurerm_key_vault.main.id
}
```

### 5.5 GCP Secret Manager

```hcl
data "google_secret_manager_secret_version" "db_password" {
  secret = "db-password"
}
```

---

## 6. .gitignore 필수 항목

```
# Terraform State (절대 커밋 X)
*.tfstate
*.tfstate.*
*.tfstate.backup

# Variable 파일 (민감 정보 포함 시)
*.tfvars
!example.tfvars

# Crash
crash.log

# Terraform 디렉토리
.terraform/
.terraform.lock.hcl  # ← 커밋! (이건 예외)

# Plan 파일 (민감 정보 포함)
*.tfplan
tfplan

# 로그
*.log
```

⚠️ `.terraform.lock.hcl` 는 커밋! (버전 고정용).

---

## 7. Remote Backend 암호화

### S3 SSE

```hcl
terraform {
  backend "s3" {
    bucket  = "my-tfstate"
    key     = "prod/terraform.tfstate"
    encrypt = true                                    # SSE-S3
    kms_key_id = "arn:aws:kms:..."                    # SSE-KMS
    dynamodb_table = "terraform-lock"
  }
}
```

### Bucket 강제 암호화

```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.state.arn
    }
  }
}
```

---

## 8. HCP Terraform Sensitive Variables

**UI:**
- Variables → Add variable → "Sensitive" 체크

**동작:**
- 값이 UI 에 표시 안 됨
- Run log 에서 마스킹
- API 로도 조회 불가

**저장 방식:** 암호화 저장.

---

## 9. 실전 시나리오

### 시나리오: DB 비밀번호 완전 안전 관리

```hcl
# 1. Secret 은 별도 Secret Manager 에 저장
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db/master-password"
}

# 2. Write-only 로 State 저장 방지
resource "aws_db_instance" "main" {
  identifier = "prod-db"

  password_wo         = data.aws_secretsmanager_secret_version.db_password.secret_string
  password_wo_version = 1

  # 비밀번호 이외 다른 속성
  engine         = "postgres"
  instance_class = "db.t3.large"
}

# 3. 비밀번호 rotation 시 version 증가
# password_wo_version = 2
```

**결과:**
- ✅ 비밀번호는 Secrets Manager 에만
- ✅ Terraform State 에 저장 안 됨
- ✅ Rotation 지원

---

## 10. Best Practices

### ✅ DO

- **Ephemeral values** 사용 (임시 값)
- **Write-only arguments** 사용 (비밀번호)
- **Secret Manager 통합** (Vault, SSM, Secrets Manager)
- **Remote Backend + KMS 암호화**
- **.gitignore 로 tfstate 제외**
- **HCP Terraform sensitive variables**

### ❌ DON'T

- `sensitive = true` 만 믿기
- 비밀번호를 코드에 하드코딩
- tfvars 파일을 Git 에 커밋
- State 파일을 public 하게 노출
- Plan 파일을 안전하지 않게 저장

---

## 11. 시험 자주 나오는 함정

### 함정 1: sensitive 의 한계

```
Q: sensitive = true 는 State 를 암호화하나요?
A: ❌ NO. CLI 출력만 마스킹. State 는 평문.
```

### 함정 2: Ephemeral 도입 시기

```
Q: Ephemeral variables 는 언제 도입?
A: Terraform 1.10+ (004 신규!)
```

### 함정 3: Write-only 도입 시기

```
Q: Write-only arguments 는 언제 도입?
A: Terraform 1.11+ (004 신규!)
```

### 함정 4: password_wo_version

```
Q: password_wo_version 은 왜 필요?
A: State 에 값이 없어서 변경 감지 불가.
   Version 을 증가시켜 apply 트리거.
```

---

## 참고 자료

- [Sensitive Data](https://developer.hashicorp.com/terraform/language/state/sensitive-data)
- [Ephemeral Values](https://developer.hashicorp.com/terraform/language/values/variables#exclude-values-from-state)
- [Write-only Arguments](https://developer.hashicorp.com/terraform/language/resources/ephemeral/write-only)
- 관련 문서: [Custom Conditions](/archive/07-lifecycle/custom-conditions/), [Variables 상세](/archive/04-configuration/variables-outputs/)
