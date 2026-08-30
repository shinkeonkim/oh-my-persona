---
title: 03. 핵심 워크플로우 / Core Workflow
description: "Objectives 3a-3g: write, init, validate, plan, apply, destroy, and fmt."
---

## 전체 흐름 / End-to-end flow

```text
Write -> fmt -> init -> validate -> plan -> review -> apply -> observe
                                                          -> destroy (when intended)
```

The workflow is a chain of artifacts. Configuration and lock constraints feed initialization; initialized schemas enable validation; configuration plus prior state plus refreshed remote data produce a plan; apply executes an approved plan and writes new state.

## 명령별 책임 / Command responsibilities

| Command | Primary responsibility | 자주 혼동하는 점 / Common confusion |
|---|---|---|
| `terraform fmt` | Canonical style | 의미나 provider API 유효성을 검증하지 않음 |
| `terraform init` | Backend/module/provider initialization | 리소스를 생성하지 않음 |
| `terraform validate` | Internal syntax/type consistency | Remote API existence를 보장하지 않음 |
| `terraform plan` | Proposed change set | Apply 전까지 실제 객체를 변경하지 않음 |
| `terraform apply` | Execute changes and update state | Saved plan 사용 시 그 plan을 적용 |
| `terraform destroy` | Plan/apply deletion of managed objects | State 밖 객체는 대상이 아님 |

## Saved plan pattern

```bash
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
```

Saved plan은 검토한 변경과 적용할 변경 사이의 불일치를 줄입니다. Automation에서는 exit code와 non-interactive options를 목적에 맞게 사용하되, `-auto-approve`를 안전성 자체로 오해하지 않습니다.

## Dependency graph

Expression reference가 graph edge를 만들며, Terraform은 독립 노드를 병렬 처리할 수 있습니다. `depends_on`은 expression으로 표현되지 않는 숨은 의존성이 있을 때만 사용합니다.

Expression references create graph edges. Use `depends_on` only for hidden dependencies that data flow cannot express.

## 각 단계의 입력과 산출물 / Inputs and artifacts

| 단계 | 읽는 것 | 만드는 것 | Remote mutation |
|---|---|---|---|
| Write | 요구사항, module contract | `.tf`, `.tfvars` | 없음 |
| `fmt` | Terraform source | canonical formatting | 없음 |
| `init` | backend/module/provider requirements | `.terraform/`, lock selection | managed resource 생성 없음 |
| `validate` | initialized schema와 configuration | diagnostics | 없음 |
| `plan` | configuration, variables, state, provider reads | proposed plan 또는 saved plan | 일반적으로 없음 |
| `apply` | 새 plan 또는 saved plan | remote changes, new state, outputs | 있음 |
| `destroy` | configuration/state/provider reads | destroy plan과 새 state | 있음 |

### Write와 input precedence

Root module input은 default, environment variable, variable files, CLI options 등 여러 source에서 올 수 있습니다. 시험에서는 정확한 precedence를 무작정 외우기보다 “같은 variable에 여러 source가 값을 제공하면 더 높은 우선순위 source가 선택된다”, “child module input은 module call argument로 전달한다”는 경계를 먼저 잡습니다. Secret을 command history나 committed tfvars에 남기지 않습니다.

### `terraform init`

Working directory를 backend, module, provider를 사용할 수 있는 상태로 준비합니다. Configuration에 새 provider나 module source가 추가됐거나 backend가 바뀌면 다시 실행합니다. 반복 실행 자체는 안전하지만 option의 의미는 다릅니다.

- `-upgrade`: configured constraint 안에서 provider/module selection을 다시 찾습니다.
- `-migrate-state`: backend 변경 시 existing state 이동을 시도합니다.
- `-reconfigure`: 이전 backend metadata를 무시하고 현재 설정을 새로 채택합니다.
- `-backend=false`: backend initialization을 생략하는 제한적 automation 용도입니다.

### `fmt`와 `validate`

`fmt`는 canonical style로 source를 고칩니다. `fmt -check`는 CI에서 수정 없이 비정상 formatting을 exit code로 확인할 때 유용합니다. `validate`는 syntax, type, internal reference consistency를 검사하지만 실제 credential 권한, quota, remote object existence를 완전히 증명하지 않습니다. Reusable module 검증에서는 `init -backend=false`와 함께 사용할 수 있습니다.

### Plan을 읽는 법

