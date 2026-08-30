---
title: 08. HCP Terraform
description: "Objectives 8a-8d: remote execution, collaboration, governance, workspaces, projects, and integrations."
---

## Local workflow, managed execution

HCP Terraform keeps the Terraform workflow while centralizing state, runs, credentials, collaboration, and governance. A workspace is an execution and state boundary; a project groups workspaces for organization and access control.

HCP Terraform은 Terraform 언어를 대체하지 않습니다. It provides a managed operating environment around plans and applies.

## 8a. Create infrastructure

```hcl
terraform {
  cloud {
    organization = "example-org"

    workspaces {
      name = "production-network"
    }
  }
}
```

Know CLI-driven, VCS-driven, and API-driven workflows. Runs can execute remotely with workspace variables and dynamic provider credentials rather than long-lived local credentials.

## 8b. Collaboration and governance

| Capability | Purpose |
|---|---|
| Teams and permissions | 최소 권한과 승인 경계 / access and approval boundaries |
| Private registry | 조직 module/provider 공유 / governed reuse |
| Policy enforcement | plan을 정책으로 평가 / evaluate plans against policy |
| Health assessments | drift and continuous validation signals |
| Explorer/change requests | cross-workspace visibility and coordinated changes |

Features and plan availability evolve; distinguish exam concepts from current subscription details.

## 8c. Workspaces and projects

- **Workspace:** configuration association, state, variables, run history, execution settings.
- **Project:** related workspace grouping and access boundary.
- **Run trigger:** upstream workspace completion can queue a downstream run.
- **Variable set:** reusable variables attached across workspace/project scope.

CLI workspaces and HCP Terraform workspaces share a name but are not interchangeable concepts. CLI workspaces are multiple state instances for one working directory; HCP workspaces are full managed execution units.

## 8d. Integration

`terraform login` obtains an API token, `cloud` configuration connects the working directory, and migration moves state into HCP Terraform. VCS integrations trigger runs from repository changes; dynamic credentials avoid storing long-lived cloud secrets.

## Organization, project, workspace 계층

| 계층 | 주요 책임 | 포함/격리 관계 |
|---|---|---|
| Organization | 사용자, team, global settings, registry, policy 범위 | 여러 project와 workspace 포함 |
| Project | 관련 workspace grouping과 access boundary | Workspace state를 합치지 않음 |
| Workspace | configuration association, variables, state, runs, execution settings | 독립 state/run boundary |

Workspace를 “resource 하나” 또는 “CLI workspace와 같은 것”으로 보지 않습니다. HCP workspace는 run history, state versions, variables, permissions, VCS association을 포함하는 managed execution unit입니다. Project로 workspace를 이동해도 state가 다른 workspace와 merge되지 않습니다.

## Run lifecycle을 따라가기

```text
Configuration ingress
  -> queue
  -> plan
  -> cost/policy/run-task checks
  -> confirmation or auto-apply decision
  -> apply
  -> state version and outputs
```

Run은 workspace execution mode와 workflow에 따라 remote agent, HCP-hosted environment 또는 local execution과 연결됩니다. 시험에서는 UI button 위치보다 plan과 apply가 어디서 실행되고 누가 승인하며 state/variables/credentials가 어느 boundary에 있는지를 구분해야 합니다.

### CLI-driven

`terraform plan`/`apply`를 local terminal에서 시작하지만 `cloud` block과 workspace 설정에 따라 remote execution이 일어납니다. Terminal은 run stream을 보여줍니다. CLI token은 HCP Terraform API/service 인증이며 target cloud credential과 다릅니다.

### VCS-driven

Repository branch와 workspace를 연결하고 commit/pull request가 run을 queue합니다. Speculative plan은 제안 변경을 검토하지만 apply하지 않습니다. Production apply는 branch, permission, policy, confirmation 설정을 따릅니다.

### API-driven

Automation이 configuration version과 run을 API로 생성합니다. API token scope, upload artifact, run status 처리를 명시적으로 설계해야 합니다.

## 세 authentication boundary

1. **User/CLI to HCP Terraform:** `terraform login` token, team token, API token.
2. **HCP run to target provider:** AWS/Azure/GCP 등 provider credential 또는 dynamic credential.
3. **HCP Terraform to VCS/integration:** OAuth app, GitHub App, run task callback 등 별도 trust.

한 boundary의 login이 다른 boundary의 권한을 자동 제공하지 않습니다. Dynamic provider credentials는 OIDC trust를 통해 run마다 short-lived credential을 발급해 static access key 저장을 줄입니다. Target cloud의 trust policy, project/workspace identifier 조건, least privilege role은 별도로 구성해야 합니다.

## Variable과 variable set

