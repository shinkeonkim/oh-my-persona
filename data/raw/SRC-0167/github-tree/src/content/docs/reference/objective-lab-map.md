---
title: Objective-Lab-Tutorial 교차 맵 / Coverage Cross-Map
description: Reverse index from all 37 Associate 004 objectives to canonical chapters, labs, official tutorials, and observable proof.
---

이 페이지는 “어떤 Lab이 어떤 objective를 다루는가?”를 반대로 찾는 index입니다. 공식 목표는 37개이며, 현재 catalog에서 27개 objective가 31개 `exam-core` tutorial에 직접 연결됩니다. Direct tutorial이 없는 10개 objective도 versioned documentation과 canonical Lab으로 학습합니다.

This reverse index maps every objective to four forms of evidence:

| Evidence | Meaning |
|---|---|
| Concept | You can explain the boundary without notes |
| Tutorial | You reviewed the official worked example and its prerequisites |
| Lab | You predicted, executed, observed, and cleaned up the behavior |
| Proof | You can point to a plan, state address, output, log, or HCP run that demonstrates the claim |

`No direct core tutorial` means the curated catalog has no tutorial assigned to that exact objective. It does **not** mean the objective is optional.

## Domain 1: Infrastructure as Code

| ID | Concept | Canonical Lab | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 1a | [IaC meaning](/domains/01-iac/) | [Lab 01](/labs/01-first-project/) reinforces declarative intent | [IaC with Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code), [Study 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004), [Review 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004), [Sample questions](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004) | Change configuration, compare the plan, and show that the declaration is reviewed before mutation |
| 1b | [IaC advantages](/domains/01-iac/) | [Lab 01](/labs/01-first-project/) | [IaC with Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code) | Re-run the same configuration and explain version control, repeatability, auditability, and idempotent no-op planning |
| 1c | [Service-agnostic workflow](/domains/01-iac/) | [Lab 01](/labs/01-first-project/), compare with [Lab 12](/labs/12-hcp-terraform/) | [IaC with Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code) | Identify which steps remain `init -> plan -> apply` and which provider schema, credentials, and API details change |

**Mastery boundary:** Terraform provides a common workflow and language. It does not make AWS, Azure, GCP, HCP, or SaaS resource schemas identical.

## Domain 2: Terraform fundamentals