Plan symbol은 단순 성공/실패가 아니라 action을 나타냅니다. `+` create, `~` in-place update, `-` destroy, `-/+` 또는 `+/-` replacement order를 읽고 어떤 argument가 replacement를 유발하는지 확인합니다. `(known after apply)`는 apply 전 계산할 수 없는 **unknown value**이지 오류나 null과 같지 않습니다.

```bash
terraform plan -out=tfplan
terraform show tfplan
terraform show -json tfplan > tfplan.json
```

Saved plan은 review와 execution 사이의 의도를 고정하는 artifact입니다. `terraform apply tfplan`은 새로운 planning options를 받지 않고 저장된 action을 실행합니다. 하지만 remote API에서 apply-time error가 발생하지 않는다는 보장은 아닙니다. Saved plan에는 sensitive value가 포함될 수 있어 공유 artifact로 공개하면 안 됩니다.

Automation은 `terraform plan -detailed-exitcode`를 사용할 수 있습니다. 일반적으로 0은 no changes, 2는 changes present, 1은 error를 뜻하므로 “2를 실패로 처리하는 일반 shell convention”과 구분해야 합니다.

### Apply, replacement, destroy

Saved plan 없이 `terraform apply`하면 Terraform이 새 plan을 만들고 승인을 요청합니다. `-auto-approve`는 승인 prompt를 생략할 뿐 권한 검토나 정책 enforcement를 대신하지 않습니다. `-replace=ADDRESS`는 정상 configuration을 유지하면서 특정 instance replacement를 plan하도록 요청하며 deprecated `taint`보다 review 가능한 흐름입니다.

`terraform destroy`는 관리 중인 전체 객체에 대해 destroy plan을 만들고 적용하는 convenience command입니다. State 밖의 객체나 다른 workspace의 객체까지 검색해 삭제하지 않습니다. 특정 resource block을 configuration에서 제거한 결과와 전체 destroy는 같은 operation이 아닙니다.

## Refresh와 drift

Normal plan은 기본적으로 remote object를 읽고 state snapshot과 configuration을 비교합니다. `-refresh-only` mode는 out-of-band remote change를 state와 output에 반영하는 proposal을 만들되 remote object 변경을 제안하지 않습니다. 반대로 `-refresh=false`는 stale state를 기준으로 판단할 위험이 있어 제한적 상황에서만 사용합니다.

## Graph, parallelism, unknown values

Reference는 값 전달과 dependency edge를 함께 만듭니다. Terraform은 서로 독립적인 graph node를 병렬 실행할 수 있습니다. `depends_on`을 과도하게 추가하면 불필요한 ordering과 더 많은 unknown value를 만들어 plan이 보수적으로 바뀔 수 있습니다. Hidden dependency가 실제로 있고 expression으로 표현할 값이 없을 때만 사용합니다.

## 실패 지점으로 진단하기 / Diagnose by phase

| 실패 시점 | 먼저 확인할 것 |
|---|---|
| Parse/fmt | block syntax, argument spelling, delimiters |
| Init | network, source address, version constraint, backend auth |
| Validate | type mismatch, missing reference, module contract |
| Plan | variable values, provider auth, data-source read, quota/schema |
| Apply | API conflict, eventual consistency, permissions, concurrent lock |
| State write | backend access, lock ownership, storage/versioning |

## 스스로 설명하기 / Recall checks

- `fmt`, `validate`, `plan`이 각각 검증하지 않는 것을 하나씩 말할 수 있는가?
- Saved plan을 사용하는 이유와 그래도 남는 apply-time risk를 설명할 수 있는가?
- `init -migrate-state`, `-reconfigure`, `-upgrade`를 서로 바꾸지 않고 설명할 수 있는가?
- Plan의 unknown value와 null, sensitive redaction 차이는 무엇인가?
- `-detailed-exitcode`의 0/1/2를 CI decision으로 변환할 수 있는가?

## 다음 연결 / Why next

Workflow가 읽는 입력은 Terraform configuration입니다. 다음 단계에서 [HCL block, expression, type, dependency](/domains/04-configuration/)를 연결합니다.

**Official sources:** [Core workflow](https://developer.hashicorp.com/terraform/intro/v1.12.x/core-workflow), [`init`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/init), [`plan`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/plan), [`apply`](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/apply)<br />
**Lab:** [Lab 01 First project](/labs/01-first-project/)<br />
**Review:** [Command behavior matrix](/reference/command-behavior-matrix/)<br />
**Questions:** [Domain 3 bank](/archive/practice-exams/domain-3-core-workflow/)
