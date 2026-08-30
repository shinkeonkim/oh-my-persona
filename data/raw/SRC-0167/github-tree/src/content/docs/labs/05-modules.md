---
title: Lab 05. Child Module 만들기 / Build a Module
description: Extract a reusable child module and test its input, output, provider, and scope boundaries.
---

| Level | Time | Objectives |
|---|---:|---|
| Intermediate | 60-90 min | 5a-5c |

**Read first:** [Modules](/domains/05-modules/), [Variables and outputs](/labs/02-variables-outputs/)

## Outcome

Root module의 resource를 local child module로 추출합니다. Directory 분리는 목적이 아니라 input/output contract와 scope boundary를 만드는 수단입니다.

## Build the contract

```text
.
├── main.tf
├── outputs.tf
├── variables.tf
└── modules/
    └── storage/
        ├── main.tf
        ├── outputs.tf
        └── variables.tf
```

1. Child module이 받아야 하는 값만 variable로 선언합니다.
2. Caller가 사용해야 하는 attribute만 output으로 노출합니다.
3. Child module에는 provider **requirement**를 선언하되 credential이나 region 같은 root configuration을 하드코딩하지 않습니다.
4. Root module에서 `source = "./modules/storage"`로 호출합니다.

## Complete no-cost module

Storage cloud resource 대신 `terraform_data`를 사용해 module contract와 address에 집중합니다.

```hcl title="modules/service/variables.tf"
variable "name" {
  type        = string
  description = "Stable service name."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]+$", var.name))
    error_message = "name must start with a letter and contain lowercase letters, digits, or hyphens."
  }
}

variable "port" {
  type        = number
  description = "Service listening port."

  validation {
    condition     = var.port >= 1 && var.port <= 65535
    error_message = "port must be between 1 and 65535."
  }
}
```

```hcl title="modules/service/main.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}

resource "terraform_data" "this" {
  input = {
    name = var.name
    port = var.port
  }
}
```

```hcl title="modules/service/outputs.tf"
output "id" {
  description = "Identifier consumed by the root module."
  value       = terraform_data.this.id
}

output "endpoint" {
  description = "Composed endpoint contract."
  value       = "${terraform_data.this.output.name}:${terraform_data.this.output.port}"
}
```

```hcl title="main.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}

module "catalog" {
  source = "./modules/service"
  name   = "catalog"
  port   = 8080
}

resource "terraform_data" "consumer" {
  input = {
    upstream_id       = module.catalog.id
    upstream_endpoint = module.catalog.endpoint
  }
}
```

```hcl title="outputs.tf"
output "catalog_endpoint" {
  value = module.catalog.endpoint
}
```

Root module의 reference는 child output만 사용합니다. `module.catalog.terraform_data.this.id`처럼 child implementation에 들어갈 수 없습니다.

```bash
terraform init
terraform validate
terraform plan
```

Local module source를 추가하거나 바꾼 뒤 `init`이 필요한 이유를 확인합니다.

Expected plan addresses:

```text
module.catalog.terraform_data.this
terraform_data.consumer
```

`terraform_data.consumer`가 module output을 참조하므로 explicit `depends_on` 없이도 child instance 뒤에 평가됩니다.

```bash
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform state list
terraform output catalog_endpoint
```

Representative output은 `catalog:8080`입니다. Generated ID 자체는 실행마다 달라질 수 있으므로 외우지 않습니다.

## Failure tests

- Required input을 제거해 caller contract error를 확인합니다.
- Wrong type을 전달해 type constraint error를 확인합니다.
- Child resource를 root에서 직접 참조하려 하지 말고 output이 필요한 이유를 설명합니다.
- Provider alias가 필요한 시나리오라면 module call의 `providers` map으로 명시적으로 전달합니다.

추가 failure test를 수행합니다.

1. `port = "8080"`을 전달해 type conversion 또는 type diagnostic을 확인하고 number로 복구합니다.
2. `name = "Catalog Service"`로 validation failure를 확인합니다.
3. Child output `endpoint`를 임시 제거해 root reference diagnostic을 확인합니다.
4. Module directory를 `modules/application`으로 옮기고 source만 바꾼 뒤 `init`이 필요한지 확인합니다. Resource address를 바꾸지 않았다면 local package source와 state address 문제를 구분합니다.

## Provider-aware extension

Cloud module에서는 child `terraform` block에 `required_providers`를 선언하되 root가 provider configuration과 credential을 소유합니다.

```hcl
# child requirement
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

Child가 aliased provider를 요구하면 `configuration_aliases`와 root module call의 `providers` map을 함께 사용합니다. Credential이나 fixed region을 child에 넣지 않습니다.

## Checkpoints and troubleshooting

- Root와 child variable은 이름이 같아도 자동 공유되지 않습니다.
- Module output은 public interface이고 local/resource는 implementation detail입니다.
- Local source는 same repository commit으로 versioned됩니다.
- Source 변경 뒤 `init`을 다시 실행합니다.
- Module path refactoring으로 state address가 바뀌면 `moved` block을 검토합니다.

`Module not installed`이면 `terraform init`을 실행했는지 확인합니다. `Unsupported argument`는 caller argument와 child variable 이름을 비교합니다. `Unsupported attribute`는 child output 존재 여부를 확인합니다. Module dependency cycle이 발생하면 root composition에서 양방향 output/input 연결을 만들지 않았는지 확인합니다.

## Verification and cleanup

- Plan의 address가 `module.storage.<TYPE>.<NAME>` 형태인지 확인합니다.
- Root variable과 child variable은 이름이 같아도 자동 공유되지 않습니다.
- Apply했다면 module resource를 포함한 destroy plan을 review한 뒤 cleanup합니다.

```bash
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
terraform state list
rm -f tfplan destroy.tfplan
```

완료 기준은 module address, input/output boundary, implicit dependency를 각각 실제 plan에서 찾아 설명하는 것입니다.

**Detailed walkthrough:** [Historical Lab 05](/archive/labs/lab-05-first-module/readme/)  
**Next:** [Lab 06 Remote state](/labs/06-remote-state/) · [Lab 11 Registry modules](/labs/11-registry-modules/)
