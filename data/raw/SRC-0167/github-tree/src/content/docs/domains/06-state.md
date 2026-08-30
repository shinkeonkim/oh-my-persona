---
title: 06. 상태 관리 / State Management
description: "Objectives 6a-6d: local and remote backends, locking, drift, and state refactoring."
---

## Three-way comparison

Terraform operation compares three things: **configuration (desired)**, **prior state (known binding)**, and **remote objects (observed reality)**. A plan explains the proposed convergence among them.

## 6a-6c. Backend and locking

The local backend stores state on disk. Remote backends centralize storage and may provide locking. Backend configuration is initialized with `terraform init`; changing it can trigger state migration or reconfiguration choices.

```hcl
terraform {
  backend "s3" {
    bucket       = "example-terraform-state"
    key          = "production/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }
}
```

:::caution
Terraform 1.12의 S3 backend는 `use_lockfile`을 지원합니다. DynamoDB-based locking은 deprecated이므로 기존 Archive의 DynamoDB 필수 설명을 현재 권장 방식으로 사용하지 마세요.
:::

Locking prevents competing state writers; it does not protect against every operational race or secure state contents. Force-unlock only after verifying the original writer is gone.

## 6d. Drift and safe refactoring

| Situation | Preferred mechanism |
|---|---|
| Observe external changes | normal plan or refresh-only plan |
| Accept remote changes into state only | `terraform apply -refresh-only` after review |
| Rename/move an address | `moved` block |
| Stop managing without destroying | `removed` block with appropriate lifecycle |
| Inspect bindings | `terraform state list/show`, `terraform show` |

Manual state editing is the last resort. Pull a backup, use supported commands, and understand that state subcommands change bindings rather than remote infrastructure unless their documentation says otherwise.

## State snapshot의 핵심 구성

State는 resource instance address, provider association, remote object ID, known attributes, dependency metadata, outputs를 포함하는 Terraform의 내부 snapshot입니다. 실제 JSON schema를 암기하거나 직접 편집하는 것이 시험 목표는 아닙니다. 대신 다음 관계를 설명해야 합니다.

```text
configuration address
  aws_instance.web["blue"]
          |
          | state binding
          v
remote object identity
  provider-specific ID
```

Configuration에서 block label을 바꾸면 remote object가 그대로여도 Terraform address가 달라집니다. 아무 조치가 없으면 old address destroy와 new address create를 제안할 수 있습니다. `moved` block은 old-to-new binding 이동 의도를 configuration history에 기록합니다.

## Backend가 결정하는 것

Backend는 state snapshot 저장 위치와 operation 실행 방식 일부를 결정합니다. Local backend는 filesystem에 저장하고 기본적인 local locking을 사용합니다. Remote backend는 중앙 저장, encryption/access control integration, locking 또는 remote operations를 제공할 수 있지만 기능은 backend마다 다릅니다.

Backend block은 variable이나 local value를 참조할 수 없습니다. Backend initialization은 expression evaluation보다 이른 단계에 일어나기 때문입니다. Credential도 block에 literal로 넣지 않고 environment, shared profile, workload identity 등 backend가 지원하는 standard chain을 사용합니다.

### Static and partial backend configuration

Backend 설정은 일반 HCL expression처럼 평가되지 않습니다. `var.bucket`, `local.state_key`, resource reference, function call을 backend block에 넣을 수 없으며 sensitive credential을 committed `.tf`에 저장해서도 안 됩니다.

공유 configuration에는 backend type만 선언하고 environment별 값은 initialization에서 공급하는 partial configuration을 사용할 수 있습니다.

```hcl
terraform {
  backend "s3" {}
}
```

```bash
terraform init \
  -backend-config="bucket=example-terraform-state" \
  -backend-config="key=production/terraform.tfstate" \
  -backend-config="region=ap-northeast-2" \
  -backend-config="use_lockfile=true"
```

`-backend-config` 값과 backend가 읽는 environment variable은 shell history, CI log, `.terraform/terraform.tfstate` backend metadata 등에 남을 수 있습니다. Access key나 token을 command line에 직접 전달하지 말고 backend의 credential chain을 사용하세요. Backend configuration file을 사용할 때도 secret이 없다면 commit 가능하지만, credential이 포함되면 별도 secret artifact로 보호하고 전달·폐기 절차를 정의해야 합니다.

Partial configuration은 environment별 state 위치를 공급하는 방법이지 Terraform input variable precedence의 일부가 아닙니다. `TF_VAR_*`는 root input variable을 위한 convention이며 backend argument를 자동 설정하지 않습니다.

### Backend 변경 절차

1. 현재 state backup과 backend versioning을 확인합니다.
2. 새 backend가 먼저 존재하고 접근 가능한지 확인합니다.
3. Backend configuration을 변경합니다.
4. `terraform init -migrate-state`로 source/destination을 확인하고 migration합니다.
5. `terraform state pull`, `state list`, normal plan으로 binding과 no-op 여부를 확인합니다.

`-reconfigure`는 이전 backend metadata를 무시하고 현재 설정을 채택합니다. Existing state를 자동 migration하는 의미가 아니므로 recovery 문맥 없이 사용하지 않습니다.

## Locking의 정확한 범위