| ID | Concept | Canonical Lab | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 2a | [Install and version providers](/domains/02-fundamentals/) | [Lab 01](/labs/01-first-project/) | [Configure providers](https://developer.hashicorp.com/terraform/tutorials/configuration-language/configure-providers), [Manage versions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions) | Delete `.terraform/`, run `init`, and distinguish the configured constraint from the selection in `.terraform.lock.hcl` |
| 2b | [How Terraform uses providers](/domains/02-fundamentals/) | [Lab 01](/labs/01-first-project/) | [Configure providers](https://developer.hashicorp.com/terraform/tutorials/configuration-language/configure-providers) | Point to the resource type owned by the provider and the state binding owned by Terraform Core |
| 2c | [Multiple providers](/domains/02-fundamentals/) | [Lab 01](/labs/01-first-project/) plus the alias extension in Domain 2 | [Configure providers](https://developer.hashicorp.com/terraform/tutorials/configuration-language/configure-providers) | Add an aliased provider, pass it explicitly, and explain why an alias is not a second provider requirement |
| 2d | [State use and management](/domains/02-fundamentals/) | [Lab 01](/labs/01-first-project/), deepened by [Lab 10](/labs/10-state-operations/) | [State CLI](https://developer.hashicorp.com/terraform/tutorials/state/state-cli) | Match a resource address to a remote object ID and explain why state is neither configuration nor the remote object |

**Mastery boundary:** Requirement, selected version, provider configuration, backend, and state are separate responsibilities.

## Domain 3: Core workflow

| ID | Concept | Canonical Lab | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 3a | [Workflow](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/) | No direct core tutorial; use [Core workflow v1.12](https://developer.hashicorp.com/terraform/intro/v1.12.x/core-workflow) | Draw write, init, validate, plan, apply, and destroy with each phase's inputs and outputs |
| 3b | [Initialize a directory](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/) | No direct core tutorial; use [`init` v1.12](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/init) | Explain changes under `.terraform/`, backend initialization, module download, provider installation, and lock-file behavior |
| 3c | [Validate configuration](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/), [Lab 08](/labs/08-custom-conditions/) | [Terraform tests](https://developer.hashicorp.com/terraform/tutorials/configuration-language/test), [Troubleshooting](https://developer.hashicorp.com/terraform/tutorials/configuration-language/troubleshooting-workflow) | Produce one syntax/type failure and one runtime condition failure, then name the phase that owns each diagnostic |
| 3d | [Generate and review a plan](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/) | [Create a plan](https://developer.hashicorp.com/terraform/tutorials/cli/plan) | Save `tfplan`, inspect it with `terraform show`, and explain unknown values and action symbols |
| 3e | [Apply changes](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/) | [Apply configuration](https://developer.hashicorp.com/terraform/tutorials/cli/apply) | Apply the saved plan and identify both remote-object and state changes |
| 3f | [Destroy managed infrastructure](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/) | No direct core tutorial; use [`destroy` v1.12](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/destroy) | Review a destroy plan, apply it, and explain why unmanaged objects are outside the operation |
| 3g | [Formatting and style](/domains/03-workflow/) | [Lab 01](/labs/01-first-project/) | No direct core tutorial; use [`fmt` v1.12](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/fmt) | Introduce noncanonical formatting, run `fmt -check`, then `fmt`, and distinguish style normalization from semantic validation |

**Mastery boundary:** `fmt`, `validate`, `plan`, and `apply` answer different questions. Passing an earlier phase does not guarantee a later phase will succeed.

## Domain 4: Terraform configuration

| ID | Concept | Canonical Labs | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 4a | [`resource` vs. `data`](/domains/04-configuration/) | [Lab 03](/labs/03-data-sources/) | [Resources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/resource), [Data sources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/data-sources) | Show that a resource is lifecycle-managed while a data source reads an object, even though both can expose state-recorded attributes |
| 4b | [References](/domains/04-configuration/) | [Lab 03](/labs/03-data-sources/) | [Resources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/resource), [Data sources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/data-sources), [Dependencies](https://developer.hashicorp.com/terraform/tutorials/configuration-language/dependencies), [Outputs](https://developer.hashicorp.com/terraform/tutorials/configuration-language/outputs) | Replace a literal with an attribute reference and identify the implicit graph edge |
| 4c | [Variables and outputs](/domains/04-configuration/) | [Lab 02](/labs/02-variables-outputs/) | [Variables](https://developer.hashicorp.com/terraform/tutorials/configuration-language/variables), [Outputs](https://developer.hashicorp.com/terraform/tutorials/configuration-language/outputs) | Demonstrate input precedence, a validation failure, and the output as a module interface |
| 4d | [Complex types](/domains/04-configuration/) | [Lab 02](/labs/02-variables-outputs/), [Lab 04](/labs/04-count-for-each/), [Lab 09](/labs/09-dynamic-blocks/) | [`count`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/count), [Expressions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/expressions), [`for_each`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/for-each), [Object attributes](https://developer.hashicorp.com/terraform/tutorials/modules/module-object-attributes) | Transform a `map(object(...))`, preserve key identity, and explain list, set, map, object, and tuple differences |
| 4e | [Expressions and functions](/domains/04-configuration/) | [Lab 02](/labs/02-variables-outputs/), [Lab 04](/labs/04-count-for-each/), [Lab 09](/labs/09-dynamic-blocks/) | [`count`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/count), [Expressions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/expressions), [`for_each`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/for-each), [Functions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/functions) | Use `for`, filtering, `merge`, `try`, or conversion functions and predict the resulting type before opening `terraform console` |
| 4f | [Dependencies](/domains/04-configuration/) | [Lab 04](/labs/04-count-for-each/), [Lab 07](/labs/07-lifecycle/) | [`count`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/count), [`for_each`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/for-each), [Dependencies](https://developer.hashicorp.com/terraform/tutorials/configuration-language/dependencies), [Lifecycle](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle) | Compare stable keys with numeric indexes and justify every explicit `depends_on` by naming the hidden dependency |
| 4g | [Custom conditions](/domains/04-configuration/) | [Lab 08](/labs/08-custom-conditions/) | [Tests](https://developer.hashicorp.com/terraform/tutorials/configuration-language/test), [Checks](https://developer.hashicorp.com/terraform/tutorials/configuration-language/checks), [Custom conditions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/custom-conditions) | Trigger variable validation, precondition, postcondition, and check behavior; state which failures block execution |
| 4h | [Sensitive data](/domains/04-configuration/) | No dedicated canonical Lab; use [Terraform 1.12 deep dive](/reference/terraform-1-12-deep-dive/) and [HCP Lab 12](/labs/12-hcp-terraform/) credential boundaries | [Sensitive variables](https://developer.hashicorp.com/terraform/tutorials/configuration-language/sensitive-variables) | Explain why `sensitive` redaction can coexist with state persistence and when `ephemeral`, write-only, Vault, or dynamic credentials change storage risk |

**Coverage gap:** Objective 4h has no dedicated zero-cost Lab that proves redaction, plan-file persistence, state persistence, ephemeral omission, and write-only behavior side by side. Treat this as a review priority rather than assuming Lab coverage is complete.

## Domain 5: Modules

| ID | Concept | Canonical Labs | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 5a | [Module sources](/domains/05-modules/) | [Lab 05](/labs/05-modules/), [Lab 11](/labs/11-registry-modules/) | [Modules overview](https://developer.hashicorp.com/terraform/tutorials/modules/module), [Use registry modules](https://developer.hashicorp.com/terraform/tutorials/modules/module-use) | Compare local, registry, and Git source identity and identify which mechanism controls each version |
| 5b | [Variable scope](/domains/05-modules/) | [Lab 05](/labs/05-modules/) | [Modules overview](https://developer.hashicorp.com/terraform/tutorials/modules/module), [Create a module](https://developer.hashicorp.com/terraform/tutorials/modules/module-create), [Object attributes](https://developer.hashicorp.com/terraform/tutorials/modules/module-object-attributes) | Attempt to read a parent local from a child, then pass the value through an explicit input |
| 5c | [Use modules](/domains/05-modules/) | [Lab 05](/labs/05-modules/) | [Modules overview](https://developer.hashicorp.com/terraform/tutorials/modules/module), [Create a module](https://developer.hashicorp.com/terraform/tutorials/modules/module-create), [Use registry modules](https://developer.hashicorp.com/terraform/tutorials/modules/module-use), [Object attributes](https://developer.hashicorp.com/terraform/tutorials/modules/module-object-attributes) | Reference a child output, inspect the `module.NAME.resource_type.name` address, and explain the contract boundary |
| 5d | [Module versions](/domains/05-modules/) | [Lab 11](/labs/11-registry-modules/) | [Manage versions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions), [Use registry modules](https://developer.hashicorp.com/terraform/tutorials/modules/module-use) | Change a registry constraint, run `init -upgrade`, and prove the provider lock file does not lock module versions |

**Mastery boundary:** A module call creates a namespace and explicit interface. It is not text inclusion, automatic parent-scope access, or a provider configuration inheritance guarantee.

## Domain 6: State management

| ID | Concept | Canonical Lab | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 6a | [Local backend](/domains/06-state/) | [Lab 06](/labs/06-remote-state/) phase 1 | No direct core tutorial; use [local backend v1.12](https://developer.hashicorp.com/terraform/language/v1.12.x/backend/local) | Locate local state and distinguish backend storage behavior from provider-managed object behavior |
| 6b | [State locking](/domains/06-state/) | [Lab 06](/labs/06-remote-state/) | No direct core tutorial; use [state locking v1.12](https://developer.hashicorp.com/terraform/language/v1.12.x/state/locking) | Create safe lock contention, observe retry behavior, and explain why `-lock=false` and premature `force-unlock` are dangerous |
| 6c | [Remote backend](/domains/06-state/) | [Lab 06](/labs/06-remote-state/) phase 2 | No direct core tutorial; use [backend configuration v1.12](https://developer.hashicorp.com/terraform/language/v1.12.x/backend) and [S3 backend](https://developer.hashicorp.com/terraform/language/v1.12.x/backend/s3) | Migrate local state, verify the destination, and distinguish `-migrate-state` from `-reconfigure` |
| 6d | [Drift and state operations](/domains/06-state/) | [Lab 10](/labs/10-state-operations/) | [State CLI](https://developer.hashicorp.com/terraform/tutorials/state/state-cli), [Move configuration](https://developer.hashicorp.com/terraform/tutorials/configuration-language/move-config), [Drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift), [Lifecycle](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle), [Import](https://developer.hashicorp.com/terraform/tutorials/state/state-import) | Produce a no-destroy move, a remove-without-destroy, an import binding, and a drift-only plan |

**Mastery boundary:** State locking serializes supported writes; it does not encrypt state, prevent every out-of-band change, or recover a corrupted snapshot automatically.

## Domain 7: Maintain infrastructure

| ID | Concept | Canonical Lab | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 7a | [Import](/domains/07-maintain/) | [Lab 10](/labs/10-state-operations/) | [Import configuration](https://developer.hashicorp.com/terraform/tutorials/state/state-import) | Add a binding and then make configuration converge; explain why import alone does not create a complete desired configuration |
| 7b | [Inspect state](/domains/07-maintain/) | [Lab 10](/labs/10-state-operations/) | [State CLI](https://developer.hashicorp.com/terraform/tutorials/state/state-cli), [Troubleshooting](https://developer.hashicorp.com/terraform/tutorials/configuration-language/troubleshooting-workflow) | Choose among `state list`, `state show`, `show`, `output -json`, and remote API inspection based on the question being asked |
| 7c | [Verbose logging](/domains/07-maintain/) | [Lab 10](/labs/10-state-operations/) | [Troubleshooting](https://developer.hashicorp.com/terraform/tutorials/configuration-language/troubleshooting-workflow) | Enable scoped logging, capture a file, identify secret exposure risk, then unset variables and delete the artifact |

**Mastery boundary:** Inspect first, back up before mutation, prefer configuration-driven refactoring, and treat state and debug logs as sensitive artifacts.

## Domain 8: HCP Terraform

| ID | Concept | Canonical Lab | Direct official tutorials | Observable proof |
|---|---|---|---|---|
| 8a | [Create infrastructure in HCP](/domains/08-hcp-terraform/) | [Lab 12](/labs/12-hcp-terraform/) | No direct `exam-core` mapping; use the HCP extension family in the [Tutorial Library map](/reference/tutorial-library-map/) | Start a remote run, identify where execution occurs, and prove state remains in the HCP workspace |
| 8b | [Collaboration and governance](/domains/08-hcp-terraform/) | [Lab 12](/labs/12-hcp-terraform/) governance extension | No direct `exam-core` mapping; review permission, policy, run-task, health, and registry tutorials by responsibility | Distinguish team permission, policy evaluation, external run task, health assessment, and private registry ownership |
| 8c | [Workspaces and projects](/domains/08-hcp-terraform/) | [Lab 12](/labs/12-hcp-terraform/) | No direct `exam-core` mapping; review workspace/project HCP extension tutorials | Place organization settings, project grouping, and workspace runs/state/variables at the correct hierarchy level |
| 8d | [Integration](/domains/08-hcp-terraform/) | [Lab 12](/labs/12-hcp-terraform/) | [Study 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004), [Review 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004), [Sample questions](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004) | Compare CLI-driven, VCS-driven, and API-driven runs and separate CLI-to-HCP authentication from run-to-provider authentication |

**Coverage gap:** Objectives 8a-8c have substantial HCP tutorial coverage but no item is promoted to `exam-core` automatically. HCP behavior is service-evolving, so use the official 004 scope page as the exam boundary and current HCP docs for production details.

## Ten objectives without a direct core tutorial

| Objective | Required replacement evidence |
|---|---|
| 3a | Domain 3 model + Lab 01 full loop + Core workflow v1.12 |
| 3b | Lab 01 initialization artifacts + `init` v1.12 reference |
| 3f | Lab 01 reviewed destroy plan + `destroy` v1.12 reference |
| 3g | Lab 01 `fmt -check` failure and correction + `fmt` v1.12 reference |
| 6a | Lab 06 local-state phase + local backend v1.12 reference |
| 6b | Lab 06 lock contention + state locking v1.12 reference |
| 6c | Lab 06 migration + backend and S3 v1.12 references |
| 8a | Domain 8 + Lab 12 remote run |
| 8b | Domain 8 governance matrix + Lab 12 extension |
| 8c | Domain 8 hierarchy model + Lab 12 workspace setup |

This table is a quality signal: tutorial-library completeness and exam-objective completeness are different contracts.

## How to record completion

For each objective, retain a short evidence note in this form:

```text
Objective: 6c
Prediction: init -migrate-state will copy the latest local snapshot to the configured backend.
Observed: destination state serial increased; a no-change plan followed migration.
Boundary: -reconfigure accepts backend metadata without copying state.
Cleanup: resources destroyed, state returned to intended backend, local backup removed securely.
Source: Terraform 1.12 backend docs and Lab 06.
```

An objective is complete only when you can explain the boundary, reproduce the observation, diagnose one failure, and clean up safely. Reading a tutorial without evidence is exposure, not mastery.
