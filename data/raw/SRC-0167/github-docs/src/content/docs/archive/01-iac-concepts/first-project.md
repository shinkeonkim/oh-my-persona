---
title: "첫 번째 Terraform 프로젝트"
description: "Legacy study material imported from 01-iac-concepts/first-project.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Terraform 프로젝트 구조 이해
- Core Workflow (init → plan → apply → destroy) 실습
- Plan 출력 해석 방법 익히기
- State 파일 첫 접촉
- 자주 발생하는 오류 해결

---

## 1. 사전 준비

### 1.1 필수 도구 확인

```bash
terraform version
# Terraform v1.12.0

aws --version
# aws-cli/2.15.0 ...

aws sts get-caller-identity
# {
#   "UserId": "AIDA...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

⚠️ 도구 설치 미완료 시 [설치 가이드](/archive/01-iac-concepts/installation/) 참고.

### 1.2 프로젝트 디렉토리 생성

```bash
mkdir -p ~/terraform-first-project
cd ~/terraform-first-project
```

---

## 2. Hello World: S3 Bucket 프로젝트

### 2.1 파일 구조

```
terraform-first-project/
├── main.tf          # 리소스 정의
├── variables.tf     # (선택) 변수
├── outputs.tf       # (선택) 출력
└── terraform.tfvars # (선택) 변수 값
```

### 2.2 main.tf 작성

```hcl
terraform {
  required_version = ">= 1.12.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "hello" {
  bucket = "terraform-hello-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "First Terraform Bucket"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}
```

### 2.3 outputs.tf 작성

```hcl
output "bucket_name" {
  description = "S3 Bucket 이름"
  value       = aws_s3_bucket.hello.id
}

output "bucket_arn" {
  description = "S3 Bucket ARN"
  value       = aws_s3_bucket.hello.arn
}

output "bucket_region" {
  description = "S3 Bucket 지역"
  value       = aws_s3_bucket.hello.region
}
```

---

## 3. terraform init - 초기화

### 실행

```bash
terraform init
```

### 예상 출력

```
Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Finding hashicorp/random versions matching "~> 3.5"...
- Installing hashicorp/aws v5.31.0...
- Installed hashicorp/aws v5.31.0 (signed by HashiCorp)
- Installing hashicorp/random v3.5.1...
- Installed hashicorp/random v3.5.1 (signed by HashiCorp)

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.
```

### 생성된 파일

```bash
ls -la
```

**결과:**
```
.terraform/                    # Provider 바이너리
.terraform.lock.hcl            # Dependency lock file
main.tf
outputs.tf
```

### .terraform 디렉토리

```bash
tree .terraform
# .terraform/
# └── providers/
#     └── registry.terraform.io/
#         └── hashicorp/
#             ├── aws/
#             │   └── 5.31.0/
#             └── random/
#                 └── 3.5.1/
```

### .terraform.lock.hcl

```hcl
provider "registry.terraform.io/hashicorp/aws" {
  version     = "5.31.0"
  constraints = "~> 5.0"
  hashes = [
    "h1:...",
    "zh:...",
  ]
}
```

⚠️ 이 파일은 **Git 에 커밋** 하세요. 팀 전체가 동일 버전 사용.

---

## 4. terraform validate - 검증

```bash
terraform validate
```

**성공:**
```
Success! The configuration is valid.
```

**실패 예시:**
```
Error: Unsupported argument

  on main.tf line 20, in resource "aws_s3_bucket" "hello":
  20:   invalid_arg = "value"

An argument named "invalid_arg" is not expected here.
```

---

## 5. terraform fmt - 포맷팅

```bash
terraform fmt
# main.tf     (변경된 파일만 출력)

terraform fmt -recursive     # 하위 디렉토리 포함
terraform fmt -check         # 변경 없이 확인만 (CI/CD)
terraform fmt -diff          # 차이 표시
```

---

## 6. terraform plan - 실행 계획

### 실행

```bash
terraform plan
```

### 출력 분석

```
Terraform used the selected providers to generate the following execution plan.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_s3_bucket.hello will be created
  + resource "aws_s3_bucket" "hello" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = (known after apply)
      + bucket_domain_name          = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags                        = {
          + "Environment" = "Learning"
          + "ManagedBy"   = "Terraform"
          + "Name"        = "First Terraform Bucket"
        }
      + tags_all                    = {
          + "Environment" = "Learning"
          + "ManagedBy"   = "Terraform"
          + "Name"        = "First Terraform Bucket"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)
    }

  # random_id.bucket_suffix will be created
  + resource "random_id" "bucket_suffix" {
      + b64_std     = (known after apply)
      + b64_url     = (known after apply)
      + byte_length = 4
      + dec         = (known after apply)
      + hex         = (known after apply)
      + id          = (known after apply)
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + bucket_arn    = (known after apply)
  + bucket_name   = (known after apply)
  + bucket_region = (known after apply)
```

### Plan 기호 이해

| 기호 | 의미 |
|------|------|
| `+` | 리소스 생성 |
| `~` | 리소스 수정 (in-place) |
| `-` | 리소스 삭제 |
| `-/+` | 재생성 (삭제 후 생성) |
| `+/-` | 재생성 (생성 후 삭제, create_before_destroy) |
| `<=` | Data Source 읽기 |

### Plan 파일로 저장

```bash
terraform plan -out=tfplan
# 저장된 plan 을 나중에 apply 가능
```

---

## 7. terraform apply - 실행

### 실행

```bash
terraform apply
```

### 대화형 승인

```
Plan: 2 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

### 완료

```
random_id.bucket_suffix: Creating...
random_id.bucket_suffix: Creation complete after 0s [id=abc123]
aws_s3_bucket.hello: Creating...
aws_s3_bucket.hello: Creation complete after 3s [id=terraform-hello-a1b2c3d4]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:

bucket_arn = "arn:aws:s3:::terraform-hello-a1b2c3d4"
bucket_name = "terraform-hello-a1b2c3d4"
bucket_region = "us-east-1"
```

### 자동 승인 (CI/CD)

```bash
terraform apply -auto-approve
```

### Plan 파일 사용

```bash
terraform apply tfplan
```

---

## 8. State 파일 확인

```bash
ls -la terraform.tfstate

cat terraform.tfstate | jq .
```

**주요 내용:**
```json
{
  "version": 4,
  "terraform_version": "1.12.0",
  "serial": 1,
  "lineage": "abc-123-...",
  "outputs": {
    "bucket_name": {
      "value": "terraform-hello-a1b2c3d4",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "hello",
      "instances": [{
        "attributes": {
          "id": "terraform-hello-a1b2c3d4",
          "arn": "arn:aws:s3:::terraform-hello-a1b2c3d4"
        }
      }]
    }
  ]
}
```

⚠️ **절대 이 파일을 수동 편집하지 마세요!**

---

## 9. AWS Console 에서 확인

```bash
aws s3 ls
# 2026-07-21 10:00:00 terraform-hello-a1b2c3d4

aws s3api get-bucket-tagging --bucket terraform-hello-a1b2c3d4
```

---

## 10. terraform output 확인

```bash
terraform output
# bucket_arn = "arn:aws:s3:::terraform-hello-a1b2c3d4"
# bucket_name = "terraform-hello-a1b2c3d4"
# bucket_region = "us-east-1"

terraform output bucket_name
# "terraform-hello-a1b2c3d4"

terraform output -raw bucket_name
# terraform-hello-a1b2c3d4

terraform output -json
```

---

## 11. 리소스 수정 실습

### 태그 추가

**main.tf 수정:**
```hcl
resource "aws_s3_bucket" "hello" {
  bucket = "terraform-hello-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "First Terraform Bucket"
    Environment = "Learning"
    ManagedBy   = "Terraform"
    Owner       = "Team-DevOps"      # 추가
    CostCenter  = "Engineering"      # 추가
  }
}
```

### Plan 확인

```bash
terraform plan
```

**출력:**
```
  # aws_s3_bucket.hello will be updated in-place
  ~ resource "aws_s3_bucket" "hello" {
        id                          = "terraform-hello-a1b2c3d4"
      ~ tags                        = {
          + "CostCenter"  = "Engineering"
            "Environment" = "Learning"
            "ManagedBy"   = "Terraform"
            "Name"        = "First Terraform Bucket"
          + "Owner"       = "Team-DevOps"
        }
      ~ tags_all                    = {
          + "CostCenter"  = "Engineering"
            # ... same as tags
        }
        # (other attributes unchanged)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

`~` 기호로 **수정** 됨을 확인.

### Apply

```bash
terraform apply -auto-approve
```

---

## 12. terraform destroy - 정리

### 실행

```bash
terraform destroy
```

### 대화형 승인

```
Plan: 0 to add, 0 to change, 2 to destroy.

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes
```

### 완료

```
aws_s3_bucket.hello: Destroying... [id=terraform-hello-a1b2c3d4]
aws_s3_bucket.hello: Destruction complete after 1s
random_id.bucket_suffix: Destroying... [id=abc123]
random_id.bucket_suffix: Destruction complete after 0s

Destroy complete! Resources: 2 destroyed.
```

### 상태 확인

```bash
terraform state list
# (empty)

cat terraform.tfstate
# 리소스가 모두 제거된 State
```

---

## 13. 자주 발생하는 오류

### 오류 1: Provider 다운로드 실패

```
Error: Failed to query available provider packages
```

**해결:**
```bash
terraform init -upgrade
```

### 오류 2: AWS Credentials 없음

```
Error: No valid credential sources found
```

**해결:**
```bash
aws configure

# 또는 환경 변수
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
```

### 오류 3: S3 Bucket 이름 중복

```
Error: creating S3 Bucket: BucketAlreadyExists
```

**해결:** Bucket 이름은 전 세계 유일. `random_id` 또는 고유 접미사 사용.

### 오류 4: Region 지정 안 함

```
Error: no valid credential sources for S3 Backend found
```

**해결:**
```hcl
provider "aws" {
  region = "us-east-1"
}
```

### 오류 5: State Lock (Remote Backend)

```
Error: Error locking state: Error acquiring the state lock
```

**해결:**
```bash
terraform force-unlock <LOCK_ID>
```

---

## 14. Full Workflow 요약

```bash
terraform init         # 초기화
terraform fmt          # 포맷팅
terraform validate     # 검증
terraform plan         # 계획
terraform apply        # 실행
terraform show         # 결과 확인
terraform state list   # 리소스 목록
terraform output       # 출력값
terraform destroy      # 정리
```

---

## 15. 다음 단계

축하합니다! 첫 번째 Terraform 프로젝트를 완성했습니다.

**다음 학습:**
- [Week 3: Core Terraform Workflow](/archive/03-core-workflow/readme/)
- [CLI 명령어 상세 가이드](/archive/03-core-workflow/cli-commands/)
- [Lab 01: 첫 번째 Terraform 프로젝트 (심화)](/archive/labs/lab-01-first-project/readme/)
- [Lab 02: Variables와 Outputs](/archive/labs/lab-02-variables-outputs/readme/)

---

## 참고 자료

- [Get Started with Terraform - AWS](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
- [Terraform CLI Documentation](https://developer.hashicorp.com/terraform/cli)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
