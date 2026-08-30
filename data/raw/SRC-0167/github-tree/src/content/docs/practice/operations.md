---
title: 운영 문제 12선 / Operations Bank
description: Twelve original bilingual questions for Terraform Associate 004 Domains 5-8.
---

각 문제를 먼저 답한 뒤 해설을 여세요. Multiple answer는 요구된 선택 수를 표시합니다.

Answer each question before opening its explanation. Multiple-answer items state how many options to select.

## Domain 5: Modules

### Q13 [5b, 5c] Module interface / module 인터페이스

Which pair forms the clearest public interface of a reusable module?

재사용 가능한 module의 공개 interface를 가장 잘 구성하는 쌍은?

- A. Input variables and output values
- B. State locks and provider binaries
- C. Backend credentials and `.terraform` cache
- D. CLI history and log files

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** Variables accept values from callers and outputs expose selected results. Resources and local values remain implementation details unless referenced through that interface.

variable은 caller의 값을 받고 output은 선택된 결과를 노출합니다. resource와 local value는 이 interface를 통해 노출하지 않는 한 구현 세부 사항입니다.

[Source: Module composition](https://developer.hashicorp.com/terraform/language/modules/develop/composition)

</details>

### Q14 [5a] Module source change / module source 변경

After changing a module's `source` argument, which command should be run before planning?

module의 `source` 인수를 변경한 뒤 plan 전에 실행할 명령은?

- A. `terraform init`
- B. `terraform state rm`
- C. `terraform force-unlock`
- D. `terraform output`

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** Initialization retrieves and installs modules. Terraform does not automatically notice and install a newly changed module source during every other command.

초기화는 module을 가져와 설치합니다. 다른 모든 명령이 변경된 module source를 자동 설치하는 것은 아닙니다.

[Source: Modules command](https://developer.hashicorp.com/terraform/cli/commands/get)

</details>

### Q15 [5d] Module version / module 버전

**True or false:** The `version` argument for a module call is supported for registry modules, but not for a module loaded from a local filesystem path.

**참/거짓:** module call의 `version` 인수는 registry module에 지원되지만 local filesystem path에서 불러온 module에는 적용되지 않는다.

<details><summary>정답과 해설 / Answer and explanation</summary>

**True.** Registry sources support version constraints. Other source types use their own mechanisms, such as a Git `ref`; local paths directly use local files.

registry source는 version constraint를 지원합니다. 다른 source type은 Git `ref` 같은 자체 메커니즘을 사용하고 local path는 local file을 직접 사용합니다.

[Source: Module sources](https://developer.hashicorp.com/terraform/language/modules/sources)

</details>

## Domain 6: State

### Q16 [2d, 6a] Local state and bindings / local state와 binding

Which statement correctly describes the default local backend and Terraform state?

기본 local backend와 Terraform state를 올바르게 설명한 것은?

- A. It stores state on the local filesystem, including bindings from resource addresses to remote object identities.
- B. It stores state only in provider APIs and never writes a local file.
- C. It automatically provides safe multi-user locking over a shared network folder.
- D. It replaces the need for provider credentials.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** The default local backend stores state locally. State binds each managed resource instance address to a remote object and stores known attributes.

기본 local backend는 state를 local filesystem에 저장합니다. state는 관리되는 resource instance address와 remote object를 연결하고 알려진 attribute를 저장합니다.

[Source: Local backend](https://developer.hashicorp.com/terraform/language/backend/local) · [Source: State purpose](https://developer.hashicorp.com/terraform/language/state/purpose)

</details>

### Q17 [6b, 6c] Shared state / 공유 state

**Choose two.** Which are typical advantages of an appropriately configured remote backend for a team?

**두 개 선택.** 적절히 구성된 remote backend가 팀에 제공하는 일반적인 이점은?

- A. Shared access to the current state snapshot
- B. State locking when the backend supports it
- C. Automatic correction of every manual cloud change
- D. Elimination of provider authentication

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and B.** Remote state centralizes the snapshot, and supported backends can coordinate locking. Drift still requires detection and a deliberate reconciliation decision; providers still need credentials.

remote state는 snapshot을 중앙화하고 지원되는 backend는 locking을 조정할 수 있습니다. drift는 여전히 탐지와 의도적인 조정이 필요하고 provider에도 credential이 필요합니다.

[Source: Backends](https://developer.hashicorp.com/terraform/language/backend)

</details>

### Q18 [6d] State reconciliation / state 조정

**Choose two.** Which mechanisms support safe state reconciliation?

**두 개 선택.** 안전한 state 조정을 지원하는 메커니즘은?

- A. Use a `moved` block when renaming a resource address while retaining the same remote object.
- B. Delete the state file whenever drift appears.
- C. Use refresh-only mode to review and record out-of-band remote changes without modifying remote objects.
- D. Run `terraform fmt` to reconcile remote object drift.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and C.** A `moved` block updates an address binding during refactoring. Refresh-only mode proposes state and output updates based on remote changes without proposing remote-object changes.

`moved` block은 refactor 과정의 address binding을 갱신합니다. refresh-only mode는 remote change에 따른 state와 output 갱신을 제안하되 remote object 변경은 제안하지 않습니다.

[Source: `moved` block](https://developer.hashicorp.com/terraform/language/moved) · [Source: Refresh-only mode](https://developer.hashicorp.com/terraform/cli/commands/plan#refresh-only-mode)

</details>

## Domain 7: Maintain state and configuration

### Q19 [7a] Import behavior / import 동작

**True or false:** Importing an existing remote object automatically generates a complete, organization-approved resource configuration in every Terraform workflow.

**참/거짓:** 기존 remote object를 import하면 모든 Terraform workflow에서 완전하고 조직 표준에 맞는 resource configuration이 자동 생성된다.

<details><summary>정답과 해설 / Answer and explanation</summary>

**False.** Import primarily establishes a state binding. Configuration must exist or be generated and then reviewed; generated configuration is not guaranteed to match organizational intent.

import의 핵심은 state binding을 설정하는 것입니다. 구성은 존재하거나 생성된 뒤 검토해야 하며 생성된 구성이 조직의 의도와 일치한다고 보장되지 않습니다.

[Source: Import existing resources](https://developer.hashicorp.com/terraform/language/import)

</details>

### Q20 [7b] Inspect state / State 조회

**Choose two.** Which commands inspect state without changing remote objects?

**두 개 선택.** remote object를 변경하지 않고 state를 검사하는 명령은?

- A. `terraform state list`
- B. `terraform state show ADDRESS`
- C. `terraform state rm ADDRESS`
- D. `terraform apply -replace=ADDRESS`

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and B.** `state list` lists resource instances in state, and `state show` displays attributes for one state address. `state rm` changes bindings, while `apply -replace` can change remote infrastructure.

`state list`는 state의 resource instance를 나열하고 `state show`는 특정 address의 attribute를 표시합니다. `state rm`은 binding을 변경하고 `apply -replace`는 remote infrastructure를 변경할 수 있습니다.

[Source: Inspect state](https://developer.hashicorp.com/terraform/cli/commands/state)

</details>

### Q21 [7c] Verbose logging / 상세 logging

Which temporary environment-variable setting enables the most verbose Terraform core logs for troubleshooting?

문제 해결을 위해 가장 상세한 Terraform core log를 임시로 활성화하는 환경 변수 설정은?

- A. `TF_LOG=TRACE`
- B. `TF_INPUT=TRACE`
- C. `TF_STATE=VERBOSE`
- D. `TF_PLAN=DEBUG_ONLY`

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** `TF_LOG` accepts log levels including `TRACE`, the most verbose. `TF_LOG_PATH` can persist logs when logging is enabled. Disable verbose logging after diagnosis because logs can expose sensitive values.

`TF_LOG`는 가장 상세한 `TRACE`를 포함한 log level을 받습니다. logging이 활성화된 상태에서 `TF_LOG_PATH`로 파일에 저장할 수 있습니다. log에 민감한 값이 노출될 수 있으므로 진단 후 비활성화합니다.

[Source: Debugging Terraform](https://developer.hashicorp.com/terraform/internals/debugging)

</details>

## Domain 8: HCP Terraform

### Q22 [8a, 8c] Workspace boundary / workspace 경계

What does an HCP Terraform workspace primarily isolate?

HCP Terraform workspace가 주로 격리하는 것은?

- A. A state, configuration association, variables, and run history
- B. One individual resource inside a shared state
- C. A provider binary for the entire organization
- D. A single input variable shared by all projects

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** HCP Terraform uses workspaces as distinct run and state boundaries for creating infrastructure, with their own configuration relationship, variables, and history. Projects group workspaces but do not merge their states.

workspace는 자체 configuration 관계, variable, history를 가진 독립적인 run·state 경계입니다. project는 workspace를 그룹화하지만 state를 합치지 않습니다.

[Source: HCP Terraform workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)

</details>

### Q23 [8d] Authentication boundaries / 인증 경계

**Choose two.** Which statements correctly separate authentication responsibilities?

**두 개 선택.** 인증 책임을 올바르게 구분한 설명은?

- A. A Terraform CLI token authenticates the CLI to HCP Terraform.
- B. A cloud provider credential authorizes all HCP Terraform organization API calls.
- C. Provider credentials authenticate provider operations to the target platform.
- D. Logging in to HCP Terraform automatically grants every cloud permission.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and C.** HCP Terraform authentication and target-provider authentication are separate boundaries. Dynamic provider credentials can reduce static secrets, but still represent authorization to the target platform.

HCP Terraform 인증과 target provider 인증은 별도 경계입니다. dynamic provider credential은 static secret을 줄일 수 있지만 여전히 target platform에 대한 권한을 나타냅니다.

[Source: CLI login](https://developer.hashicorp.com/terraform/cli/commands/login) · [Source: Dynamic provider credentials](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/dynamic-provider-credentials)

</details>

### Q24 [8b] Governance and health / 거버넌스와 상태

Which HCP Terraform capability evaluates policy rules against a run before infrastructure changes proceed?

인프라 변경이 진행되기 전 run에 정책 규칙을 평가하는 HCP Terraform 기능은?

- A. Policy enforcement with Sentinel or OPA
- B. Workspace health assessment
- C. The local provider plugin cache
- D. `terraform fmt`

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** Policy enforcement evaluates governance rules in the run lifecycle. Health assessments detect drift and continuous-validation status; they serve a different purpose.

policy enforcement는 run lifecycle에서 governance rule을 평가합니다. health assessment는 drift와 continuous validation 상태를 탐지하므로 목적이 다릅니다.

[Source: Policy enforcement](https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement) · [Source: Health assessments](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/health)

</details>

## Score guide

- **10-12:** Re-run only missed questions after explaining why each distractor is wrong.
- **7-9:** Review [State](/domains/06-state/), [Maintain](/domains/07-maintain/), and [HCP Terraform](/domains/08-hcp-terraform/).
- **0-6:** Repeat the hands-on labs before using a timed attempt.
