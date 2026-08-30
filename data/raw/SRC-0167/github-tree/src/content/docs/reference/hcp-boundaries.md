---
title: HCP Terraform 책임 경계 / HCP Boundaries
description: Distinguish HCP Terraform workspaces, projects, run methods, credentials, policies, run tasks, and health assessments.
---

HCP Terraform 문제는 기능 이름보다 **어떤 경계를 소유하는가**를 묻는 경우가 많습니다.

## Organization, project, workspace

| Object | Primary responsibility | Does not do |
|---|---|---|
| Organization | Top-level users, teams, shared settings, governance | Merge all workspace state |
| Project | Group workspaces and apply scoped access/settings | Act as one Terraform state |
| Workspace | Configuration relationship, variables, runs, state, history | Equal a CLI workspace |
| CLI workspace | Multiple state instances for one local configuration | Provide HCP collaboration features |

HCP workspace는 state와 run의 isolation boundary입니다. Project가 여러 workspace를 그룹화해도 각 workspace의 state는 독립적입니다.

**Official sources:** [Workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces), [Projects](https://developer.hashicorp.com/terraform/cloud-docs/projects)

## Run methods

| Method | Configuration arrives through | Typical trigger |
|---|---|---|
| VCS-driven | Connected repository and working directory | Commit or pull request event |
| CLI-driven | `terraform` CLI uploads configuration | User runs plan/apply locally |
| API-driven | HCP Terraform API | External automation creates a run |

모든 방식에서 remote execution을 사용한다면 plan/apply는 HCP Terraform run environment에서 수행됩니다. “CLI-driven”은 infrastructure API call이 반드시 local machine에서 실행된다는 뜻이 아닙니다.

## Three authentication boundaries

1. **User/CLI to HCP Terraform:** `terraform login`으로 얻은 token 등이 HCP Terraform service 요청을 인증합니다.
2. **HCP Terraform to VCS/integration:** VCS connection이나 integration credential이 source 또는 external service 접근을 인증합니다.
3. **Terraform provider to target platform:** AWS, Azure, GCP 등 provider credential이 managed API operation을 인증합니다.

하나의 login이 나머지 경계의 권한을 자동으로 부여하지 않습니다. Dynamic provider credentials는 run별 short-lived credential을 발급해 long-lived static secret 의존성을 줄이지만 target platform authorization 자체를 없애지는 않습니다.

**Official sources:** [CLI login](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/login), [Dynamic provider credentials](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/dynamic-provider-credentials)

## Variables and variable sets

- Terraform variable: configuration의 declared input에 값을 제공합니다.
- Environment variable: provider SDK, CLI, shell process가 읽는 execution environment 값을 제공합니다.
- Variable set: 여러 workspace에 공통 variable을 재사용하고 scope를 관리합니다.
- Sensitive marking: UI 표시와 access를 제한하지만 secret lifecycle 전체를 자동 해결하지 않습니다.

Variable precedence와 scope는 source와 workspace 설정에 따라 달라질 수 있으므로 같은 key를 여러 source에서 중복 정의하지 않는 운영 규칙이 중요합니다.

## Governance capabilities

| Capability | Question it answers | Run-blocking behavior |
|---|---|---|
| Sentinel/OPA policy | “This proposed change complies with policy?” | Enforcement setting can block |
| Run task | “Should an external system inspect or act at this run stage?” | Advisory or mandatory |
| Cost estimation | “What cost change is estimated?” | Information used by later review/policy |
| Health assessment | “Has drift or continuous validation failure appeared?” | Monitoring signal, not a normal plan approval |
| Team permissions | “Who may read, plan, apply, or administer?” | Authorization before actions |

Run task는 `pre_plan`, `post_plan`, `pre_apply`, `post_apply` 같은 lifecycle stage에서 external service와 통합할 수 있습니다. Policy set은 workspace나 project scope에 적용할 수 있으며 Sentinel 또는 OPA framework를 사용할 수 있습니다. 사용 가능한 기능과 enforcement는 service plan에 따라 달라질 수 있습니다.

**Official sources:** [Policy enforcement](https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement), [Run tasks](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-tasks), [Health assessments](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/health), [Teams](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/permissions)

## Fast classification

- State or run isolation: workspace
- Grouping and scoped administration: project
- Human/service access to HCP: token and team permissions
- Cloud API access: provider credentials
- Rule evaluation: policy
- External lifecycle integration: run task
- Drift and validation monitoring: health assessment
