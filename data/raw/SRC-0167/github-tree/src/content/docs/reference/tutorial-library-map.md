---
title: Terraform Tutorials Library 맵 / Tutorial Library Map
description: A reproducible map of all Terraform-filtered HashiCorp tutorials, separated into exam core, extensions, and cross-product material.
---

HashiCorp Tutorials Library에서 `product=terraform` filter를 선택하면 **Terraform 자체 tutorial만** 나오는 것이 아닙니다. 현재 snapshot은 Terraform-only 174개, Terraform이 primary인 integration 24개, Terraform이 secondary tool인 cross-product tutorial 59개를 합친 **257개**입니다. 따라서 검색 결과를 전부 같은 우선순위로 읽는 방식은 Associate 004 학습에 적합하지 않습니다.

Selecting `product=terraform` does not return only standalone Terraform tutorials. The current snapshot contains **257 records**: 174 Terraform-only tutorials, 24 integrations where Terraform is the primary product, and 59 cross-product tutorials where Terraform is secondary. This page turns that catalog into a study decision system.

## Snapshot contract

`src/data/tutorial-catalog.json`은 tutorial 본문을 복제하지 않습니다. 공개 검색 index가 제공하는 title, URL, description, product tags, edition, level, read time, headings, collection metadata만 저장합니다. Normal builds use this committed artifact and do not require a network request.

| Contract | Current snapshot |
|---|---:|
| Total unique tutorials | 257 |
| Terraform-only | 174 |
| Terraform-primary, multi-product | 24 |
| Terraform-secondary, cross-product | 59 |
| Open source edition | 184 |
| HCP Terraform (`tfc`) | 42 |
| HCP product edition | 24 |
| Enterprise edition | 7 |

Refresh metadata explicitly with:

```bash
bun run tutorials:update
```

The sync rejects malformed records, duplicate slugs, missing Terraform tags, and a returned item count that differs from Algolia's reported count. A successful refresh therefore means the local artifact is internally consistent, not that every tutorial is exam-relevant.

## Seven study scopes

| Scope | Count | Read policy | Meaning |
|---|---:|---|---|
| `exam-core` | 31 | Read and practice | Directly maps to at least one Associate 004 objective |
| `supplemental` | 82 | Select by weakness | Terraform-primary production patterns or provider-specific workflows |
| `hcp-extension` | 42 | Read for Domain 8 | HCP Terraform runs, workspaces, governance, policy, registry, and integrations |
| `ecosystem-extension` | 24 | Read after core | Terraform-primary integration with Vault, Packer, Kubernetes, or SaaS tools |
| `provider-development` | 14 | Optional | Plugin Framework and provider-author workflows, not provider-consumer basics |
| `current-extension` | 5 | Version-bound appendix | Stacks, actions, or other current features outside the Terraform 1.12 baseline |
| `cross-product` | 59 | Link-only by default | Vault, Boundary, Nomad, Packer, or Consul tutorial that happens to use Terraform |

These labels are editorial routing, not HashiCorp categories. They prevent three common errors:

1. **Search-filter fallacy:** `product=terraform` does not mean “tested on Associate 004.”
2. **Edition fallacy:** an `open_source` tutorial can still be provider-development or cross-product material.
3. **Recency fallacy:** a current tutorial can describe behavior introduced after Terraform 1.12 and must not silently redefine the exam baseline.

## Start with the certification trio

Read these three pages before using the general catalog:

1. [Learning Path - Terraform Associate 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004) defines study order.
2. [Exam Content List - Terraform Associate 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004) defines scope.
3. [Sample Questions - Terraform Associate 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004) demonstrates question style, not a memorization bank.

The objective-to-tutorial and objective-to-lab links are consolidated in the [Objective-Lab-Tutorial map](/reference/objective-lab-map/).

## Core tutorial sequence

### 1. Mental model and providers

