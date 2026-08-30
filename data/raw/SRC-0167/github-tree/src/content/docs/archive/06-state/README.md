---
title: "Week 6: State Management"
description: "Legacy study material imported from 06-state/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- State 파일의 역할과 중요성 이해
- Local vs Remote Backend
- State Locking 이해
- State 조작 및 관리 기법
- Drift Detection 및 해결

---

## 1. Terraform State란?

### 정의

**terraform.tfstate**는 Terraform이 관리하는 인프라의 **현재 상태**를 저장하는 JSON 파일입니다.

### State의 역할

**1. 리소스 매핑**
```
Terraform Configuration ←→ Real World Resources
```

**2. 메타데이터 저장**
- Resource ID
- Dependencies
- Attribute values

**3. 성능 최적화**
- API 호출 최소화
- 대규모 인프라 관리

**4. 팀 협업**
- Remote State
- State Locking

---

## 2. State 파일 구조

```json
{
  "version": 4,
  "terraform_version": "1.12.0",
  "serial": 5,
  "lineage": "abc-123-def",
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
            "private_ip": "10.0.1.10"
          },
          "dependencies": ["aws_security_group.web"]
        }
      ]
    }
  ]
}
```

---

## 3. Local vs Remote Backend

### Local Backend (기본값)

**특징:**
- `terraform.tfstate` 파일로 저장
- 로컬 파일 시스템
- State Locking 없음

**장점:**
- 간단한 설정
- 빠른 시작

**단점:**
- 팀 협업 어려움
- 백업/복구 수동
- State 충돌 위험

```hcl
terraform {
}
```

### Remote Backend

**지원 Backend:**
- S3 + DynamoDB
- Azure Blob Storage
- Google Cloud Storage
- HCP Terraform
- Consul
- etcd

**S3 Backend 예시:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

**장점:**
- 팀 협업 가능
- 자동 백업
- State Locking (DynamoDB)
- 암호화 지원

---

## 4. State Locking

### 목적

동시에 여러 사용자가 `terraform apply` 실행 방지

### DynamoDB를 통한 Locking

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

### Lock 확인

```bash
aws dynamodb scan \
  --table-name terraform-state-lock
```

### Force Unlock

```bash
terraform force-unlock <LOCK_ID>
```

---

## 5. State 조작 명령어

### terraform state list

```bash
terraform state list

aws_instance.web
aws_s3_bucket.data
module.vpc.aws_vpc.main
```

### terraform state show

```bash
terraform state show aws_instance.web

# aws_instance.web:
resource "aws_instance" "web" {
    ami           = "ami-12345678"
    id            = "i-1234567890abcdef0"
    instance_type = "t2.micro"
    public_ip     = "54.123.45.67"
}
```

### terraform state mv

```bash
terraform state mv aws_instance.old aws_instance.new

terraform state mv \
  -state-out=other.tfstate \
  aws_instance.web \
  aws_instance.web
```

### terraform state rm

```bash
terraform state rm aws_instance.web
```
→ State에서만 제거, 실제 인프라는 유지

### terraform state pull/push

```bash
terraform state pull > backup.tfstate

terraform state push backup.tfstate
```

---

## 6. Drift Detection

### Drift란?

State와 실제 인프라 간의 불일치

**발생 원인:**
- AWS Console에서 수동 변경
- 다른 도구로 변경
- 외부 자동화

### Drift 감지

```bash
terraform plan

~ resource "aws_instance" "web" {
    ~ instance_type = "t2.small" -> "t2.micro"
  }
```

### Drift 해결

**Option 1: Terraform 구성 우선**
```bash
terraform apply
```
→ 실제 인프라를 구성에 맞춤

**Option 2: 실제 상태 수용**
```hcl
resource "aws_instance" "web" {
  instance_type = "t2.small"
}
```
→ 구성 파일 업데이트

**Option 3: Refresh Only**
```bash
terraform apply -refresh-only
```
→ State만 업데이트

---

## 7. terraform import

### 목적

기존 인프라를 Terraform State에 가져오기

### 사용법

**1. 리소스 블록 작성:**
```hcl
resource "aws_instance" "imported" {
}
```

**2. Import 실행:**
```bash
terraform import aws_instance.imported i-1234567890abcdef0
```

**3. State 확인:**
```bash
terraform state show aws_instance.imported
```

**4. 구성 파일 업데이트:**
```hcl
resource "aws_instance" "imported" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```

**5. Plan 검증:**
```bash
terraform plan
```

---

## 8. State 보안

### 민감 정보 보호

**State 파일에 포함될 수 있는 정보:**
- 데이터베이스 비밀번호
- API 키
- Private 키

**보호 방법:**

**1. Remote Backend + Encryption:**
```hcl
terraform {
  backend "s3" {
    encrypt = true
  }
}
```

**2. 접근 제어:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-state/*",
    "Condition": {
      "StringEquals": {
        "aws:username": ["alice", "bob"]
      }
    }
  }]
}
```

**3. .gitignore:**
```
*.tfstate
*.tfstate.*
*.tfstate.backup
```

---

## 9. 실전 시나리오

### 시나리오 1: Local → Remote 마이그레이션

```hcl
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
```

```bash
terraform init -migrate-state
```

### 시나리오 2: 리소스 이름 변경

```bash
terraform state mv aws_instance.old aws_instance.new
```

### 시나리오 3: Import

```bash
terraform import aws_instance.web i-1234567890abcdef0
```

---

## 핵심 요약

**State 역할:**
- ✅ 리소스 매핑
- ✅ 메타데이터 저장
- ✅ 성능 최적화
- ✅ 협업 지원

**Best Practices:**
- ✅ Remote Backend 사용
- ✅ State Locking 활성화
- ✅ 암호화 적용
- ✅ 정기 백업
- ✅ .gitignore 설정

---

## 참고 자료

- [State](https://developer.hashicorp.com/terraform/language/state)
- [Backends](https://developer.hashicorp.com/terraform/language/settings/backends)
- [Import](https://developer.hashicorp.com/terraform/cli/commands/import)