State locking은 동시에 두 writer가 같은 snapshot을 갱신하는 것을 막습니다. 모든 backend가 locking을 지원하는 것은 아니며 read-only command와 operation별 동작도 다를 수 있습니다. Lock은 remote infrastructure 전체의 transaction이나 API 경쟁 상태를 해결하지 않습니다.

Terraform 1.12 S3 backend의 `use_lockfile = true`는 S3 lock object를 사용합니다. DynamoDB-based locking은 deprecated입니다. 기존 환경이 migration 기간에 두 방식을 함께 구성할 수는 있지만 신규 가이드의 기본으로 DynamoDB table을 요구하지 않습니다.

`-lock=false`는 정상 workaround가 아닙니다. `force-unlock LOCK_ID`도 원래 process가 종료됐고 자동 해제가 실패했음을 확인한 자신의 lock에만 사용합니다. 살아 있는 writer의 lock을 제거하면 snapshot overwrite가 발생할 수 있습니다.

## Refresh, drift, reconciliation

**Drift**는 remote object가 Terraform configuration/state가 기대하는 값과 달라진 상황입니다. Normal plan은 provider read를 통해 drift를 발견하고 configuration으로 되돌리거나 replacement하는 change를 제안할 수 있습니다.

| 의도 | 도구 | Remote object mutation |
|---|---|---|
| Drift를 configuration으로 되돌림 | normal plan/apply | 있음 |
| Out-of-band 값을 state에 채택 | refresh-only plan/apply | 없음 |
| Address rename 기록 | `moved` block | 없음, binding 이동 |
| 관리만 중단하고 객체 유지 | `removed` + `destroy = false` | 없음, binding 제거 |
| 기존 객체 관리 시작 | `import` block | 없음, binding 추가 |

Refresh-only는 “drift 수정”이 아니라 remote reality를 state/output에 받아들이는 선택입니다. 이후 configuration이 여전히 다르면 다음 normal plan에서 다시 change가 나타날 수 있으므로 configuration도 의도에 맞게 수정해야 합니다.

## State command를 읽기와 mutation으로 분류

### Inspection

- `terraform state list`: snapshot 안의 address 목록
- `terraform state show ADDRESS`: 한 instance의 known attributes
- `terraform show`: current state 또는 saved plan의 human-readable view
- `terraform output -json`: root outputs를 machine-readable form으로 조회

### Binding mutation

- `terraform state mv`: binding address 이동
- `terraform state rm`: remote destroy 없이 binding 제거
- `terraform import`: existing object와 address 연결
- `terraform force-unlock`: failed lock recovery

Imperative state command는 즉시 snapshot을 바꾸므로 backup과 peer coordination이 필요합니다. 가능한 경우 `moved`, `removed`, `import` block으로 의도를 configuration과 review history에 남깁니다.

## State security와 recovery

State에는 password, token, private endpoint, generated value가 포함될 수 있습니다. Backend encryption at rest/in transit, least-privilege access, versioning, audit log, retention을 적용합니다. Local backup과 `state pull` 결과도 같은 secret classification으로 취급합니다.

Recovery는 “새 빈 state로 다시 시작”이 아닙니다. Versioned snapshot을 확인하고 lineage/serial 및 실제 infrastructure와 일치하는 restore point를 선택한 뒤 plan으로 검증합니다. Backend object를 수동 overwrite하기 전에 provider/HashiCorp의 recovery 절차와 조직 change process를 따릅니다.

## 시험 함정과 self-check

- Remote backend가 언제나 locking 또는 remote execution을 제공한다고 가정하지 않습니다.
- Locking은 state writer를 조정하며 state encryption과 다른 기능입니다.
- `state rm`은 remote object를 삭제하지 않지만 다음 plan은 새 object 생성을 제안할 수 있습니다.
- `terraform refresh` 독립 명령보다 review 가능한 refresh-only plan/apply 흐름을 우선합니다.
- Backend configuration과 provider configuration의 credential 경계는 다릅니다.

다음을 설명할 수 있어야 합니다.

1. Configuration/state/remote object의 three-way comparison에서 drift가 발견되는 지점은 어디인가?
2. `moved`, `removed`, `import` block이 binding에 더하고 빼고 이동하는 효과는 무엇인가?
3. S3 `use_lockfile`과 deprecated DynamoDB locking을 어떻게 구분하는가?
4. `force-unlock` 전에 어떤 사실을 확인해야 하는가?
5. State backup을 public artifact로 저장하면 안 되는 이유는 무엇인가?

## 다음 연결 / Why next

State를 이해하면 기존 객체를 import하고 문제를 진단할 수 있습니다. 다음은 [maintain infrastructure](/domains/07-maintain/)입니다.

**Official sources:** [State](https://developer.hashicorp.com/terraform/language/v1.12.x/state), [Backends](https://developer.hashicorp.com/terraform/language/v1.12.x/state/backends), [Locking](https://developer.hashicorp.com/terraform/language/v1.12.x/state/locking), [Refactor](https://developer.hashicorp.com/terraform/language/v1.12.x/state/refactor)<br />
**Labs:** [06 Remote state](/labs/06-remote-state/), [10 State operations](/labs/10-state-operations/)<br />
**Questions:** [Domain 6 bank](/archive/practice-exams/domain-6-state/)
