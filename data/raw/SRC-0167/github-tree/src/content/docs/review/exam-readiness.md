---
title: 시험 대비 최종 정리 / Exam Readiness
description: A final objective-by-objective review connecting concepts, labs, behavior boundaries, and the canonical question bank.
---

시험 준비 완료 여부를 점수 하나로 판단하지 마세요. 각 objective의 동작을 설명하고, 관련 Lab에서 관찰하고, 오답을 공식 문서로 교정할 수 있어야 합니다.

## Readiness map

**모바일 / Mobile:** 오른쪽 열이 보이지 않으면 표 안을 좌우로 스크롤하세요. Swipe horizontally inside the table to read every column.

| Domain | Explain without notes | Prove in a Lab | Practice |
|---|---|---|---|
| 1. IaC | declarative intent, reviewability, multi-provider workflow | [Lab 01](/labs/01-first-project/) | [20 questions](/archive/practice-exams/domain-1-iac-concepts/) |
| 2. Fundamentals | provider requirement/configuration, alias, lock file, state binding | [Lab 01](/labs/01-first-project/) | [20 questions](/archive/practice-exams/domain-2-terraform-fundamentals/) |
| 3. Workflow | write/init/validate/plan/apply/destroy and saved plans | [Lab 01](/labs/01-first-project/) | [25 questions](/archive/practice-exams/domain-3-core-workflow/) |
| 4. Configuration | resource/data, types, expressions, dependencies, conditions, secrets | [Labs 02-09](/labs/) | [35 questions](/archive/practice-exams/domain-4-configuration/) |
| 5. Modules | source, scope, composition, version selection | [Labs 05 and 11](/labs/05-modules/) | [25 questions](/archive/practice-exams/domain-5-modules/) |
| 6. State | backend, locking, migration, drift, moved/removed | [Labs 06 and 10](/labs/06-remote-state/) | [30 questions](/archive/practice-exams/domain-6-state/) |
| 7. Maintain | import, state inspection, verbose logging | [Lab 10](/labs/10-state-operations/) | [25 questions](/archive/practice-exams/domain-7-maintain/) |
| 8. HCP Terraform | runs, workspace/project, auth, governance, integrations | [Lab 12](/labs/12-hcp-terraform/) | [20 questions](/archive/practice-exams/domain-8-hcp-terraform/) |

## Objective별 공부할 내용 / Objective curriculum

아래 표의 **설명할 수 있어야 함**은 definition 암기가 아니라 입력, 실행 phase, state/remote 영향까지 자신의 말로 연결한다는 뜻입니다. **구분할 함정**은 보기에서 서로 바꿔 제시되는 개념입니다.

### Domain 1. Infrastructure as Code with Terraform

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 1a | IaC, desired state, declarative configuration, reconciliation | Configuration, prior state, provider read를 비교해 plan이 만들어지는 흐름 | Declarative가 모든 API 호출·무중단·보안을 자동 보장한다는 주장 |
| 1b | version control, repeatability, reviewability, automation, auditability | Git diff와 plan review가 manual click-ops보다 변경 통제를 높이는 이유 | IaC가 비용 0, drift 0, vulnerability 0을 보장한다는 주장 |
| 1c | provider plugin, multi-cloud, hybrid, service-agnostic workflow | Terraform Core가 공통 graph/workflow를 제공하고 provider가 서로 다른 API schema를 구현하는 방식 | Multi-cloud가 cloud 간 자동 migration 또는 동일 resource schema라는 주장 |

**읽기 순서:** [Domain 1](/domains/01-iac/) → [Lab 01](/labs/01-first-project/)의 두 번째 no-op plan → [Domain 1 문제](/archive/practice-exams/domain-1-iac-concepts/).

**Recall:** “Terraform은 declarative이므로 항상 idempotent하다”라는 문장을 정확한 조건과 예외를 포함해 고쳐 말해보세요. Provider schema, external drift, changing data source가 두 번째 plan에 미치는 영향까지 말할 수 있어야 합니다.

### Domain 2. Terraform fundamentals

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 2a | provider source, version constraint, selection, checksum, dependency lock file | `required_providers`, `.terraform.lock.hcl`, `init -upgrade`가 각각 결정하는 것 | Constraint와 selected version을 같은 값으로 보는 것 |
| 2b | Terraform Core/provider protocol, resource/data schema, provider configuration | Core가 graph/plan을 조정하고 provider가 target API를 호출하는 책임 분리 | Backend가 resource type을 구현하거나 provider가 state location을 결정한다는 주장 |
| 2c | multiple providers, aliases, provider inheritance/mapping | Region/account별 alias와 child module `providers` map을 구성하는 방식 | Alias가 별도 binary 또는 automatic cross-region replication이라는 주장 |
| 2d | state binding, address, remote ID, attributes, metadata, backend | State가 HCL copy가 아니라 address-to-object binding인 이유 | State를 remote infrastructure 자체 또는 단순 inventory로 보는 것 |