Workspace variable은 Terraform variable과 environment variable category를 구분합니다. Sensitive 표시를 사용해 UI/API 노출을 제한할 수 있지만 target system으로 전달된 값과 state persistence는 Terraform/provider schema에 따라 달라집니다. Variable set은 여러 workspace 또는 project에 공통 값을 연결해 중복을 줄입니다.

Priority와 scope가 겹치면 어떤 value가 최종 적용되는지 HCP Terraform variable precedence 문서를 확인합니다. 같은 key를 여러 set/workspace에 무분별하게 정의하면 run context를 이해하기 어렵습니다. Credential은 가능하면 dynamic 방식으로 대체합니다.

## Collaboration과 governance

### Teams and permissions

Organization/team/project/workspace scope에서 read, plan, write, admin 같은 permission boundary를 설계합니다. Apply 권한과 variable/state read 권한을 최소화하고 service account token을 개인 token과 구분합니다.

### Private registry

Organization이 승인한 module/provider version을 검색하고 재사용하는 distribution boundary입니다. Registry가 module quality를 자동 보장하는 것은 아니며 versioning, tests, documentation, deprecation process가 필요합니다.

### Policy enforcement

Sentinel 또는 OPA policy set은 plan data를 평가해 advisory, mandatory 등 configured enforcement를 적용합니다. `prevent_destroy` 같은 resource-local lifecycle과 조직 전체 governance policy는 범위가 다릅니다.

### Run tasks

External system이 `pre_plan`, `post_plan`, `pre_apply`, `post_apply` stage에서 security, cost, compliance 검사를 수행하도록 연결합니다. Advisory와 mandatory enforcement를 구분하며 HMAC verification과 callback availability를 설계해야 합니다.

### Health assessments

Drift detection과 continuous validation 결과를 workspace health로 제공합니다. Policy enforcement가 run 진행을 통제하는 것과, health assessment가 deployed state의 변화를 관찰하는 것은 목적이 다릅니다.

## Cross-workspace data와 run trigger

`terraform_remote_state` 또는 HCP Terraform data sharing은 다른 state output을 읽는 coupling을 만듭니다. Output만 읽더라도 underlying state access와 sensitivity를 검토합니다. Run trigger는 source workspace의 successful apply 뒤 downstream workspace run을 queue해 dependency workflow를 만들지만 resource-level graph처럼 하나의 atomic transaction을 제공하지 않습니다.

## Migration과 cleanup

CLI configuration에 `cloud` block을 추가하고 `terraform init`을 실행하면 local/기존 state를 HCP workspace로 migration하는 prompt가 나타날 수 있습니다. Source와 destination workspace를 확인하고 backup/versioning을 준비합니다. Migration 뒤 state version, resource address, normal plan을 확인합니다.

Disposable workspace cleanup 순서는 managed resource destroy run, state/output 확인, VCS/run trigger/variable set 연결 해제, token 폐기, workspace 삭제입니다. Workspace를 먼저 삭제해 managed resource를 orphan으로 남기지 않습니다.

## 시험 함정 / Exam traps

- HCP Terraform은 Terraform language/provider를 대체하지 않고 workflow를 관리합니다.
- Project는 workspace를 그룹화하지만 state와 run history를 합치지 않습니다.
- CLI token과 provider credential은 별개입니다.
- Run trigger는 upstream output 값을 자동 전달하는 data source가 아닙니다.
- Policy, run task, health assessment는 각각 governance, external integration, ongoing observation 목적입니다.
- Service plan별 제공 기능은 바뀔 수 있으므로 durable responsibility boundary를 우선 학습합니다.

## 스스로 설명하기 / Recall checks

- Organization/project/workspace를 access, grouping, state/run 책임으로 구분할 수 있는가?
- CLI-driven, VCS-driven, API-driven run에서 configuration ingress가 어떻게 다른가?
- Dynamic provider credential이 제거하는 static secret과 여전히 필요한 trust policy를 설명할 수 있는가?
- Policy enforcement, run task, health assessment의 실행 시점과 목적을 비교할 수 있는가?
- Workspace migration과 삭제 시 state와 managed resource를 orphan으로 만들지 않는 순서를 설명할 수 있는가?

## 종합 확인 / Final checkpoint

You should now be able to trace one change from HCL expression, through graph and plan, through provider execution, into state, and finally into an HCP Terraform run and governance decision.

**Official sources:** [HCP Terraform](https://developer.hashicorp.com/terraform/cloud-docs), [Workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces), [Projects](https://developer.hashicorp.com/terraform/cloud-docs/projects), [CLI integration](https://developer.hashicorp.com/terraform/cli/v1.12.x/cloud)<br />
**Lab:** [Lab 12 HCP Terraform](/labs/12-hcp-terraform/)<br />
**Review:** [HCP responsibility boundaries](/reference/hcp-boundaries/)<br />
**Questions:** [Domain 8 bank](/archive/practice-exams/domain-8-hcp-terraform/)
