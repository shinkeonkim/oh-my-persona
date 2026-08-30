---
title: Lab 12. HCP Terraform Remote Run
description: Run a no-cloud-cost Terraform configuration in HCP Terraform and distinguish service, workspace, and provider authentication boundaries.
---

| Level | Time | Objectives |
|---|---:|---|
| Advanced | 60-90 min | 8a-8d |

**Read first:** [HCP Terraform](/domains/08-hcp-terraform/), [HCP responsibility boundaries](/reference/hcp-boundaries/)

## Outcome

Cloud credential 없이 `random_pet` resource를 사용하는 CLI-driven remote run을 수행합니다. HCP workspace가 state, variables, run history, execution setting을 격리한다는 점을 확인합니다.

## Safe configuration

```hcl
terraform {
  required_version = ">= 1.12.0, < 1.13.0"

  cloud {
    organization = "YOUR_ORGANIZATION"
    workspaces {
      name = "associate-004-lab-12"
    }
  }

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}

resource "random_pet" "example" {
  length = 2
}

output "name" {
  value = random_pet.example.id
}
```

File tree는 다음과 같습니다.

```text
lab-12/
├── versions.tf
├── main.tf
└── outputs.tf
```

위 configuration을 `versions.tf`의 terraform/provider block, `main.tf`의 resource, `outputs.tf`의 output으로 나누면 review하기 쉽습니다. `random_pet`은 remote run environment에서 provider가 실행하지만 external cloud billable resource를 만들지 않습니다.

## Prepare HCP boundaries

1. 학습용 HCP Terraform organization 또는 허가된 organization을 사용합니다.
2. `associate-004-lab-12` project와 같은 이름의 workspace를 만듭니다.
3. Workspace execution mode가 remote인지 확인합니다.
4. Workspace에 static AWS/Azure/GCP access key를 추가하지 않습니다.
5. CLI token은 최소 scope와 짧은 학습 수명으로 발급합니다.

Project는 workspace를 그룹화하고 access를 적용하지만 state를 합치지 않습니다. Workspace는 configuration association, variables, state versions, run history, execution settings의 boundary입니다.

## Authenticate and run

```bash
terraform login
terraform init
terraform plan
terraform apply
```

`terraform login`은 browser token flow 또는 입력한 API token을 local credentials file에 저장할 수 있습니다. 이 token은 CLI가 HCP Terraform service와 통신하도록 인증하며 target provider credential이 아닙니다.

`terraform init`에서 cloud block의 organization/workspace를 확인합니다. Existing local state가 있다면 migration prompt source/destination을 신중히 읽습니다. 이 Lab은 새 directory이므로 빈 HCP workspace에서 시작합니다.

CLI-driven `terraform plan`의 terminal에는 remote run URL과 streamed progress가 나타나야 합니다. HCP UI에서 같은 run의 configuration version, plan summary, logs를 확인합니다.

Representative flow:

```text
Running plan in HCP Terraform...
random_pet.example: Plan to create
Plan: 1 to add, 0 to change, 0 to destroy.
```

Exact run ID와 generated pet name은 달라집니다. Apply 뒤 output과 state version에서 `random_pet.example` address를 확인합니다.

```bash
terraform state list
terraform output name
terraform plan
```

두 번째 plan은 configuration 변화가 없으면 no changes여야 합니다.

1. CLI token은 CLI-to-HCP authentication이며 provider credential이 아님을 확인합니다.
2. Local terminal에 stream되는 output과 HCP run page의 plan을 비교합니다.
3. Workspace state와 run history를 확인합니다.
4. Project를 만들고 workspace를 이동해도 state가 다른 workspace와 합쳐지지 않는지 확인합니다.

## Compare workflow types

### CLI-driven

Local terminal이 command entry point이고 HCP가 run execution/state를 관리합니다. Local directory에는 full authoritative state를 저장하지 않습니다.

### VCS-driven observation

Disposable repository를 연결할 수 있다면 pull request 또는 non-default branch에서 speculative plan을 관찰합니다. Speculative plan은 proposed change를 보여주지만 apply하지 않습니다. Default branch merge, auto-apply 설정, manual confirmation, team permission이 apply boundary를 결정합니다.

### API-driven concept

Automation은 configuration version을 upload하고 run을 생성하며 status를 poll/callback으로 처리합니다. User token을 script에 하드코딩하지 않고 service token scope와 rotation을 설계합니다. 이 Lab에서는 실제 API automation을 만들 필요가 없습니다.

## Variables and variable sets