**반드시 직접 확인:** `terraform init` 후 provider constraint와 lock selection을 두 파일에서 각각 표시하고, aliased provider가 resource의 `provider = aws.dr`로 선택되는 예를 쓸 수 있어야 합니다.

**Recall:** State를 잃은 configuration이 같은 bucket 이름을 포함하고 있어도 Terraform이 자동으로 기존 bucket을 관리 대상으로 확정할 수 없는 이유를 binding 관점에서 설명하세요.

### Domain 3. Core Terraform workflow

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 3a | write → init → validate → plan → apply → operate | 각 phase가 읽고 만드는 artifact와 remote mutation 여부 | 모든 명령이 provider API를 변경한다는 주장 |
| 3b | backend/module/provider initialization, `-upgrade`, `-migrate-state`, `-reconfigure` | Source나 backend 변화에 따라 어떤 init mode를 선택하는가 | `init`이 infrastructure를 생성하거나 `-reconfigure`가 state를 자동 이동한다는 주장 |
| 3c | syntax, type, reference consistency, initialized schema | `validate`가 확인하는 것과 credential/quota까지 증명하지 못하는 것 | `fmt`, `validate`, `plan`을 같은 검증으로 보는 것 |
| 3d | plan actions, unknown values, saved plan, detailed exit code | `+`, `~`, `-`, replacement와 `(known after apply)`를 읽는 법 | Plan이 apply 성공과 no drift를 영구 보장한다는 주장 |
| 3e | apply approval, saved plan execution, state write | Saved plan과 automatic new plan apply의 차이 | `-auto-approve`가 policy/security 검토를 제공한다는 주장 |
| 3f | destroy plan, managed scope, protection | `destroy`가 current state의 managed objects를 대상으로 하는 과정 | Account의 모든 object 또는 state 밖 object까지 삭제한다는 주장 |
| 3g | canonical formatting, `fmt -check` | Source style normalization과 CI check behavior | `fmt`가 configuration semantics나 remote resource를 검증한다는 주장 |

**명령 비교 과제:** [`command behavior matrix`](/reference/command-behavior-matrix/)에서 `fmt`, `validate`, `plan`, `show`, `apply` 행을 가리고 각 명령의 configuration/state/provider read와 mutation을 복원하세요.

**Recall:** `terraform plan -out=tfplan` 뒤 configuration이 변경됐다면 왜 old saved plan을 그대로 적용하지 않아야 하는지 artifact와 lock consistency 관점에서 설명하세요.

### Domain 4. Terraform configuration

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 4a | resource vs data block, lifecycle ownership | Managed resource와 read-only lookup의 plan/state/remote 차이 | Data source가 state에 아무 정보도 남기지 않거나 object를 생성한다는 주장 |
| 4b | attribute reference, implicit dependency, resource address | Reference가 value flow와 graph edge를 함께 만드는 과정 | 문자열로 쓴 address 또는 block 작성 순서가 dependency라는 주장 |
| 4c | input variable, local value, output, precedence, sensitivity | Root input, internal calculation, public module output 경계 | Output이 root input을 공급하거나 local을 caller가 override한다는 주장 |
| 4d | primitive, list/set/map, tuple/object, null, unknown | Type constraint와 collection identity가 evaluation에 미치는 영향 | List와 set이 모두 stable index/order를 갖는다는 주장 |
| 4e | conditional, `for`, splat, functions, templates, dynamic blocks | Value transformation, resource repetition, nested block generation을 구분 | `dynamic`이 arbitrary HCL 또는 top-level resource를 생성한다는 주장 |
| 4f | implicit/explicit dependency, `count`, `for_each`, lifecycle | Stable key와 numeric index, hidden dependency, replacement ordering | 모든 resource에 `depends_on`이 필요하거나 count가 항상 replacement한다는 주장 |
| 4g | variable validation, precondition, postcondition, check | Available data와 blocking/warning behavior에 맞춰 condition을 배치 | `check` failure가 항상 apply를 차단한다는 주장 |
| 4h | sensitive, ephemeral, write-only, Vault, dynamic credentials, secure state | Display redaction, non-persistence, credential delivery, backend protection의 차이 | `sensitive = true` 또는 Vault 사용만으로 state 비저장이 보장된다는 주장 |

