---
title: 명령 동작 매트릭스 / Command Behavior Matrix
description: Compare what common Terraform commands read, contact, and change across configuration, state, and remote APIs.
---

명령을 외울 때는 이름보다 **입력과 side effect**를 분리하세요. 아래 표는 기본 동작을 요약하며 option, backend, provider에 따라 remote access의 세부 사항은 달라질 수 있습니다.

## Core commands

| Command | Reads configuration | Reads state | Contacts provider API | Writes state | Changes remote objects |
|---|---:|---:|---:|---:|---:|
| `terraform fmt` | Yes | No | No | No | No |
| `terraform validate` | Yes | No | No | No | No |
| `terraform init` | Yes | Backend metadata | Downloads and backend access | Backend migration only | No managed-resource change |
| `terraform plan` | Yes | Yes | Normally yes | No persistent state change | No |
| `terraform apply` | Yes or saved plan | Yes | Yes | Yes | Usually yes |
| `terraform destroy` | Yes | Yes | Yes | Yes | Yes, destroys managed objects |
| `terraform show PLAN` | No configuration mutation | Reads plan/state data | No | No | No |
| `terraform output` | No | Yes | No refresh | No | No |

`validate`는 syntax와 internal consistency를 확인하지만 provider credential이 실제 API operation을 수행할 수 있다는 증거가 아닙니다. `plan`은 run-specific variable, state, provider schema와 remote object 정보를 포함해 더 넓은 context를 평가합니다.

## Plan modes and options

| Form | Purpose | Important boundary |
|---|---|---|
| `terraform plan` | Reconcile configuration, state, and remote reality | Produces a speculative plan unless saved |
| `terraform plan -out=tfplan` | Save an executable plan | The file can contain sensitive data |
| `terraform apply tfplan` | Execute the saved plan | Does not ask for a new plan approval |
| `terraform plan -refresh-only` | Review out-of-band changes | Does not propose changing remote objects |
| `terraform plan -destroy` | Preview destruction of all managed objects | Still only a plan |
| `terraform plan -replace=ADDRESS` | Force replacement in the proposed actions | Preferred over the deprecated `taint` workflow |

Saved plan file은 binary이며 `terraform show` 또는 `terraform show -json`으로 검사합니다. Plan에는 sensitive value가 cleartext로 포함될 수 있으므로 일반 artifact처럼 공개 저장하지 않습니다.

## State inspection and mutation

| Command | Category | Effect |
|---|---|---|
| `terraform state list` | Inspect | Lists addresses in state |
| `terraform state show ADDRESS` | Inspect | Displays recorded attributes for one instance |
| `terraform state pull` | Inspect/export | Downloads current state; output is sensitive |
| `terraform state mv SOURCE DESTINATION` | Mutate binding | Changes an address binding |
| `terraform state rm ADDRESS` | Mutate binding | Stops tracking without destroying the object |
| `terraform state push FILE` | Replace snapshot | Dangerous; can overwrite remote state |
| `terraform force-unlock LOCK_ID` | Lock recovery | Removes a failed lock, not another user's active lock |

State command가 remote object를 직접 삭제하지 않더라도 다음 normal plan에서 configuration과 binding의 불일치가 새로운 create/destroy proposal로 나타날 수 있습니다.

## Workflow checkpoints

1. `fmt -check`로 canonical formatting을 확인합니다.
2. `init`으로 backend, module, provider dependency를 준비합니다.
3. `validate`로 configuration 자체의 유효성을 확인합니다.
4. `plan -out`으로 실제 context의 action을 생성하고 review합니다.
5. 승인된 saved plan을 `apply`합니다.

**Official sources:** [`fmt`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/fmt), [`validate`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/validate), [`init`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/init), [`plan`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/plan), [`apply`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/apply), [State commands](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/state)