| Tutorial | Why it matters |
|---|---|
| [What is Infrastructure as Code with Terraform?](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code) | IaC intent, reviewability, repeatability, and the common workflow across services |
| [Configure Terraform providers](https://developer.hashicorp.com/terraform/tutorials/configuration-language/configure-providers) | Requirement, installation, configuration, aliases, and multiple-provider boundaries |
| [Manage Terraform versions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions) | Terraform/provider constraints and upgrade decisions |

Do not infer that provider-neutral workflow means provider-neutral configuration. Terraform Core shares a workflow, while each provider owns resource schemas, authentication, and API behavior.

### 2. Configuration language

| Cluster | Tutorials | Observation target |
|---|---|---|
| Managed vs. read-only objects | [Resources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/resource), [Data sources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/data-sources) | Lifecycle ownership, refresh, state recording, and references |
| Inputs and outputs | [Variables](https://developer.hashicorp.com/terraform/tutorials/configuration-language/variables), [Outputs](https://developer.hashicorp.com/terraform/tutorials/configuration-language/outputs) | Module interface, type constraints, validation, and value exposure |
| Dynamic values | [Expressions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/expressions), [Functions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/functions) | Evaluation and transformation, not imperative execution |
| Repeated instances | [`count`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/count), [`for_each`](https://developer.hashicorp.com/terraform/tutorials/configuration-language/for-each) | Numeric index identity vs. stable key identity |
| Dependency graph | [Dependencies](https://developer.hashicorp.com/terraform/tutorials/configuration-language/dependencies) | Implicit references first; `depends_on` only for hidden dependencies |
| Validation | [Custom conditions](https://developer.hashicorp.com/terraform/tutorials/configuration-language/custom-conditions), [Checks](https://developer.hashicorp.com/terraform/tutorials/configuration-language/checks), [Tests](https://developer.hashicorp.com/terraform/tutorials/configuration-language/test) | Variable validation, precondition, postcondition, check, and test timing |
| Secret display | [Sensitive variables](https://developer.hashicorp.com/terraform/tutorials/configuration-language/sensitive-variables) | Redaction is not storage prevention |

For Terraform 1.12, pair the sensitive tutorial with [Terraform 1.12 deep dive](/reference/terraform-1-12-deep-dive/) to distinguish `sensitive`, `ephemeral`, and provider write-only arguments.

### 3. Workflow and state

| Tutorial | Exam observation |
|---|---|
| [Create a Terraform plan](https://developer.hashicorp.com/terraform/tutorials/cli/plan) | Unknown values, action symbols, saved plans, and review before mutation |
| [Apply Terraform configuration](https://developer.hashicorp.com/terraform/tutorials/cli/apply) | Apply a reviewed plan and observe remote plus state mutation |
| [Manage resources in Terraform state](https://developer.hashicorp.com/terraform/tutorials/state/state-cli) | Inspect before mutating; distinguish address, binding, snapshot, and remote object |
| [Manage resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift) | Compare configuration, prior state, and refreshed remote reality |
| [Manage resource lifecycle](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle) | Replacement order, destroy protection, ignored changes, and explicit replacement triggers |
| [Use configuration to move resources](https://developer.hashicorp.com/terraform/tutorials/configuration-language/move-config) | Preserve object identity while changing addresses |
| [Import Terraform configuration](https://developer.hashicorp.com/terraform/tutorials/state/state-import) | Add a binding, then converge configuration with the imported object |
| [Troubleshoot Terraform](https://developer.hashicorp.com/terraform/tutorials/configuration-language/troubleshooting-workflow) | Diagnose Core, provider, backend, module, and API failures at the correct boundary |

The live library has no single exam-core tutorial mapped directly to objectives 3a, 3b, 3f, 3g, 6a, 6b, or 6c in this catalog contract. Those objectives are covered by versioned docs and Labs 01 and 06; absence from the tutorial list is not permission to skip them.

### 4. Modules

Read in contract order:

1. [Modules overview](https://developer.hashicorp.com/terraform/tutorials/modules/module): root and child module boundaries.
2. [Build and use a local module](https://developer.hashicorp.com/terraform/tutorials/modules/module-create): input, implementation, and output ownership.
3. [Use registry modules in configuration](https://developer.hashicorp.com/terraform/tutorials/modules/module-use): source address, version constraint, and registry selection.
4. [Customize modules with object attributes](https://developer.hashicorp.com/terraform/tutorials/modules/module-object-attributes): typed object interfaces and optional attributes.

Module versions are not provider selections. `.terraform.lock.hcl` records provider selections; registry module constraints live in the module call, and downloaded module metadata is generated under `.terraform/modules/`.

## Supplemental families

### Provider-specific get-started tracks

AWS, Azure, Google Cloud, OCI, and Docker tracks repeat the same conceptual sequence with different provider schemas:

```text
install -> authenticate -> init -> create -> change -> output -> destroy
```

Choose one executable track, then compare another track at the configuration level. Re-running every provider track has diminishing exam value. Extract the durable pattern and note what changes: credentials, provider source, resource arguments, remote API, cost, and cleanup.

### HCP Terraform

Use HCP-focused tutorials for Domain 8 after mastering local workflow and state. Organize them by responsibility:

| Responsibility | Tutorial family | Questions to answer |
|---|---|---|
| Workspace creation | `cloud-sign-up`, `cloud-create-vcs-workspace`, `cloud-create-project` | What belongs to organization, project, and workspace? |
| Runs | `cloud-change`, `cloud-destroy`, `cloud-refresh-only` | Where does execution occur and when is state written? |
| Variables | `cloud-multiple-variable-sets` | Terraform variable vs. environment variable vs. variable set? |
| Collaboration | `cloud-permissions`, `cloud-run-triggers` | Who can plan/apply and how do dependent workspaces coordinate? |
| Governance | `cloud-run-tasks-*`, Sentinel tutorials, drift tutorials | Native policy evaluation vs. external run task vs. health assessment? |
| Migration | `cloud-migrate`, `migrate-remote-s3-backend-hcp-terraform` | Which state is source, which is destination, and how is rollback handled? |

HCP Terraform current behavior changes faster than Terraform 1.12 language behavior. For an exam claim, verify the certification page first; for production, use current HCP documentation.

### Provider development

The 14 Plugin Framework tutorials teach how to implement provider schemas, CRUD operations, import, functions, tests, logging, documentation, and releases. They are valuable for provider authors but are not a substitute for objective 2b, which asks how a Terraform user configures and uses providers.

### Ecosystem and cross-product tutorials

Use these after the core path when the integration itself is your learning goal:

| Primary product | Typical Terraform role | Default Associate policy |
|---|---|---|
| Vault | Configure auth engines, policies, dynamic credentials, or Terraform secrets engine | Read only for objective 4h or credential-boundary context |
| Boundary | Provision scopes, targets, roles, workers, and session-recording infrastructure | Link-only |
| Nomad | Provision clusters and supporting cloud infrastructure | Link-only |
| Packer | Connect image pipelines and HCP Packer metadata to Terraform | Optional production extension |
| Consul | Provision clusters or configure Terraform Sync | Link-only |

Terraform appearing in a tutorial does not make the primary product's architecture part of the Associate exam.

## Current-version boundary

The catalog marks Stacks, actions, and query-oriented tutorials as `current-extension`. They belong in a current-product appendix because their semantics may postdate the Terraform 1.12 exam baseline.

Before promoting a current feature into a Domain explanation, answer all four questions:

1. Is it documented in `v1.12.x`?
2. Does the Associate 004 Exam Content List name or imply it?
3. Is it a replacement for a 1.12 behavior, or an additional workflow?
4. Will presenting it inline create a false answer for an exam scenario?

If any answer is uncertain, keep it in an explicitly versioned appendix.

## Coverage decision rubric

| Decision | Use when | Local treatment |
|---|---|---|
| Include deeply | Direct objective mapping and durable 1.12 behavior | Domain explanation, executable Lab, recall check, practice question |
| Summarize | Useful production pattern but not necessary for objective mastery | Reference section with source links and boundaries |
| Add optional Lab | Behavior requires observation and has safe prerequisites | Provider-specific or HCP extension Lab with cost and cleanup |
| Link only | Cross-product, enterprise-only, duplicated provider track, or high-cost workflow | Catalog metadata and one-sentence relevance note |
| Exclude from exam claims | Current-only feature or provider-author implementation detail | Versioned appendix; never use as the sole basis for an Associate answer |

## Maintenance rules

1. Run `bun run tutorials:update` only when intentionally refreshing research evidence.
2. Review changes in total count, edition distribution, URL, collection, and headings before accepting the artifact.
3. A new tutorial starts as supplemental or cross-product until an objective mapping is reviewed.
4. Never copy tutorial prose wholesale. Write an original explanation, cite the canonical URL, and preserve the source license boundary.
5. Keep Terraform 1.12 facts in versioned docs even when a current tutorial presents a newer workflow.
6. Update the [Objective-Lab-Tutorial map](/reference/objective-lab-map/) when a core mapping changes.

**Primary catalog:** [Terraform Tutorials Library](https://developer.hashicorp.com/tutorials/library?product=terraform)  
**Local metadata artifact:** `src/data/tutorial-catalog.json`  
**Normalization contract:** `scripts/tutorial-catalog.mjs`