**실습 연결:** [Lab 02](/labs/02-variables-outputs/)에서 typed contract, [Lab 04](/labs/04-count-for-each/)에서 instance identity, [Lab 08](/labs/08-custom-conditions/)에서 failure phase, [Lab 09](/labs/09-dynamic-blocks/)에서 nested block을 확인합니다.

**Recall:** `for` expression, `for_each`, `dynamic`을 각각 한 줄 HCL로 쓰고 결과가 value/resource instance/nested block 중 무엇인지 말하세요. `null`, unknown, sensitive도 서로 바꾸지 않고 설명해야 합니다.

### Domain 5. Terraform modules

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 5a | local, registry, Git/object-storage source | Source별 installation과 version pin 방식 | 모든 source가 module `version` argument를 지원한다는 주장 |
| 5b | root/child scope, input/output contract, resource address | Child가 parent local/resource를 자동으로 보지 못하는 이유 | 같은 variable 이름이 scope를 넘어 자동 공유된다는 주장 |
| 5c | module call, composition, output reference, provider passing | Root가 child outputs를 sibling inputs로 연결하는 flat composition | Child implementation resource를 parent가 직접 참조할 수 있다는 주장 |
| 5d | registry version constraint, Git ref, upgrade review | `init -upgrade`, changelog, plan을 통한 module upgrade | `.terraform.lock.hcl`이 remote module selection까지 잠근다는 주장 |

**실습 연결:** [Lab 05](/labs/05-modules/)에서 local child address와 contract, [Lab 11](/labs/11-registry-modules/)에서 registry version selection을 확인합니다.

**Recall:** Child module에 provider requirement를 선언하면서 credential/region configuration은 root가 소유해야 하는 이유를 재사용성과 alias 전달 관점에서 설명하세요.

### Domain 6. Terraform state management

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 6a | local backend, local state file, local locking | Default state location과 single-user limitation | Local backend가 shared network collaboration을 자동 제공한다는 주장 |
| 6b | state writer coordination, lock timeout, force unlock | Lock이 방지하는 race와 해결하지 않는 security/API race | Locking을 encryption 또는 infrastructure transaction으로 보는 것 |
| 6c | backend block, remote state, migration, S3 `use_lockfile` | Pre-created backend와 `init -migrate-state` 흐름 | Backend block에서 variable 사용, 신규 S3에 DynamoDB locking 필수라는 주장 |
| 6d | drift, refresh-only, moved/removed/import, state commands | Binding 추가·이동·제거와 remote mutation 여부 | `state rm`이 remote object를 삭제하거나 refresh-only가 drift를 remote 수정한다는 주장 |

**실습 연결:** [Lab 06](/labs/06-remote-state/)의 local→S3 migration과 [Lab 10](/labs/10-state-operations/)의 moved/removed/import를 수행합니다.

**Recall:** Normal plan, refresh-only plan, `moved`, `removed`, `import`를 configuration/state/remote object 세 열의 표로 직접 분류하세요. `force-unlock` 전에 확인할 active writer도 말할 수 있어야 합니다.

### Domain 7. Maintain infrastructure

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 7a | import block, CLI import, generated configuration, convergence | Existing object binding 뒤 normal plan으로 configuration을 맞추는 과정 | Import가 완전하고 조직 표준인 HCL을 항상 자동 작성한다는 주장 |
| 7b | `state list/show`, `show`, `output`, mutation commands | Inspection과 binding mutation command를 분류 | `state show`가 source configuration을 출력하거나 remote object를 변경한다는 주장 |
| 7c | `TF_LOG`, `TF_LOG_PATH`, provider/backend ownership, log sensitivity | 최소 verbosity와 scope로 diagnostic을 수집하는 순서 | `TRACE`가 항상 첫 단계이거나 log가 secret을 포함하지 않는다는 주장 |

**Recall:** Provider 403과 S3 backend AccessDenied를 diagnostic phase, credential boundary, log scope로 구분하고 각각 어디를 확인할지 말하세요.

### Domain 8. HCP Terraform

