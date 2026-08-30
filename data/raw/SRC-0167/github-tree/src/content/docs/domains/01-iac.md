---
title: 01. IaC와 Terraform / IaC with Terraform
description: "Objectives 1a-1c: IaC meaning, advantages, and service-agnostic workflows."
---

## 핵심 모델 / Core model

**IaC (Infrastructure as Code)**는 인프라의 목표 상태를 사람이 검토하고 기계가 실행할 수 있는 코드로 관리하는 방식입니다. Terraform 구성은 절차를 나열하기보다 결과를 선언하고, Terraform은 현재 상태와 비교해 변경 계획을 만듭니다.

IaC manages desired infrastructure state as reviewable, machine-executable code. Terraform primarily declares outcomes, compares them with known current state, and proposes the changes needed to converge.

## 1a. What IaC is

- 구성은 version control에서 검토하고 변경 이력을 남길 수 있습니다.
- 같은 입력과 버전 제약으로 환경을 반복 생성할 수 있습니다.
- 코드 자체가 자동화 가능한 운영 문서가 됩니다.

Configuration can be reviewed and versioned, environments can be reproduced from controlled inputs, and the code becomes executable operational documentation.

## 1b. Why IaC patterns help

| Pattern | 이점 / Benefit |
|---|---|
| Declarative configuration | 구현 세부보다 목표 상태에 집중 / focuses on desired state |
| Plan before apply | 변경 영향 검토 / review impact before mutation |
| Reusable modules | 반복과 편차 감소 / reduce repetition and variance |
| Versioned workflow | 감사, 협업, 롤백 판단 / audit and collaboration trail |

:::caution
IaC는 자동으로 idempotency, 보안, 무중단을 보장하지 않습니다. Provider behavior, lifecycle, state, credentials, and review practices still determine safety.
:::

## 1c. Multi-cloud and service-agnostic workflow

Terraform Core는 provider plugin을 통해 서로 다른 API를 동일한 workflow로 다룹니다. 구성 언어와 `init → plan → apply`는 공통이지만, 각 provider의 resource schema와 인증 방식은 다릅니다.

Terraform Core uses provider plugins to apply a common workflow across APIs. The language and workflow are shared; resource schemas, authentication, and remote behavior remain provider-specific.

## 선언적 조정 모델 / Declarative reconciliation model

Terraform을 이해할 때 가장 중요한 질문은 “어떤 명령을 차례로 실행하는가?”가 아니라 “구성, 이전 state, 원격 객체를 비교했을 때 어떤 차이가 있는가?”입니다. Configuration은 **desired state**, state snapshot은 Terraform이 마지막으로 알고 있던 **known state**, provider가 읽은 API 결과는 **observed remote state** 역할을 합니다. `terraform plan`은 이 세 정보를 조합해 create, update, replace, destroy 또는 no-op을 제안합니다.

이 과정은 일반적인 imperative script와 다릅니다. Script는 `create`, `wait`, `update` 같은 절차를 작성자가 결정하지만, Terraform 구성은 resource 사이의 reference를 통해 dependency graph를 만들고 Terraform Core가 실행 순서를 계산합니다. 다만 declarative라는 말이 “항상 무중단”, “항상 같은 API 호출”, “실패하지 않음”을 뜻하지는 않습니다. 실제 동작은 provider schema, API 제약, lifecycle 설정과 현재 state에 따라 달라집니다.

```text
Configuration + Previous State + Provider Read
                    |
                    v
             Proposed Plan
                    |
             review and approve
                    v
        Remote Changes + New State
```

## IaC가 만드는 운영 능력 / Operational capabilities

| 능력 | 실제 의미 | 보장하지 않는 것 |
|---|---|---|
| Reproducibility | 같은 module과 통제된 input으로 환경을 반복 구성 | 외부 API와 이미지가 영원히 동일함 |
| Version control | 변경 이유, reviewer, diff를 Git에 기록 | `git revert`만으로 이미 삭제된 객체가 자동 복구됨 |
| Automation | plan/apply를 CI 또는 remote run에 연결 | 승인·권한·비용 통제가 자동으로 올바름 |
| Consistency | module과 policy로 조직 표준을 재사용 | 모든 환경이 완전히 동일해야 함 |
| Auditability | configuration과 run 결과를 추적 | state에 secret이 절대 저장되지 않음 |

