---
title: Lab 01. 첫 프로젝트 / First Project
description: Observe provider installation, dependency locking, planning, state creation, and cleanup in the core Terraform workflow.
---

| Level | Time | Objectives |
|---|---:|---|
| Beginner | 35-50 min | 2a-2d, 3a-3g, 6a |

**Read first:** [IaC](/domains/01-iac/), [Fundamentals](/domains/02-fundamentals/), [Core workflow](/domains/03-workflow/)

## Outcome

AWS S3 bucket configuration을 사용해 `init → plan → apply → inspect → destroy`를 한 번 수행합니다. 핵심은 bucket 자체가 아니라 각 단계가 어떤 artifact를 읽고 쓰는지 설명하는 것입니다.

## Prepare

1. Disposable AWS account/profile과 globally unique bucket suffix를 준비합니다.
2. [solution files](/guide/labs-and-practice/#lab-01)을 빈 Lab directory에 저장하고 placeholder bucket name을 변경합니다.
3. `.gitignore`에 `.terraform/`, plan file, `*.tfstate*`가 포함됐는지 확인합니다.

## Execute and observe

```bash
terraform fmt -check
terraform init
terraform validate
terraform plan -out=tfplan
terraform show tfplan
```

- `init` 뒤 `.terraform.lock.hcl`에 선택된 provider version과 checksum이 생기는지 확인합니다.
- Plan에서 S3 bucket과 연결 resource 사이의 reference dependency를 찾습니다.
- 예상 action을 설명할 수 있을 때만 `terraform apply tfplan`을 실행합니다.

```bash
terraform state list
terraform state show aws_s3_bucket.my_first_bucket
terraform output
```

State address와 AWS object ID가 어떤 binding을 만드는지 기록합니다.

## 처음부터 만드는 파일 / Complete configuration

빈 directory에서 다음 네 파일을 만듭니다.

```text
lab-01/
├── versions.tf
├── variables.tf
├── main.tf
└── outputs.tf
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

```hcl title="variables.tf"
variable "aws_region" {
  type        = string
  description = "AWS region used by this disposable lab."
  default     = "ap-northeast-2"
}

variable "bucket_name" {
  type        = string
  description = "Globally unique lowercase S3 bucket name."

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "bucket_name must be a valid lowercase S3 bucket name."
  }
}
```

```hcl title="main.tf"
resource "aws_s3_bucket" "lab" {
  bucket = var.bucket_name

  tags = {
    Purpose = "terraform-associate-004-lab-01"
  }
}
```

```hcl title="outputs.tf"
output "bucket_arn" {
  description = "ARN returned by the AWS provider after apply."
  value       = aws_s3_bucket.lab.arn
}
```

Credential은 source file에 쓰지 않습니다. `AWS_PROFILE`, AWS SSO, environment credential 또는 disposable account의 standard credential chain을 사용합니다. Bucket name은 전 세계에서 unique해야 하므로 개인 suffix를 포함합니다.

```bash
export TF_VAR_bucket_name="tf004-lab01-YOUR-UNIQUE-SUFFIX"
terraform fmt -check
terraform init
```

첫 `init`의 핵심 출력은 `Installing hashicorp/aws...`, `Terraform has created a lock file .terraform.lock.hcl`, `Terraform has been successfully initialized`입니다. 실제 patch version은 실행 날짜와 constraint에 따라 달라질 수 있습니다. `.terraform/`은 local cache이고 `.terraform.lock.hcl`은 team이 검토·commit할 dependency selection입니다.

## Plan을 행동 단위로 읽기

```bash
terraform validate
terraform plan -out=tfplan
terraform show tfplan
```

Representative observation:

```text
Terraform will perform the following actions:
  # aws_s3_bucket.lab will be created
  + resource "aws_s3_bucket" "lab" { ... }

Plan: 1 to add, 0 to change, 0 to destroy.
```

정확한 ARN이나 computed attribute를 미리 외우지 않습니다. `(known after apply)`는 provider가 create/read한 뒤 알 수 있는 unknown value입니다. Plan에서 configuration address `aws_s3_bucket.lab`, action `create`, input bucket name을 확인한 뒤에만 saved plan을 적용합니다.

```bash
terraform apply tfplan
terraform state list
terraform state show aws_s3_bucket.lab
terraform output bucket_arn
terraform plan
```

Apply 뒤 `state list`에는 `aws_s3_bucket.lab`이 한 줄로 나타나야 합니다. 두 번째 normal plan은 외부 변경이 없다면 `No changes. Your infrastructure matches the configuration.`을 표시합니다. 이것이 idempotent convergence 관찰입니다.

## Deliberate experiments

1. `Purpose` tag 값을 바꾸고 plan의 in-place update 여부를 확인합니다.
2. `terraform show tfplan`과 current configuration을 비교합니다. Saved plan 생성 뒤 configuration을 바꾸면 old plan과 source가 다른 artifact임을 확인합니다.
3. `.terraform.lock.hcl`의 constraint와 selected provider version/checksum을 찾아 `versions.tf`의 범위와 구분합니다.
4. AWS Console에서 tag를 바꾼 뒤 plan을 실행해 drift가 어떻게 표시되는지 확인하고, Lab configuration으로 되돌립니다.

## Troubleshooting

| 증상 | 원인 후보 | 확인 방법 |
|---|---|---|
| `No valid credential sources found` | AWS credential chain 없음 | `aws sts get-caller-identity`, profile/SSO 확인 |
| bucket already exists | global name collision | `TF_VAR_bucket_name`에 unique suffix 사용 |
| `Inconsistent dependency lock file` | source/lock/plan 불일치 | saved plan을 버리고 `init`, 새 plan 생성 |
| destroy access denied | IAM permission 부족 또는 bucket 상태 | object가 비었는지와 delete permission 확인 |

실패했다고 state를 삭제하지 않습니다. Configuration, state, remote object가 어떤 단계까지 생성됐는지 `state list`와 plan으로 먼저 확인합니다.

## Success and cleanup

- 두 번째 normal plan이 예상한 변경 없음 또는 설명 가능한 drift만 표시합니다.
- `terraform destroy` 후 AWS console과 `terraform state list`를 모두 확인합니다.
- Saved plan과 local state를 공유 repository에 남기지 않습니다.

Cleanup은 apply와 같은 수준으로 review합니다.

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
terraform state list
rm -f tfplan destroy.tfplan
unset TF_VAR_bucket_name
```

예상 결과는 `Plan: 0 to add, 0 to change, 1 to destroy`이며 최종 `state list`는 비어 있어야 합니다. AWS Console 확인은 보조 수단이고 Terraform 관점의 완료 조건은 destroy apply와 empty state입니다.

## Explain before moving on

1. Provider constraint와 lock selection은 어떻게 다른가?
2. Plan file을 apply에 전달하면 무엇을 다시 계산하지 않는가?
3. State가 없으면 Terraform은 기존 bucket과 resource address의 관계를 어떻게 아는가?

**Detailed walkthrough:** [Historical Lab 01](/archive/labs/lab-01-first-project/readme/)  
**Next:** [Lab 02 Variables and outputs](/labs/02-variables-outputs/) · [Command matrix](/reference/command-behavior-matrix/)
