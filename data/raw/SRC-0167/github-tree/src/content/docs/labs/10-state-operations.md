---
title: Lab 10. State 검사와 리팩터링 / State Operations
description: Inspect and refactor disposable state using configuration-driven moved and removed blocks before considering imperative commands.
---

| Level | Time | Objectives |
|---|---:|---|
| Advanced | 50-70 min | 6d, 7a-7c |

**Read first:** [State management](/domains/06-state/), [Maintain infrastructure](/domains/07-maintain/)

## Outcome

Disposable local state에서 address를 검사하고 rename, management removal, import의 binding 변화를 구분합니다. Raw state JSON을 직접 편집하지 않습니다.

:::caution[Disposable state only]
Production state로 연습하지 마세요. 시작 전 `terraform state pull > state-backup.json`을 만들고 backup도 secret으로 취급합니다.
:::

## Inspect without mutation

```bash
terraform state list
terraform state show ADDRESS
terraform show
terraform output -json
```

각 명령이 configuration, state snapshot, remote API 중 무엇을 읽는지 [command matrix](/reference/command-behavior-matrix/#state-inspection-and-mutation)와 대조합니다.

## Build disposable state

```text
lab-10/
├── versions.tf
└── main.tf
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="main.tf"
resource "terraform_data" "old_name" {
  input = {
    owner = "study"
    phase = "before-move"
  }
}

output "record_id" {
  value = terraform_data.old_name.id
}
```

```bash
terraform init
terraform apply -auto-approve
terraform state list
terraform state pull > state-backup.json
```

Expected address는 `terraform_data.old_name`입니다. Backup은 public repository에 commit하지 않고 Lab 종료 후 폐기합니다.

## Rename with configuration

Resource block label을 바꾸고 old/new address를 `moved` block에 기록합니다.

```hcl
moved {
  from = terraform_data.old_name
  to   = terraform_data.new_name
}
```

Plan이 rename만으로 destroy/create를 제안하지 않는지 확인합니다.

Resource block label을 `new_name`으로 바꾸고 다음 block을 추가합니다.

```hcl
moved {
  from = terraform_data.old_name
  to   = terraform_data.new_name
}
```

Output reference도 `new_name`으로 바꿉니다.

```bash
terraform plan -out=move.tfplan
terraform show move.tfplan
terraform apply move.tfplan
terraform state list
```

Expected plan은 address move를 표시하며 remote create/destroy가 없어야 합니다. Apply 뒤 state에는 `terraform_data.new_name`만 남습니다. ID가 유지되는지 move 전 기록과 비교합니다. Deliberate comparison으로 `moved` block을 잠시 제거해 old destroy/new create plan을 확인하되 apply하지 않고 block을 복구합니다.

## Stop management without destroy

`removed` block과 `destroy = false`를 사용해 remote object를 유지한 채 binding removal을 plan합니다. 같은 의도를 `terraform state rm`으로 수행할 수 있지만 configuration-driven history가 남지 않는 차이를 설명합니다.

Resource block과 output을 제거하고 다음을 추가합니다.

```hcl
removed {
  from = terraform_data.new_name

  lifecycle {
    destroy = false
  }
}
```

```bash
terraform plan -out=forget.tfplan
terraform show forget.tfplan
```

Plan은 object destroy 없이 state에서 제거할 의도를 보여야 합니다. `terraform_data`는 실제 external object가 없지만 binding semantics를 안전하게 관찰할 수 있습니다. Production cloud object에서는 이후 Terraform이 더 이상 update/destroy하지 않으며 ownership 문서가 필요합니다.

`terraform state rm ADDRESS`는 비슷한 결과를 즉시 만들지만 code review 가능한 configuration history가 없습니다. Emergency나 legacy workflow가 아니라면 `removed` block을 우선 검토합니다.

## Import boundary

Existing disposable object에 맞는 `resource` configuration과 `import` block을 작성합니다. Import가 configuration을 조직 표준에 맞게 완성해 주지 않으며 address-to-object binding을 추가한다는 점을 plan에서 확인합니다.

Removed plan을 apply한 뒤 import 실험을 위해 resource를 다시 정의합니다.

```hcl
resource "terraform_data" "imported" {
  input = "managed-after-import"
}

import {
  to = terraform_data.imported
  id = "lab-10-import-id"
}
```

```bash
terraform plan -out=import.tfplan
terraform show import.tfplan
```

Importer의 ID format은 resource type마다 다릅니다. Built-in resource behavior가 설치된 Terraform patch에서 다르면 production 객체로 우회하지 말고 diagnostic을 기록한 뒤 official import docs와 conceptual binding 효과를 비교합니다. Import 뒤 normal plan에서 input update가 나타날 수 있으며 이는 import가 configuration을 자동 완성하지 않기 때문입니다.

## Imperative command comparison

Disposable backup이 있는 상태에서 `terraform state mv terraform_data.imported terraform_data.renamed`와 `terraform state rm terraform_data.renamed`의 효과를 예측합니다. 실제 실행하면 configuration도 즉시 같은 address/ownership으로 수정한 후 plan합니다. State command만 실행하고 configuration을 그대로 두면 다음 plan이 create/destroy를 제안할 수 있습니다.

## Troubleshooting and recovery

| 증상 | 원인 | 대응 |
|---|---|---|
| move 뒤 create/destroy | from/to address 불일치 | module/index/key 포함 full address 확인 |
| import already managed | binding 중복 | duplicate binding을 만들지 말고 ownership 조사 |
| state lock error | active writer 또는 stale lock | active operation 확인, 정상 종료 대기 |
| backup에 secret 노출 | raw state 취급 오류 | 접근 제한과 안전한 폐기 |

Raw state JSON을 text editor로 수정하지 않습니다. 문제가 생기면 current state, backup, configuration, remote reality를 비교하고 versioned backend recovery procedure를 따릅니다.

## Logging and cleanup

필요한 경우에만 `TF_LOG=DEBUG` 또는 `TRACE`를 짧게 사용하고, log에 credential과 value가 포함될 수 있으므로 종료 후 삭제합니다. Lab 종료 시 configuration과 state가 같은 의도를 표현하는지 확인한 뒤 remote object를 정리합니다.

```bash
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
terraform state list
rm -f move.tfplan forget.tfplan import.tfplan destroy.tfplan state-backup.json terraform-debug.log
unset TF_LOG TF_LOG_PATH
```

완료 기준은 moved/import/removed가 binding을 이동/추가/제거한다는 효과와 remote mutation 여부를 설명하고, imperative state command 사용 뒤 configuration reconciliation이 필요한 이유를 말하는 것입니다.

**Detailed walkthrough:** [Historical Lab 10](/archive/labs/lab-10-state-manipulation/readme/)  
**Next:** [Lab 11 Registry modules](/labs/11-registry-modules/) · [State questions](/archive/practice-exams/domain-6-state/)
