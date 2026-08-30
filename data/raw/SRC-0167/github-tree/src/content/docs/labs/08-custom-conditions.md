---
title: Lab 08. Custom Conditions
description: Trigger and compare input validation, preconditions, postconditions, and non-blocking check assertions.
---

| Level | Time | Objectives |
|---|---:|---|
| Advanced | 45-60 min | 4g |

**Read first:** [Validation layers](/domains/04-configuration/#4g-validation-layers)

## Outcome

같은 invariant를 아무 위치에나 복제하지 않고 **가장 이른 올바른 phase**에서 검증합니다. 각 failure가 plan/apply를 중단하는지 또는 warning을 남기는지 비교합니다.

## Complete condition laboratory

```text
lab-08/
├── versions.tf
├── variables.tf
├── main.tf
└── outputs.tf
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="variables.tf"
variable "environment" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment must be dev, stage, or prod."
  }
}

variable "replicas" {
  type    = number
  default = 2

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 5
    error_message = "replicas must be between 1 and 5."
  }
}
```

```hcl title="main.tf"
resource "terraform_data" "deployment" {
  input = {
    environment = var.environment
    replicas    = var.replicas
  }

  lifecycle {
    precondition {
      condition     = var.environment != "prod" || var.replicas >= 2
      error_message = "prod requires at least two replicas."
    }

    postcondition {
      condition     = self.output.replicas == var.replicas
      error_message = "provider result must preserve the requested replica count."
    }
  }
}

check "production_shape" {
  assert {
    condition     = var.environment != "prod" || terraform_data.deployment.output.replicas >= 3
    error_message = "Recommended production shape is at least three replicas."
  }
}
```

```hcl title="outputs.tf"
output "deployment" {
  value = terraform_data.deployment.output

  precondition {
    condition     = terraform_data.deployment.output.environment != ""
    error_message = "deployment environment must not be empty."
  }
}
```

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
```

Default `dev/2`는 variable validation, resource pre/postcondition, check를 모두 통과해야 합니다.

## Build four tests

1. Variable `validation`: environment input이 allowlist에 있는지 확인합니다.
2. Resource `precondition`: operation 전에 region 또는 combined input assumption을 확인합니다.
3. Resource/data `postcondition`: provider가 읽거나 만든 결과의 attribute를 확인합니다.
4. `check` block: deployed system의 지속적 assertion을 평가합니다.

## Failure sequence

한 번에 하나만 바꿔 failure phase를 기록합니다.

### 1. Input validation

```bash
terraform plan -var='environment=qa'
terraform plan -var='replicas=0'
```

Resource graph operation 전에 input contract가 실패해야 합니다. Environment allowlist는 다른 resource 상태와 무관하므로 variable validation이 가장 이른 올바른 위치입니다.

### 2. Preconditions

```bash
terraform plan -var='environment=prod' -var='replicas=1'
```

각 variable은 자체 범위를 만족하지만 두 값을 조합한 production invariant가 실패합니다. 그래서 variable 하나의 validation보다 resource precondition이 적합합니다.

### 3. Check warning

```bash
terraform plan -var='environment=prod' -var='replicas=2'
```

Precondition은 통과하지만 recommended shape check는 warning을 보고합니다. Plan이 check 때문에 precondition처럼 강제 중단되지 않는 차이를 확인합니다. Security enforcement를 `check`에만 맡기지 않습니다.

### 4. Postcondition

현재 `terraform_data`는 input을 output으로 보존하므로 postcondition이 통과합니다. Deliberate failure를 위해 condition을 잠시 `self.output.replicas == var.replicas + 1`로 바꾸고 plan/apply diagnostic을 확인한 뒤 즉시 원래대로 복구합니다. 실제 provider data source에서는 API가 반환한 architecture, status, account ID 같은 observed result를 검증할 때 사용합니다.

```bash
terraform init
terraform validate
terraform plan
```

각 condition을 한 번씩 실패시키고 다음을 기록합니다.

| Mechanism | Earliest available data | Expected failure behavior |
|---|---|---|
| Variable validation | Input value | Rejects invalid input |
| Precondition | Configuration plus earlier values | Blocks the affected operation |
| Postcondition | Read/applied result | Blocks dependent progress and reports failure |
| Check assertion | Operational result | Reports warning without blocking like pre/postconditions |

## Unknown value와 evaluation timing

Condition은 해당 phase에서 사용할 수 있는 값으로 작성합니다. Apply 뒤에만 알려지는 remote ID를 variable validation에서 검사할 수 없습니다. Precondition도 dependent resource의 unknown value를 포함하면 plan에서 evaluation이 연기될 수 있습니다. “모든 것을 가장 일찍 검사”가 아니라 **필요한 데이터가 준비된 가장 이른 phase**를 선택합니다.

Error message는 boolean expression을 그대로 반복하지 말고 다음을 포함합니다.

- 실패한 contract의 의미
- 허용 범위 또는 expected state
- caller가 수정할 input/configuration

Secret value 자체를 error message에 interpolation하지 않습니다.

## Troubleshooting

| 증상 | 원인 | 수정 |
|---|---|---|
| condition must return bool | string/number expression | comparison 또는 boolean function 사용 |
| invalid reference in validation | 다른 variable/resource 참조 위치 오류 | contract를 precondition으로 이동 검토 |
| known after apply | observed result가 아직 unknown | postcondition/check phase 사용 |
| check warning인데 run 계속 | check의 non-blocking semantics | policy 또는 precondition 필요 여부 판단 |

## Apply and cleanup

```bash
terraform apply -var='environment=prod' -var='replicas=3' -auto-approve
terraform output deployment
terraform plan
terraform destroy -auto-approve
terraform state list
```

완료 기준은 네 condition type의 available data와 failure behavior를 표 없이 설명하고, 같은 invariant를 여러 위치에 중복하지 않는 것입니다.

## Quality criteria

- Error message는 실패한 값, 기대 조건, 수정 방향을 설명합니다.
- Condition expression은 bool을 반환합니다.
- Unknown value 때문에 올바른 phase보다 너무 이른 검증을 강제하지 않습니다.
- `check`를 security enforcement로 오해하지 않습니다.

**Detailed walkthrough:** [Historical Lab 08](/archive/labs/lab-08-custom-conditions/readme/)  
**Next:** [Lab 09 Dynamic blocks](/labs/09-dynamic-blocks/) · [Configuration questions](/archive/practice-exams/domain-4-configuration/)