| ID | 공부할 개념 | 설명할 수 있어야 함 | 구분할 함정 |
|---|---|---|---|
| 8a | CLI/VCS/API-driven remote runs, state versions, variables | Configuration ingress부터 plan/apply/state까지 managed run lifecycle | HCP가 Terraform language/provider를 대체한다는 주장 |
| 8b | teams, permissions, private registry, policy, run tasks, health | Governance, external integration, ongoing observation의 역할 | Policy/run task/health assessment를 같은 기능으로 보는 것 |
| 8c | organization, project, workspace, run history/state boundary | Project가 grouping/access를 제공하고 workspace가 state/run을 격리하는 방식 | Project 이동이 workspace state를 merge하거나 CLI workspace와 같다는 주장 |
| 8d | `terraform login`, cloud block, VCS integration, variable set, run trigger, dynamic credential | CLI-to-HCP, run-to-provider, HCP-to-VCS auth boundary | HCP login token이 target cloud permission을 자동 제공한다는 주장 |

**실습 연결:** [Lab 12](/labs/12-hcp-terraform/)에서 no-cost remote run을 수행하고 [HCP responsibility boundaries](/reference/hcp-boundaries/)의 표를 빈 종이에 재작성합니다.

**Recall:** Policy set, run task, health assessment, run trigger를 각각 “언제 실행되고 무엇을 바꾸거나 관찰하는가?”로 비교하세요. Dynamic provider credential이 static secret을 줄이지만 target cloud trust policy는 여전히 필요한 이유도 설명합니다.

## 공부 완료 판정 / Readiness gates

각 Domain은 다음 네 gate를 모두 통과할 때만 완료로 표시합니다.

1. **Explain:** Notes 없이 objective별 핵심 개념과 반대 개념을 90초 안에 설명합니다.
2. **Recognize:** Plan/diagnostic/HCL을 보고 command phase, address, action, ownership을 식별합니다.
3. **Prove:** 연결된 canonical Lab에서 expected checkpoint를 실제로 재현합니다.
4. **Correct:** 문제를 틀렸을 때 정답 문장뿐 아니라 각 distractor가 왜 틀렸는지 공식 문서 근거로 적습니다.

단순히 문제를 많이 맞혀도 Lab 결과를 설명하지 못하거나 `sensitive`, state, HCP auth boundary를 혼동하면 해당 Domain은 미완료입니다.

## High-value boundaries

### Provider, backend, module

- Provider implements resource/data types and calls target APIs.
- Backend stores state and may coordinate locking.
- Module groups configuration behind input/output contracts.

### Configuration, state, remote object

- Configuration declares desired behavior.
- State records address-to-object bindings and known attributes.
- Provider reads and changes remote objects.
- A state command can change a binding without changing the object, which affects the next plan.

### Command phases

- `fmt`: canonical source formatting
- `validate`: configuration syntax and internal consistency
- `plan`: proposed convergence using run context
- `apply`: execute a new or saved plan
- refresh-only: update recorded state/output without proposing remote mutation

Review the full [command behavior matrix](/reference/command-behavior-matrix/).

### Secret handling

- `sensitive`: redact display; value can remain in plan/state
- `ephemeral`: omit supported values from plan/state
- write-only argument: provider-defined non-persisted resource input
- Dynamic credential: short-lived target-platform authorization, separate from HCP login

Review [Terraform 1.12 deep dive](/reference/terraform-1-12-deep-dive/) and [HCP boundaries](/reference/hcp-boundaries/).

## Final seven-day loop

| Day | Work |
|---|---|
| 1 | Domains 1-3 recall, Lab 01, related questions |
| 2 | Domain 4 values/types, Labs 02-04, configuration questions |
| 3 | Domain 4 lifecycle/conditions, Labs 07-09 |
| 4 | Domain 5, Labs 05/11, module questions |
| 5 | Domains 6-7, Labs 06/10, state and maintain questions |
| 6 | Domain 8, Lab 12, HCP questions |
| 7 | [24-question diagnostic](/practice/strategy/), official-source correction, rest |

## Final checklist

- [ ] Official objectives 1a-8d를 자신의 말로 설명할 수 있다.
- [ ] Provider constraint와 lock selection을 구분할 수 있다.
- [ ] Plan action과 resource address를 읽을 수 있다.
- [ ] `count` index와 `for_each` key의 state impact를 설명할 수 있다.
- [ ] Sensitive, ephemeral, write-only의 저장 차이를 설명할 수 있다.
- [ ] S3 `use_lockfile`과 deprecated DynamoDB locking을 구분한다.
- [ ] Import, moved, removed, state rm의 binding 효과를 구분한다.
- [ ] HCP workspace/project와 세 authentication boundary를 구분한다.
- [ ] 틀린 문제마다 정답뿐 아니라 distractor가 틀린 이유를 설명한다.

HashiCorp는 official content list에 domain weight나 passing score를 공개하지 않습니다. 이 checklist와 재현 가능한 Lab 결과를 readiness evidence로 사용하세요.
