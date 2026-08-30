---
title: "Week 3: Core Terraform Workflow"
description: "Legacy study material imported from 03-core-workflow/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Terraform CLI 명령어 완벽 이해
- 워크플로우 각 단계의 역할 파악
- State 파일의 역할과 관리
- 포맷팅 및 검증 도구 활용

---

## 1. Terraform Core Workflow

### 기본 워크플로우

```
Write → Init → Validate → Plan → Apply → Destroy
```

### 각 단계 상세

#### 1. Write (코드 작성)

**main.tf:**
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-terraform-bucket-12345"

  tags = {
    Name        = "Example Bucket"
    Environment = "Dev"
  }
}
```

#### 2. terraform init

**목적:** 작업 디렉토리 초기화

**동작:**
- Provider 플러그인 다운로드
- Backend 초기화
- Child 모듈 다운로드

**명령어:**
```bash
terraform init

terraform init -upgrade

terraform init -reconfigure
```

**예상 출력:**
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.31.0...

Terraform has been successfully initialized!
```

**생성되는 파일:**
- `.terraform/` - Provider 바이너리
- `.terraform.lock.hcl` - Dependency lock file

#### 3. terraform validate

**목적:** 구성 문법 검증

**특징:**
- Provider 다운로드 후 실행 가능
- 원격 서비스 접근 안 함 (로컬만)
- 구문 오류, 타입 오류 검출

**명령어:**
```bash
terraform validate
```

**성공:**
```
Success! The configuration is valid.
```

**실패:**
```
Error: Unsupported argument

  on main.tf line 5:
   5:   invalid_argument = "value"

An argument named "invalid_argument" is not expected here.
```

#### 4. terraform fmt

**목적:** 코드 포맷팅

**동작:**
- 들여쓰기 정리
- 속성 정렬
- 표준 형식으로 변환

**명령어:**
```bash
terraform fmt

terraform fmt -recursive

terraform fmt -check

terraform fmt -diff
```

**Before:**
```hcl
resource"aws_instance""example"{
ami="ami-12345"
instance_type="t2.micro"
tags={Name="Server"}}
```

**After:**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345"
  instance_type = "t2.micro"
  
  tags = {
    Name = "Server"
  }
}
```

#### 5. terraform plan

**목적:** 실행 계획 생성

**동작:**
1. State Refresh (기본)
2. 구성과 State 비교
3. 변경 사항 계산
4. 실행 계획 출력

**명령어:**
```bash
terraform plan

terraform plan -out=tfplan

terraform plan -refresh=false

terraform plan -target=aws_instance.web
```

**출력 기호:**
- `+` : 생성될 리소스
- `~` : 수정될 리소스
- `-` : 삭제될 리소스
- `-/+` : 재생성될 리소스 (삭제 후 생성)
- `<=` : 읽기 작업 (data source)

**예시:**
```
Terraform will perform the following actions:

  # aws_instance.web will be created
  + resource "aws_instance" "web" {
      + ami           = "ami-12345678"
      + instance_type = "t2.micro"
      + id            = (known after apply)
      + public_ip     = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

#### 6. terraform apply

**목적:** 인프라 변경 적용

**동작:**
1. Plan 생성
2. 사용자 승인 대기 (기본)
3. 변경 실행
4. State 업데이트

**명령어:**
```bash
terraform apply

terraform apply -auto-approve

terraform apply tfplan

terraform apply -target=aws_instance.web
```

**대화형 승인:**
```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

**완료:**
```
aws_instance.web: Creating...
aws_instance.web: Creation complete after 30s [id=i-1234567890abcdef0]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

#### 7. terraform destroy

**목적:** 모든 관리 리소스 삭제

**명령어:**
```bash
terraform destroy

terraform destroy -auto-approve

terraform destroy -target=aws_instance.web
```

---

## 2. State 파일 이해하기

### State란?

**terraform.tfstate:**
- 현재 인프라 상태 저장
- JSON 형식
- 민감 정보 포함 가능

### State의 역할

**1. 리소스 매핑**
```
Configuration ←→ Real Infrastructure
```

**2. 메타데이터 저장**
- 리소스 ID
- 속성 값
- 종속성 관계

**3. 성능 향상**
- API 호출 최소화
- 대규모 인프라 관리

**4. 협업**
- Remote State
- State Locking

### State 파일 예시

```json
{
  "version": 4,
  "terraform_version": "1.12.0",
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
            "public_ip": "54.123.45.67"
          }
        }
      ]
    }
  ]
}
```

### State 조작 명령어

```bash
terraform state list

terraform state show aws_instance.web

terraform state mv SOURCE DEST

terraform state rm aws_instance.old

terraform state pull

terraform state push
```

---

## 3. 워크플로우 고급

### Plan 파일 사용

```bash
terraform plan -out=tfplan

terraform show tfplan

terraform apply tfplan
```

**장점:**
- Plan과 Apply 간 일관성
- 검토 프로세스
- CI/CD 파이프라인

### Refresh

```bash
terraform apply -refresh-only
```

**Drift 감지:**
```
~ resource "aws_instance" "web" {
    ~ instance_type = "t2.small" -> "t2.micro"
  }
```

### Target 사용

```bash
terraform apply -target=aws_instance.web

terraform destroy -target=aws_s3_bucket.data
```

**주의:**
- 프로덕션에서 지양
- 종속성 고려 필요

---

## 4. 실전 예제

### 예제 1: 기본 워크플로우

```bash
terraform init

terraform validate

terraform fmt

terraform plan

terraform apply

terraform show

terraform state list

terraform destroy
```

### 예제 2: Plan 파일 활용

```bash
terraform plan -out=prod.tfplan

terraform show -json prod.tfplan | jq .

terraform apply prod.tfplan
```

### 예제 3: Drift 해결

```bash
terraform plan

terraform apply -refresh-only

terraform apply
```

---

## 5. 핵심 요약

### 명령어 정리

| 명령어 | 목적 | State 접근 | 인프라 변경 |
|--------|------|-----------|-----------|
| `init` | 초기화 | ❌ | ❌ |
| `validate` | 검증 | ❌ | ❌ |
| `fmt` | 포맷팅 | ❌ | ❌ |
| `plan` | 계획 | Read (refresh) | ❌ |
| `apply` | 적용 | Read/Write | ✅ |
| `destroy` | 삭제 | Read/Write | ✅ (삭제) |

### 워크플로우

```
1. init    - 준비
2. validate - 검증
3. fmt     - 정리
4. plan    - 계획
5. apply   - 실행
6. destroy - 정리
```

---

다음: [CLI 명령어 상세 가이드](/archive/03-core-workflow/cli-commands/)

---

## 참고 자료

- [Terraform CLI](https://developer.hashicorp.com/terraform/cli)
- [Core Workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
- [State](https://developer.hashicorp.com/terraform/language/state)
