---
title: Lab 02. 변수와 출력 / Variables and Outputs
description: Build and test a typed module interface using input variables, locals, conditional resources, and outputs.
---

| Level | Time | Objectives |
|---|---:|---|
| Beginner | 40-55 min | 4c-4e |

**Read first:** [Configuration 4c-4e](/domains/04-configuration/#4c-4e-values-types-expressions)

## Outcome

S3 configuration의 hard-coded value를 typed input으로 바꾸고 output을 통해 선택한 결과만 노출합니다. Variable source, type conversion, conditional `count`, output dependency를 관찰합니다.

## Prepare and predict

1. [Lab 02 downloads](/guide/labs-and-practice/#lab-02)을 disposable directory에 저장합니다.
2. `terraform.tfvars.example`을 `terraform.tfvars`로 복사하고 unique prefix를 설정합니다.
3. `enable_versioning = false`와 `true`에서 resource address가 어떻게 달라질지 예상합니다.

## Zero-cost complete configuration

Variable, local, conditional instance, output만 집중하도록 cloud credential이 필요 없는 built-in `terraform_data` resource로 먼저 실습합니다.

```text
lab-02/
├── versions.tf
├── variables.tf
├── main.tf
├── outputs.tf
└── terraform.tfvars.example
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="variables.tf"
variable "environment" {
  type        = string
  description = "Deployment environment label."
  default     = "dev"

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment must be dev, stage, or prod."
  }
}

variable "service" {
  type = object({
    name    = string
    port    = number
    enabled = optional(bool, true)
  })

  validation {
    condition     = var.service.port >= 1 && var.service.port <= 65535
    error_message = "service.port must be between 1 and 65535."
  }
}

variable "create_audit_record" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
```

```hcl title="main.tf"
locals {
  common_tags = merge(var.tags, {
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}

resource "terraform_data" "service" {
  input = {
    name = var.service.name
    port = var.service.port
    tags = local.common_tags
  }
}

resource "terraform_data" "audit" {
  count = var.create_audit_record ? 1 : 0

  input = "${var.environment}:${var.service.name}"
}
```

```hcl title="outputs.tf"
output "service_contract" {
  description = "Selected values exposed to a caller."
  value = {
    id   = terraform_data.service.id
    name = terraform_data.service.output.name
    port = terraform_data.service.output.port
  }
}

output "audit_id" {
  description = "Null when the conditional instance is disabled."
  value       = try(terraform_data.audit[0].id, null)
}
```

```hcl title="terraform.tfvars.example"
environment = "dev"
service = {
  name = "catalog"
  port = 8080
}
create_audit_record = false
tags = {
  Owner = "study"
}
```

Example을 복사하되 real secret은 tfvars에 넣지 않습니다.

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan -out=disabled.tfplan
```

예상 plan은 `terraform_data.service` 한 개 create이고 `terraform_data.audit[0]`은 없어야 합니다. `audit_id`는 conditional instance가 없으므로 null입니다.

## Execute

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=without-versioning.tfplan
terraform show without-versioning.tfplan
```

다음 순서로 실험합니다.

1. Wrong type 또는 허용되지 않은 environment를 넣어 validation failure를 확인합니다.
2. 올바른 값으로 plan을 다시 생성합니다.
3. `enable_versioning`을 바꾸고 `aws_s3_bucket_versioning.versioning[0]` address의 생성 여부를 비교합니다.
4. `tags` map이 `merge()` 결과에 어떻게 반영되는지 console 또는 plan에서 확인합니다.

다음 deliberate failures를 순서대로 수행합니다.

```bash
# terraform.tfvars에서 environment를 qa로 변경
terraform plan

# service.port를 70000으로 변경
terraform plan
```

첫 실패는 environment validation, 두 번째는 port validation의 error message를 보여야 합니다. 두 값을 복구한 뒤 console에서 transformation을 확인합니다.

```bash
terraform console
> local.common_tags
> var.service.enabled
> var.create_audit_record ? 1 : 0
```

이제 `create_audit_record = true`로 바꾸고 plan을 생성합니다. Expected address는 `terraform_data.audit[0]`입니다. Apply한 뒤 false로 되돌리면 그 instance만 destroy proposal이 나타나야 합니다.

```bash
terraform plan -out=enabled.tfplan
terraform apply enabled.tfplan
terraform output
terraform output -json
terraform state list
```

## Checkpoints and diagnosis

- `var.service`는 object contract이며 `local.common_tags`는 내부 계산값입니다.
- Optional attribute를 생략하면 `enabled`는 true입니다.
- Output은 resource object 전체가 아니라 caller가 필요한 stable contract만 노출합니다.
- `try(..., null)`은 conditional instance가 없을 때 output shape를 유지합니다.
- Wrong type error는 provider 호출 전 configuration evaluation에서 발생합니다.

`Variables not allowed`가 backend block에서 발생하면 variable을 쓸 수 없는 초기화 phase를 혼동한 것입니다. `Unsupported attribute`는 object type에 없는 key를 참조했는지 확인합니다. `Invalid index`는 `count = 0`인 instance `[0]`을 직접 읽었는지 확인합니다.

## Verify and cleanup

```bash
terraform output
terraform output -json
terraform state list
terraform destroy
```

- Output은 resource 전체가 아니라 caller에게 필요한 contract만 노출해야 합니다.
- Sensitive output 표시는 저장 방지와 다르다는 점을 [1.12 deep dive](/reference/terraform-1-12-deep-dive/#sensitive-ephemeral-and-write-only)에서 확인합니다.

```bash
terraform destroy -auto-approve
terraform state list
rm -f disabled.tfplan enabled.tfplan terraform.tfstate.backup
```

완료 기준은 state가 비고, variable validation 두 종류를 재현했으며, false/true에 따른 instance address 차이와 output contract를 설명하는 것입니다. AWS download variant를 사용했다면 S3 versioning resource까지 destroy plan에 포함됐는지 별도로 확인합니다.

**Detailed walkthrough:** [Historical Lab 02](/archive/labs/lab-02-variables-outputs/readme/)  
**Next:** [Lab 03 Data sources](/labs/03-data-sources/) · [Configuration questions](/archive/practice-exams/domain-4-configuration/)
