---
title: Terraform 1.12 심화 포인트 / Deep Dive
description: Version-aware review of sensitive data, dependency locks, S3 locking, imports, and state refactoring for Associate 004.
---

이 페이지는 Associate 004의 Terraform 1.12 기준에서 오래된 학습 자료와 충돌하기 쉬운 동작을 모읍니다. 기능이 존재한다는 사실보다 **무엇을 저장하고, 무엇을 바꾸며, 어느 단계에서 동작하는지**를 우선해서 학습하세요.

This page focuses on behavior boundaries that commonly conflict with older study notes. Learn what each feature stores, mutates, and evaluates.

## Sensitive, ephemeral, and write-only

| Mechanism | CLI/UI redaction | Stored in plan/state | Key constraint |
|---|---:|---:|---|
| `sensitive = true` | Yes | Usually yes | Redaction is not encryption or storage prevention |
| `ephemeral = true` | Not by itself | No | Allowed only in ephemeral contexts |
| `sensitive = true` + `ephemeral = true` | Yes | No | Useful for temporary secret inputs |
| Provider write-only argument | Provider-defined | Value is omitted | A companion version argument may trigger updates |
| `ephemeral` resource | Not persisted | No | Exists only during the current operation |

`sensitive`는 사람이 보는 출력을 가리지만 state 저장을 막지 않습니다. 반대로 ephemeral value는 plan과 state에서 생략됩니다. 둘은 서로 대체 관계가 아니며 함께 지정할 수 있습니다.

`ephemeral`은 root module output에 지정할 수 없습니다. Child module output은 ephemeral value를 전달할 수 있지만, 그 값을 받는 경로 역시 허용된 ephemeral context여야 합니다.

```hcl
variable "database_password" {
  type      = string
  sensitive = true
  ephemeral = true
}
```

**Official sources:** [Manage sensitive data](https://developer.hashicorp.com/terraform/language/v1.12.x/manage-sensitive-data), [Ephemeral values](https://developer.hashicorp.com/terraform/language/v1.12.x/manage-sensitive-data/ephemeral), [Write-only arguments](https://developer.hashicorp.com/terraform/language/v1.12.x/manage-sensitive-data/write-only)

## Provider constraints and the lock file

`required_providers`와 `.terraform.lock.hcl`은 같은 역할이 아닙니다.

- Configuration constraint: 설치 가능한 provider version의 범위를 선언합니다.
- Dependency lock file: 선택된 provider version과 package checksum을 기록합니다.
- `terraform init`: constraint와 기존 lock selection을 함께 고려합니다.
- `terraform init -upgrade`: 기존 selection을 무시하고 constraint 안에서 새 version을 선택할 수 있습니다.
- Lock file은 현재 **provider dependency만** 추적하며 remote module version selection을 고정하지 않습니다.
- `.terraform.lock.hcl`은 review와 재현성을 위해 version control에 포함하는 것이 권장됩니다.

Module `version` constraint는 registry source에 적용합니다. Git source는 `?ref=` 같은 source-specific revision을 사용하고 local module은 현재 local file을 사용합니다.

**Official sources:** [Provider requirements](https://developer.hashicorp.com/terraform/language/v1.12.x/providers/requirements), [Dependency lock file](https://developer.hashicorp.com/terraform/language/v1.12.x/files/dependency-lock), [Module sources](https://developer.hashicorp.com/terraform/language/v1.12.x/modules/sources)

## S3 state locking

Terraform 1.12의 S3 backend는 `use_lockfile = true`로 S3 lock file을 사용할 수 있습니다.

```hcl
terraform {
  backend "s3" {
    bucket       = "example-state"
    key          = "production/terraform.tfstate"
    region       = "ap-northeast-2"
    use_lockfile = true
  }
}
```

- S3 locking은 opt-in이며 `use_lockfile`의 기본값은 `false`입니다.
- Lock object에는 `GetObject`, `PutObject`, `DeleteObject` 권한이 필요합니다.
- DynamoDB-based locking은 deprecated입니다. 구 version migration 동안 두 방식을 함께 구성할 수 있지만 새 기준으로 가르치지 않습니다.
- Backend가 locking을 지원하면 state를 쓸 수 있는 operation에서 Terraform이 자동으로 lock을 획득합니다.
- `-lock=false`는 corruption 위험을 높이므로 정상적인 해결책이 아닙니다.
- `force-unlock`은 자동 unlock이 실패한 **자신의 lock**에만 lock ID를 확인한 뒤 사용합니다.

**Official sources:** [S3 backend](https://developer.hashicorp.com/terraform/language/v1.12.x/backend/s3), [State locking](https://developer.hashicorp.com/terraform/language/v1.12.x/state/locking)

## Import and state refactoring

| Intent | Preferred mechanism | Remote object effect |
|---|---|---|
| Adopt an existing object | `import` block or `terraform import` | Object remains; binding is added |
| Rename or move an address | `moved` block | Object remains; binding address changes |
| Stop managing without destroy | `removed` block with `destroy = false` | Object remains; binding is removed |
| Record out-of-band changes | Refresh-only plan/apply | State and outputs update; object is not changed |
| Intentionally replace one instance | `-replace=ADDRESS` | Replacement is planned and applied |

Import는 remote object를 새로 만드는 작업이 아니라 configuration address와 existing object identity의 binding을 state에 추가하는 작업입니다. Destination `resource` configuration은 imported object를 이후 어떤 상태로 관리할지 정의합니다.

`moved`와 `removed` block은 imperative state command보다 intent와 history가 configuration에 남는다는 장점이 있습니다. 모든 변경은 plan에서 address와 action을 확인한 뒤 적용합니다.

**Official sources:** [Import resources](https://developer.hashicorp.com/terraform/language/v1.12.x/import), [`moved` block](https://developer.hashicorp.com/terraform/language/v1.12.x/moved), [`removed` block](https://developer.hashicorp.com/terraform/language/v1.12.x/removed), [Refresh-only mode](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/plan#refresh-only-mode)

## Exam-ready distinctions

- Provider manages resource types; backend stores state and may lock it.
- Constraint allows versions; lock file records a selection.
- `sensitive` hides display; `ephemeral` prevents persistence.
- Import adds a binding; `moved` changes its address; `removed` removes it.
- Refresh-only reconciles recorded data; normal apply can change remote objects.