Workspace에 Terraform variable `environment = "lab"`을 추가하고 configuration에서 input variable로 읽는 extension을 수행할 수 있습니다. Environment variable category와 Terraform variable category를 혼동하지 않습니다. Variable set을 project 또는 workspace에 연결해 reusable non-secret setting을 공유하고 precedence가 겹치지 않게 합니다.

Sensitive marking은 HCP UI/API 표시를 제한하지만 provider가 사용한 값이 state에 기록되지 않는다는 보장은 아닙니다. Dynamic provider credentials, Terraform 1.12 ephemeral/write-only support, secure state access를 별도 검토합니다.

## Extend without static secrets

Cloud provider experiment가 필요하면 long-lived access key를 workspace variable에 복사하는 방식보다 HCP Terraform의 dynamic provider credentials를 사용합니다. OIDC trust와 target-cloud role은 official provider-specific guide에 따라 별도 구성합니다.

VCS-driven workflow를 추가로 비교할 때는 이 repository가 아니라 disposable infrastructure repository를 연결하고, pull request plan과 apply approval boundary를 관찰합니다.

Dynamic provider credential extension은 target cloud에 OIDC trust와 role을 구성해야 합니다. HCP run identity 조건을 workspace/project 단위로 제한하고 least privilege role을 연결합니다. HCP CLI login token이 cloud API permission을 제공한다고 가정하지 않습니다.

## Governance observation

Organization plan에서 사용 가능한 기능만 read-only로 관찰합니다.

| Capability | 확인할 질문 |
|---|---|
| Team permissions | 누가 read/plan/apply/state/variable 권한을 갖는가? |
| Policy set | plan data를 어느 stage와 enforcement level에서 평가하는가? |
| Run task | external system이 pre/post plan/apply 중 어디서 응답하는가? |
| Health assessment | deployed workspace의 drift/continuous validation을 어떻게 표시하는가? |
| Private registry | 승인 module/provider를 어떤 scope로 배포하는가? |

Policy는 resource-local `prevent_destroy`보다 조직 범위가 넓습니다. Run task는 external integration이고 health assessment는 ongoing observation입니다. 기능 availability와 UI는 service plan/시점에 따라 바뀔 수 있으므로 책임 경계를 학습합니다.

## Run trigger experiment design

두 disposable workspace가 있다면 upstream successful apply 뒤 downstream run을 queue하는 run trigger를 관찰할 수 있습니다. Trigger는 data를 자동 전달하지 않고 하나의 atomic graph를 만들지도 않습니다. Downstream이 output을 필요로 하면 별도 data-sharing mechanism과 state access를 설계해야 합니다.

## Troubleshooting

| 증상 | 경계 | 확인 |
|---|---|---|
| unauthorized HCP request | CLI-to-HCP | `terraform login`, token scope, hostname |
| provider auth failure | run-to-target cloud | dynamic credential/OIDC role 또는 provider variables |
| workspace not found | cloud configuration | organization/name/tag mapping |
| run queued | HCP capacity/concurrency | active runs와 workspace lock |
| VCS run not triggered | HCP-to-VCS | app installation, branch/path trigger |

Log를 공유할 때 token, variable, state/output을 redaction합니다. Auth error를 해결하려고 static cloud key를 source에 추가하지 않습니다.

## Verification and cleanup

- CLI, HCP service, target provider의 세 authentication boundary를 설명합니다.
- Workspace와 project의 책임 차이를 설명합니다.
- Policy, run task, health assessment의 목적을 구분합니다.
- `terraform destroy`를 remote run으로 완료한 뒤 disposable workspace와 token을 정리합니다.

Cleanup order:

```bash
terraform plan -destroy
terraform destroy
terraform state list
```

HCP run에서 destroy 완료와 새 state version을 확인한 후 VCS connection, run trigger, workspace-specific variable/variable set attachment를 제거합니다. 그 다음 disposable workspace와 project를 삭제하고 CLI token을 revoke합니다. Workspace를 먼저 삭제해 managed resource를 orphan으로 남기지 않습니다.

완료 기준은 CLI/HCP/provider의 세 auth boundary, organization/project/workspace 계층, CLI/VCS/API workflow, policy/run task/health assessment 목적을 각각 자신의 말로 설명하는 것입니다.

**Historical note:** [Old Lab 12](/archive/labs/lab-12-hcp-terraform/readme/)의 static AWS key 절차는 사용하지 마세요.  
**Official:** [Dynamic provider credentials](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/dynamic-provider-credentials) · [CLI-driven runs](https://developer.hashicorp.com/terraform/cloud-docs/run/cli)  
**Next:** [Exam readiness](/review/exam-readiness/) · [HCP questions](/archive/practice-exams/domain-8-hcp-terraform/)
