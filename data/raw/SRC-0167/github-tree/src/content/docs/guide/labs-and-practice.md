---
title: Lab 다운로드 / Lab Downloads
description: Download the reviewed Terraform example files and continue into the twelve canonical lab guides.
---

## Canonical Lab 경로

실습의 시작점은 [Lab index](/labs/)입니다. 각 canonical Lab page는 선행 개념, 단계, 검증, cleanup과 historical detailed guide를 연결합니다.

Start from the [Lab index](/labs/). Each canonical page connects prerequisites, steps, verification, cleanup, and any historical detailed walkthrough.

| Level | Labs | Guide |
|---|---|---|
| Beginner | 01 First project, 02 Variables/outputs, 03 Data sources | [Begin Lab 01](/labs/01-first-project/) |
| Intermediate | 04 `count`/`for_each`, 05 Module, 06 Remote state, 07 Lifecycle | [Begin Lab 04](/labs/04-count-for-each/) |
| Advanced | 08 Conditions, 09 Dynamic blocks, 10 State, 11 Registry, 12 HCP Terraform | [Begin Lab 08](/labs/08-custom-conditions/) |

## 다운로드 가능한 솔루션 / Downloadable solutions

현재 repository에 검토된 standalone solution file이 존재하는 Lab 01-03만 다운로드로 제공합니다. Labs 04-12는 canonical guide와 self-contained code block을 제공하며, 존재하지 않는 download를 표시하지 않습니다.

Only labs with real source solution files are listed. Labs 04-12 include guides but no complete solution directories in the source project.

### Lab 01

- [providers.tf](/lab-files/lab-01-first-project/solution/providers.tf)
- [main.tf](/lab-files/lab-01-first-project/solution/main.tf)
- [outputs.tf](/lab-files/lab-01-first-project/solution/outputs.tf)

### Lab 02

- [variables.tf](/lab-files/lab-02-variables-outputs/solution/variables.tf)
- [main.tf](/lab-files/lab-02-variables-outputs/solution/main.tf)
- [outputs.tf](/lab-files/lab-02-variables-outputs/solution/outputs.tf)
- [terraform.tfvars.example](/lab-files/lab-02-variables-outputs/solution/terraform.tfvars.example)

### Lab 03

- [providers.tf](/lab-files/lab-03-data-sources/solution/providers.tf)
- [data.tf](/lab-files/lab-03-data-sources/solution/data.tf)
- [main.tf](/lab-files/lab-03-data-sources/solution/main.tf)
- [outputs.tf](/lab-files/lab-03-data-sources/solution/outputs.tf)

## Hello world practice

`practices/terraform-hello-world`에서 안전한 구성과 dependency lock file만 공개합니다. State와 provider cache는 민감 정보와 대용량 binary가 포함될 수 있어 의도적으로 제외합니다.

Only safe configuration artifacts are published from the local hello-world practice. State and provider caches are intentionally excluded.

- [main.tf](/practice-files/terraform-hello-world/main.tf)
- [.terraform.lock.hcl](/practice-files/terraform-hello-world/.terraform.lock.hcl)