**Idempotency**는 같은 목표 상태에 반복 수렴한다는 성질입니다. 두 번째 plan이 보통 no changes를 보이는 이유이지만 provider의 시간 의존 data source, 외부 변경(drift), 비결정적 input이 있으면 새로운 차이가 나타날 수 있습니다. 따라서 “Terraform은 언제나 같은 결과를 만든다”보다 “현재 관측값을 목표 상태와 다시 비교한다”가 정확합니다.

## Terraform이 service-agnostic한 방식

Terraform Core는 HCL parsing, graph, plan, state coordination을 담당하고 provider plugin은 특정 API의 resource와 data source schema를 제공합니다. AWS resource와 GitHub repository를 한 configuration에 둘 수 있는 이유는 모든 서비스가 같아서가 아니라, 각 provider가 Terraform protocol에 맞춰 다른 API 동작을 구현하기 때문입니다.

- **Provider requirement**는 module이 필요한 provider source와 허용 version을 선언합니다.
- **Provider configuration**은 region, endpoint, alias처럼 한 실행에서 사용할 설정을 제공합니다.
- **Resource**는 Terraform이 lifecycle을 관리할 객체입니다.
- **Data source**는 provider를 통해 기존 정보를 읽되 그 객체의 lifecycle을 소유하지 않습니다.
- **Backend**는 provider와 별개로 state 저장과 선택적 locking을 담당합니다.

Multi-cloud는 하나의 configuration에서 여러 provider를 사용할 수 있다는 의미이지 cloud 간 자동 migration이나 공통 resource schema를 의미하지 않습니다. 각 provider의 인증, quota, retry, replacement behavior를 따로 이해해야 합니다.

## 시험에서 자주 섞이는 경계 / Exam boundaries

1. **Declarative vs imperative:** 목표 상태를 선언하는 것과 모든 API 순서를 직접 작성하는 것을 구분합니다.
2. **Provisioning vs configuration management:** Terraform도 provisioner를 제공하지만 일반적인 주 역할은 API 기반 infrastructure lifecycle입니다. 이미 생성된 서버 내부 package 설정은 별도의 configuration-management 도구가 더 적합할 수 있습니다.
3. **Immutable pattern vs lifecycle guarantee:** replacement 중심 설계를 지원할 수 있지만 모든 resource update가 자동 replacement되는 것은 provider schema가 결정합니다.
4. **Plan review vs rollback:** plan은 미래 변경을 검토하는 artifact입니다. 과거 infrastructure를 자동 복원하는 rollback snapshot이 아닙니다.
5. **State vs inventory:** state는 단순 목록이 아니라 Terraform address와 remote object identity의 binding을 포함합니다.

## 스스로 설명하기 / Recall checks

- Configuration, state, remote API 결과가 plan에서 어떤 역할을 하는지 한 문장씩 설명할 수 있는가?
- IaC가 reviewability를 높이는 이유와 보안을 자동 보장하지 않는 이유를 함께 말할 수 있는가?
- Terraform Core, provider, backend의 책임을 서로 바꾸지 않고 설명할 수 있는가?
- Multi-provider graph가 가능하다는 것과 provider별 schema가 다르다는 사실을 동시에 설명할 수 있는가?
- 두 번째 plan에 change가 나타나는 가능한 원인을 drift, input, data source 관점에서 세 가지 제시할 수 있는가?

## 다음 연결 / Why next

IaC의 선언을 실행하려면 누가 API를 호출하고 무엇이 이미 존재하는지 알아야 합니다. 그래서 다음은 [provider와 state](/domains/02-fundamentals/)입니다.

**Official sources:** [Terraform intro v1.12](https://developer.hashicorp.com/terraform/intro/v1.12.x), [Use cases](https://developer.hashicorp.com/terraform/intro/v1.12.x/use-cases)<br />
**Lab:** [Lab 01 First project](/labs/01-first-project/)<br />
**Questions:** [Domain 1 bank](/archive/practice-exams/domain-1-iac-concepts/)
