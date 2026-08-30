---
title: Lab 09. Dynamic Blocks
description: Generate repeatable nested blocks from typed collections without confusing blocks with ordinary values.
---

| Level | Time | Objectives |
|---|---:|---|
| Advanced | 40-60 min | 4d-4e |

**Read first:** [Types and expressions](/domains/04-configuration/#4c-4e-values-types-expressions), [Lab 04](/labs/04-count-for-each/)

## Outcome

Typed collection에서 provider resource의 repeatable nested block을 생성합니다. `dynamic`은 resource instance를 반복하는 `for_each`와 목적이 다릅니다.

## Model the input

```hcl
variable "ingress_rules" {
  type = map(object({
    port        = number
    description = string
    cidrs       = set(string)
  }))
}
```

Map key를 stable rule identity로 사용하고 validation으로 port range와 empty CIDR을 검사합니다.

## Complete plan-first configuration

Dynamic block은 provider가 repeatable nested block을 정의할 때 의미가 있으므로 AWS security group schema를 사용합니다. Security group 자체에는 hourly charge가 없지만 account/network 변경 권한이 필요합니다. 학습만 필요하면 `plan`까지 실행하고 apply하지 않습니다.

```text
lab-09/
├── versions.tf
├── variables.tf
├── main.tf
└── terraform.tfvars.example
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
  type    = string
  default = "ap-northeast-2"
}

variable "vpc_id" {
  type        = string
  description = "Disposable VPC that will contain the lab security group."
}

variable "ingress_rules" {
  type = map(object({
    port        = number
    description = string
    cidrs       = set(string)
  }))

  validation {
    condition = alltrue([
      for rule in values(var.ingress_rules) :
      rule.port >= 1 && rule.port <= 65535 && length(rule.cidrs) > 0
    ])
    error_message = "Every rule needs a valid port and at least one CIDR."
  }
}
```

```hcl title="main.tf"
resource "aws_security_group" "lab" {
  name_prefix = "tf004-lab09-"
  description = "Terraform Associate 004 dynamic block lab"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    iterator = rule

    content {
      description = "${rule.key}: ${rule.value.description}"
      from_port   = rule.value.port
      to_port     = rule.value.port
      protocol    = "tcp"
      cidr_blocks = sort(tolist(rule.value.cidrs))
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Purpose = "terraform-associate-004-lab-09"
  }
}
```

```hcl title="terraform.tfvars.example"
vpc_id = "vpc-REPLACE_ME"
ingress_rules = {
  https = {
    port        = 443
    description = "TLS endpoint"
    cidrs       = ["10.0.0.0/8"]
  }
  metrics = {
    port        = 9090
    description = "Internal metrics"
    cidrs       = ["10.20.0.0/16"]
  }
}
```

Disposable VPC와 restrictive private CIDR를 사용합니다. 편의를 위해 ingress를 `0.0.0.0/0`으로 열지 않습니다.

## Generate nested blocks

```hcl
dynamic "ingress" {
  for_each = var.ingress_rules
  content {
    from_port   = ingress.value.port
    to_port     = ingress.value.port
    protocol    = "tcp"
    cidr_blocks = sort(tolist(ingress.value.cidrs))
    description = ingress.value.description
  }
}
```

`terraform console`에서 input transformation을 먼저 확인한 뒤 plan을 생성합니다. Rule 하나를 추가·제거하고 nested block diff를 비교합니다.

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform console
```

Console에서 `keys(var.ingress_rules)`, `{ for key, rule in var.ingress_rules : key => rule.port }`, `[for rule in values(var.ingress_rules) : rule.port]`를 평가합니다. 그 후 plan을 생성합니다.

```bash
terraform plan -out=tfplan
terraform show tfplan
```

Expected observation은 security group resource 하나 안에 ingress nested block 두 개가 나타나는 것입니다. State address는 `aws_security_group.lab` 하나이며 `ingress["https"]` 같은 별도 resource instance address가 생기지 않습니다. 이것이 resource `for_each`와 dynamic block의 핵심 차이입니다.

## Change experiments

1. `metrics` rule을 제거하고 nested block removal을 확인합니다.
2. `admin` key를 추가하되 private CIDR와 port 22를 사용해 block addition을 확인합니다.
3. `cidrs` 순서를 바꿉니다. Set과 `sort(tolist(...))` 때문에 의미 없는 ordering diff가 줄어드는지 확인합니다.
4. Port를 70000으로 바꿔 provider call 전에 variable validation이 실패하는지 확인합니다.

`iterator = rule`을 생략하면 iterator name은 block label `ingress`입니다. Nested dynamic block이 겹치면 명시적 iterator가 readability를 높입니다.

## What dynamic cannot do

Dynamic block은 provider schema의 repeatable nested block만 생성합니다. `lifecycle`, `provider`, `depends_on` 같은 meta-argument block은 Terraform이 graph를 만들기 전에 처리해야 하므로 dynamic으로 생성할 수 없습니다. Ordinary argument list/map을 만들 때는 `for` expression을 사용합니다.

## Troubleshooting

| 증상 | 원인 | 수정 |
|---|---|---|
| unsupported block type | provider schema에 nested block 없음 | Registry resource schema 확인 |
| unsuitable `for_each` value | collection type/unknown key | map 또는 known collection 사용 |
| invalid CIDR/port | input/provider validation | value와 error message 확인 |
| perpetual ordering diff | list/set ordering 불안정 | stable key와 sorted value 사용 |

Dynamic abstraction으로 caller가 provider schema 전체를 그대로 넘기게 되면 module contract가 더 어려워집니다. 반복 수가 작고 고정이면 explicit block이 더 읽기 좋습니다.

## Verification

- Ordinary argument에는 `for` expression을 사용합니다.
- Repeatable nested block에만 `dynamic` block을 사용합니다.
- Provider가 요구하는 block label과 schema를 registry documentation에서 확인합니다.
- 과도한 dynamic abstraction이 module interface를 읽기 어렵게 만들면 explicit block을 선택합니다.

Security group 같은 cloud resource를 apply했다면 rule과 resource가 모두 destroy됐는지 확인합니다.

```bash
# Apply를 선택한 경우만
terraform apply tfplan
terraform state list
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
terraform state list
rm -f tfplan destroy.tfplan
```

완료 기준은 `for` expression, resource `for_each`, dynamic `for_each`가 각각 value, resource instances, nested blocks 중 무엇을 만드는지 설명하는 것입니다.

**Detailed walkthrough:** [Historical Lab 09](/archive/labs/lab-09-dynamic-blocks/readme/)  
**Next:** [Lab 10 State operations](/labs/10-state-operations/) · [Official dynamic blocks](https://developer.hashicorp.com/terraform/language/v1.12.x/expressions/dynamic-blocks)
