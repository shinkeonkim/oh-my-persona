---
title: Lab 학습 경로 / Lab Study Path
description: Twelve canonical Terraform labs aligned to concepts, official objectives, verification checks, and exam review.
---

Lab은 명령을 복사하는 시간이 아니라 **configuration, plan, state, remote object 사이의 변화를 관찰하는 시간**입니다. 각 Lab은 개념 문서를 먼저 읽고, 실행 결과를 기록하고, cleanup을 확인하는 동일한 구조를 사용합니다.

## Lab map

| Lab | Focus | Objectives | Prerequisite |
|---|---|---|---|
| [01 First project](/labs/01-first-project/) | init, plan, apply, destroy | 2a-2d, 3a-3g | [Domains 1-3](/domains/01-iac/) |
| [02 Variables and outputs](/labs/02-variables-outputs/) | types, input, output | 4c-4e | [Configuration](/domains/04-configuration/) |
| [03 Data sources](/labs/03-data-sources/) | read vs manage, references | 4a-4b | [Configuration](/domains/04-configuration/) |
| [04 count and for_each](/labs/04-count-for-each/) | instance addresses | 4d-4f | [Configuration](/domains/04-configuration/) |
| [05 Modules](/labs/05-modules/) | root/child contracts | 5a-5c | [Modules](/domains/05-modules/) |
| [06 Remote state](/labs/06-remote-state/) | backend, migration, locking | 6a-6c | [State](/domains/06-state/) |
| [07 Lifecycle](/labs/07-lifecycle/) | replacement and protection | 4f | [Configuration](/domains/04-configuration/) |
| [08 Custom conditions](/labs/08-custom-conditions/) | validation layers | 4g | [Configuration](/domains/04-configuration/) |
| [09 Dynamic blocks](/labs/09-dynamic-blocks/) | collection-driven nested blocks | 4d-4e | [Configuration](/domains/04-configuration/) |
| [10 State operations](/labs/10-state-operations/) | inspect, move, remove, import | 6d, 7a-7c | [Maintain](/domains/07-maintain/) |
| [11 Registry modules](/labs/11-registry-modules/) | source and version | 5a, 5d | [Modules](/domains/05-modules/) |
| [12 HCP Terraform](/labs/12-hcp-terraform/) | remote runs and workspace boundary | 8a-8d | [HCP Terraform](/domains/08-hcp-terraform/) |

## Standard loop

1. **Predict:** plan이 어떤 address에 어떤 action을 제안할지 먼저 적습니다.
2. **Initialize:** `terraform init`이 backend, module, provider 중 무엇을 준비하는지 확인합니다.
3. **Validate:** `terraform fmt -check`와 `terraform validate`를 통과시킵니다.
4. **Observe:** saved plan을 만들고 `terraform show`로 action과 dependency를 읽습니다.
5. **Apply only when needed:** cloud resource가 필요한 Lab은 비용과 credential을 확인한 뒤 적용합니다.
6. **Verify:** output, state inspection, provider console 중 적절한 방법으로 결과를 확인합니다.
7. **Cleanup:** `terraform destroy` 또는 Lab별 복구 절차를 수행하고 state와 remote object를 다시 확인합니다.
8. **Explain:** 관련 objective를 문서 없이 한 문장으로 설명합니다.

:::caution[Safety]
State, plan file, `.terraform/`, credential, HCP token을 commit하지 마세요. Cloud Lab은 disposable account/project와 최소 권한을 사용하고 종료 전 비용 발생 object를 확인합니다.
:::

Standalone solution download는 [Lab downloads](/guide/labs-and-practice/)에서 Lab 01-03에만 제공합니다. Labs 04-12는 이 canonical guide와 연결된 detailed walkthrough의 code block을 사용합니다.
