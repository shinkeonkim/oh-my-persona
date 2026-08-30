---
title: Lab 07. Lifecycle 판단 / Lifecycle Decisions
description: Compare replacement ordering, destroy protection, and drift ownership using lifecycle meta-arguments.
---

| Level | Time | Objectives |
|---|---:|---|
| Intermediate | 45-65 min | 4f |

**Read first:** [Dependencies and lifecycle](/domains/04-configuration/#4f-dependencies), [State model](/domains/06-state/)

## Outcome

`create_before_destroy`, `prevent_destroy`, `ignore_changes`가 해결하는 서로 다른 문제를 plan으로 비교합니다. Lifecycle은 모든 change를 안전하게 만드는 장식이 아니라 ownership과 replacement decision입니다.

## Complete no-cost harness

`terraform_data.triggers_replace`는 값이 바뀔 때 replacement를 계획하므로 lifecycle action order를 cloud 비용 없이 관찰할 수 있습니다.

```text
lab-07/
├── versions.tf
├── variables.tf
└── main.tf
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="variables.tf"
variable "release" {
  type    = string
  default = "v1"
}

variable "external_note" {
  type    = string
  default = "owned-by-terraform"
}
```

```hcl title="main.tf"
resource "terraform_data" "application" {
  input            = var.external_note
  triggers_replace = [var.release]

  lifecycle {
    create_before_destroy = true
  }
}

output "application" {
  value = {
    id      = terraform_data.application.id
    release = var.release
    note    = terraform_data.application.output
  }
}
```

```bash
terraform init
terraform apply -auto-approve
terraform state show terraform_data.application
```

`release = "v2"`로 바꾸고 plan을 생성합니다. Expected action은 replacement이며 `create_before_destroy` 때문에 `+/-` ordering으로 새 instance create 뒤 old destroy가 제안됩니다. Provider resource에서는 old/new가 동시에 존재할 수 있는 unique name과 quota가 필요하다는 점을 함께 기록합니다.

## Experiments

### Replacement ordering

1. Provider schema에서 replacement를 요구하는 argument를 하나 선택합니다.
2. Normal plan과 `create_before_destroy = true` plan의 action order를 비교합니다.
3. 이름 uniqueness, quota, dependency가 old/new 동시 존재를 허용하는지 확인합니다.

```bash
terraform plan -out=replace.tfplan
terraform show replace.tfplan
```

Lifecycle block을 제거한 plan과 action order를 비교하되 둘 중 하나를 apply하기 전에 saved plan을 새로 만듭니다. Old saved plan을 configuration 변경 뒤 재사용하지 않습니다.

### Destroy protection

```hcl
lifecycle {
  prevent_destroy = true
}
```

Destroy 또는 replacement plan이 configuration error로 중단되는지 확인합니다. Block을 configuration에서 완전히 제거하면 이 보호를 평가할 block도 사라질 수 있으므로 별도 policy와 backup을 대신하지 않습니다.

`prevent_destroy = true`를 추가한 뒤 다음 두 command를 비교합니다.

```bash
terraform plan -destroy
terraform plan -replace=terraform_data.application
```

둘 다 configured object의 destroy/replacement를 거부해야 합니다. 하지만 resource block 자체를 configuration에서 삭제하면 lifecycle rule도 함께 사라진다는 한계를 설명합니다. Production protection은 HCP policy, permission, backup과 함께 설계합니다.

### Shared ownership

`ignore_changes`에 provider가 아닌 외부 controller가 소유하는 한 attribute만 지정합니다. 전체 변경을 무시하거나 실제 drift를 숨기는 설정은 피합니다.

`prevent_destroy`를 제거하고 다음 lifecycle을 시험합니다.

```hcl
lifecycle {
  ignore_changes = [input]
}
```

`external_note`를 바꿔도 input update가 plan에서 무시되는지 확인합니다. `triggers_replace`인 release는 계속 Terraform ownership이므로 변경 시 replacement가 보여야 합니다. 이것이 attribute ownership 분리입니다. `ignore_changes = all`은 Terraform이 create/destroy는 할 수 있지만 update를 거의 관리하지 않게 하므로 일반적 drift 해결책이 아닙니다.

## replace_triggered_by extension

```hcl
resource "terraform_data" "schema" {
  input = "schema-v1"
}

resource "terraform_data" "application" {
  input = var.external_note

  lifecycle {
    replace_triggered_by = [terraform_data.schema]
  }
}
```

Schema resource change가 application input을 직접 바꾸지 않아도 replacement signal을 주는지 plan에서 관찰합니다. Plain value에는 `terraform_data`를 bridge로 사용할 수 있습니다.

## Failure and decision table

| 목적 | 올바른 mechanism | 잘못된 기대 |
|---|---|---|
| Replacement 순서 변경 | `create_before_destroy` | 모든 downtime 자동 제거 |
| Configured destroy 차단 | `prevent_destroy` | resource block 삭제도 영구 차단 |
| External ownership 인정 | narrow `ignore_changes` | drift 전체 숨김 |
| 다른 managed change에 replace | `replace_triggered_by` | arbitrary string 직접 감시 |

Plan에 replacement가 없으면 변경한 argument가 provider/schema상 update인지 `triggers_replace`인지 확인합니다. Dependency cycle이 생기면 `create_before_destroy` propagation과 explicit `depends_on`을 검토합니다.

## Verification

- `create_before_destroy`: replacement order
- `prevent_destroy`: configured object의 destroy/replacement 거부
- `ignore_changes`: selected attribute의 update ownership 조정
- `replace_triggered_by`: 다른 managed change에 따른 replacement signal

Apply한 cloud object는 lifecycle protection을 제거하는 plan을 먼저 review한 뒤 destroy합니다.

```bash
# prevent_destroy를 제거하고 configuration을 validate한 뒤
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
terraform state list
rm -f replace.tfplan destroy.tfplan
```

완료 기준은 네 lifecycle argument를 한 문장씩 구분하고 각 setting이 해결하지 못하는 운영 risk를 하나씩 말하는 것입니다.

**Detailed walkthrough:** [Historical Lab 07](/archive/labs/lab-07-lifecycle/readme/)  
**Next:** [Lab 08 Custom conditions](/labs/08-custom-conditions/) · [Command matrix](/reference/command-behavior-matrix/)
