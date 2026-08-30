---
title: 기초 문제 12선 / Foundations Bank
description: Twelve original bilingual questions for Terraform Associate 004 Domains 1-4.
---

각 문제를 먼저 답한 뒤 해설을 여세요. Multiple answer는 요구된 선택 수를 표시합니다.

Answer each question before opening its explanation. Multiple-answer items state how many options to select.

## Domain 1: Infrastructure as Code

### Q1 [1a] Declarative intent / 선언적 의도

**True or false:** A declarative Terraform configuration normally describes the desired end state rather than every API call required to reach it.

**참/거짓:** 선언적 Terraform 구성은 일반적으로 원하는 최종 상태를 기술하며, 그 상태에 도달하기 위한 모든 API 호출 순서를 직접 기술하지 않는다.

<details><summary>정답과 해설 / Answer and explanation</summary>

**True.** Terraform builds a dependency graph, compares configuration with known infrastructure, and proposes the actions needed. The configuration is not an imperative API-call script.

Terraform은 의존성 그래프를 만들고 구성과 알려진 인프라를 비교해 필요한 작업을 제안합니다. 구성은 명령형 API 호출 스크립트가 아닙니다.

[Source: Infrastructure as code](https://developer.hashicorp.com/terraform/intro/use-cases#infrastructure-as-code)

</details>

### Q2 [1a] Mutable or immutable / 변경형 또는 불변형

A team changes a machine image ID in configuration. Which approach best matches immutable infrastructure?

팀이 구성에서 머신 이미지 ID를 변경했다. 불변 인프라에 가장 부합하는 방식은?

- A. Log in and patch every existing server manually
- B. Replace servers with instances built from the new image
- C. Edit the Terraform state file to show the new image
- D. Run `terraform fmt` to update the servers

<details><summary>정답과 해설 / Answer and explanation</summary>

**B.** Immutable practice replaces an artifact instead of mutating it in place. State editing does not change remote objects, and `fmt` only formats configuration.

불변 방식은 기존 산출물을 내부에서 수정하지 않고 교체합니다. state 편집은 원격 객체를 바꾸지 않으며 `fmt`는 구성 형식만 정리합니다.

[Source: Infrastructure as code](https://developer.hashicorp.com/terraform/intro/use-cases#infrastructure-as-code)

</details>

### Q3 [1b] IaC benefits / IaC 이점

**Choose two.** Which benefits come directly from keeping infrastructure definitions in version-controlled text?

**두 개 선택.** 인프라 정의를 버전 관리되는 텍스트로 유지할 때 직접 얻는 이점은?

- A. Reviewable change history
- B. Guaranteed zero-cost infrastructure
- C. Repeatable environment creation
- D. Automatic removal of every security risk

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and C.** Versioned definitions support review, history, automation, and repeatability. IaC does not guarantee cost or security outcomes.

버전 관리된 정의는 검토, 변경 이력, 자동화, 반복성을 지원합니다. IaC 자체가 비용이나 보안 결과를 보장하지는 않습니다.

[Source: Terraform overview](https://developer.hashicorp.com/terraform/intro)

</details>

## Domain 2: Terraform's purpose

### Q4 [2a, 2b] Provider responsibility / provider 책임

Which component translates Terraform resource operations into calls to a platform API?

Terraform resource 작업을 플랫폼 API 호출로 변환하는 구성 요소는?

- A. Backend
- B. Provider plugin
- C. Child module output
- D. CLI workspace

<details><summary>정답과 해설 / Answer and explanation</summary>

**B.** Providers implement resource types and communicate with remote APIs. A backend stores state and may coordinate locking; it does not implement cloud resources.

provider는 resource type을 구현하고 원격 API와 통신합니다. backend는 state를 저장하고 잠금을 조정할 수 있지만 cloud resource를 구현하지 않습니다.

[Source: Providers](https://developer.hashicorp.com/terraform/language/providers)

</details>

### Q5 [1c, 2c] Multi-provider graph / 다중 provider 그래프

**True or false:** A single Terraform configuration can manage objects from multiple providers and infer ordering from references between them.

**참/거짓:** 하나의 Terraform 구성은 여러 provider의 객체를 관리하고 객체 간 참조로 순서를 추론할 수 있다.

<details><summary>정답과 해설 / Answer and explanation</summary>

**True.** Terraform can combine providers in one dependency graph. This is different from claiming that every object must use the same cloud or API.

Terraform은 여러 provider를 하나의 의존성 그래프에서 결합할 수 있습니다. 모든 객체가 같은 cloud나 API를 사용해야 한다는 뜻은 아닙니다.

[Source: Terraform overview](https://developer.hashicorp.com/terraform/intro)

</details>

### Q6 [2a] Provider source and version / provider 출처와 버전

Where should a module declare the provider source address and acceptable version constraints?

module은 provider source address와 허용 가능한 version constraint를 어디에 선언해야 하는가?

- A. `required_providers` inside the `terraform` block
- B. The state file's `outputs` object
- C. A `backend` block only
- D. A `.terraform.lock.hcl` file edited by hand

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** `required_providers` declares each provider's source and version constraint. Terraform generates and updates the dependency lock file; it should not replace configuration constraints.

`required_providers`가 provider 출처와 버전 제약을 선언합니다. dependency lock file은 Terraform이 생성·갱신하며 구성의 제약 선언을 대신하지 않습니다.

[Source: Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)

</details>

## Domain 3: Core workflow

### Q7 [3a, 3b] Initialization / 초기화

A configuration adds a registry module and changes its remote backend. Which command prepares the working directory for both changes?

구성에 registry module을 추가하고 remote backend를 변경했다. 두 변경을 위해 작업 디렉터리를 준비하는 명령은?

- A. `terraform init`
- B. `terraform validate`
- C. `terraform show`
- D. `terraform output`

<details><summary>정답과 해설 / Answer and explanation</summary>

**A.** `terraform init` installs modules and providers and initializes backend settings. It is safe to run repeatedly.

`terraform init`은 module과 provider를 설치하고 backend 설정을 초기화합니다. 반복 실행해도 안전합니다.

[Source: Initialize Terraform configuration](https://developer.hashicorp.com/terraform/cli/commands/init)

</details>

### Q8 [3c, 3g] Formatting and validation / 형식과 검증

**Choose two.** Which statements are correct?

**두 개 선택.** 올바른 설명은?

- A. `terraform fmt -check` can detect non-canonical formatting without rewriting files.
- B. `terraform validate` proves provider credentials can create every object.
- C. `terraform validate` checks configuration syntax and internal consistency.
- D. `terraform fmt` previews remote infrastructure changes.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and C.** Formatting and static validation operate on configuration. A plan is needed to include context such as remote APIs and run-specific variable values.

formatting과 정적 validation은 구성에 작용합니다. 원격 API와 실행별 변수 값을 포함한 검증에는 plan이 필요합니다.

[Source: `fmt`](https://developer.hashicorp.com/terraform/cli/commands/fmt) · [Source: `validate`](https://developer.hashicorp.com/terraform/cli/commands/validate)

</details>

### Q9 [3d-3f] Apply and destroy plans / apply와 destroy plan

**Choose two.** Which statements correctly describe applying and destroying infrastructure?

**두 개 선택.** 인프라 적용과 삭제를 올바르게 설명한 것은?

- A. `terraform plan -out=tfplan` followed by `terraform apply tfplan` executes the saved plan.
- B. `terraform apply` without a saved plan never creates a new plan.
- C. `terraform destroy` creates and executes a destroy plan after approval.
- D. `terraform show` deletes every object displayed in state.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and C.** Passing a saved plan file to `apply` executes that reviewed plan. Without a saved plan, `apply` creates a new plan. `terraform destroy` is a convenience form for planning destruction of all managed objects and then applying it after approval.

저장된 plan file을 `apply`에 전달하면 검토한 plan을 실행합니다. 저장 plan 없이 `apply`하면 새 plan을 만듭니다. `terraform destroy`는 관리 객체 전체의 삭제를 계획하고 승인 후 적용하는 편의 명령입니다.

[Source: Create a plan](https://developer.hashicorp.com/terraform/cli/commands/plan) · [Source: Apply](https://developer.hashicorp.com/terraform/cli/commands/apply) · [Source: Destroy](https://developer.hashicorp.com/terraform/cli/commands/destroy)

</details>

## Domain 4: Configuration

### Q10 [4a, 4c-4e] Configuration building blocks / 구성 작성 요소

**Choose three.** Which statements are correct?

**세 개 선택.** 올바른 설명은?

- A. A `data` block can read information from an existing remote object without managing its lifecycle as a resource.
- B. `var.ports["https"]` reads key `https` from a `map(number)` input variable.
- C. A `for` expression can transform one collection value into another.
- D. An `output` block supplies an input value to the root module.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A, B, and C.** Data sources read information, input variables are referenced through `var`, and expressions can transform collections. Outputs expose values; they do not provide root-module inputs.

data source는 정보를 읽고, input variable은 `var`로 참조하며, expression은 collection을 변환할 수 있습니다. output은 값을 노출하며 root module의 input을 제공하지 않습니다.

[Source: Data sources](https://developer.hashicorp.com/terraform/language/data-sources) · [Source: Input variables](https://developer.hashicorp.com/terraform/language/values/variables) · [Source: `for` expressions](https://developer.hashicorp.com/terraform/language/expressions/for)

</details>

### Q11 [4b, 4f] Implicit dependency / 암시적 의존성

Resource B uses `resource_a.example.id` in one of its arguments. Is a separate `depends_on` normally required for the same dependency?

Resource B의 인수에서 `resource_a.example.id`를 사용한다. 같은 의존성을 위해 별도 `depends_on`이 일반적으로 필요한가?

- A. Yes, every pair of resources needs `depends_on`
- B. No, the expression already creates an implicit dependency
- C. Yes, but only after the first apply
- D. No, because Terraform always creates blocks alphabetically

<details><summary>정답과 해설 / Answer and explanation</summary>

**B.** References create implicit dependencies and let Terraform infer the required ordering. Use `depends_on` for hidden dependencies Terraform cannot infer from expressions.

참조는 암시적 의존성을 만들고 Terraform이 필요한 순서를 추론하게 합니다. 표현식에서 보이지 않는 의존성에만 `depends_on`을 사용합니다.

[Source: Resource dependencies](https://developer.hashicorp.com/terraform/language/resources/behavior#resource-dependencies)

</details>

### Q12 [4g, 4h] Validation and secrets / 검증과 secret

**Choose two.** Which statements are correct?

**두 개 선택.** 올바른 설명은?

- A. Marking a value `sensitive` usually redacts it in CLI output.
- B. Marking a value `sensitive` guarantees it is never stored in state.
- C. A variable `validation` block can reject an invalid input value.
- D. A `check` block always prevents an apply from completing when its assertion fails.

<details><summary>정답과 해설 / Answer and explanation</summary>

**A and C.** `sensitive` controls display but sensitive values can still be stored in state. Input validation rejects unsuitable values. Failed `check` assertions report warnings and do not block the operation in the same way as preconditions or postconditions.

`sensitive`는 표시를 제어하지만 값은 state에 저장될 수 있습니다. input validation은 부적합한 값을 거부합니다. 실패한 `check` assertion은 경고를 보고하며 precondition/postcondition과 같은 방식으로 작업을 중단하지 않습니다.

[Source: Sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data) · [Source: Validate configuration](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)

</details>

## Score guide

- **10-12:** Explain every distractor, then continue to [Operations](/practice/operations/).
- **7-9:** Review the objective pages linked by your miss tags.
- **0-6:** Revisit [Domains 1-4](/domains/01-iac/) before retaking with shuffled notes.
