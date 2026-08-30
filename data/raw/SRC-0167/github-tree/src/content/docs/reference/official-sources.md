---
title: 공식 자료 맵 / Official Source Map
description: Source-of-truth hierarchy and version-pinned Terraform 1.12 documentation map.
---

## 자료 우선순위 / Source hierarchy

1. **시험 목표 / Exam scope:** Associate 004 Exam Content List
2. **학습 순서 / Study order:** Associate 004 Learning Path
3. **시험 기준 동작 / Versioned behavior:** Terraform `v1.12.x` documentation
4. **현재 제품 동작 / Current behavior:** current Terraform and HCP Terraform docs
5. **이 사이트의 설명 / This site's explanation:** bilingual synthesis and labs

시험 문제를 판단할 때 최신 버전의 기능과 1.12의 기능이 다르면 **시험 기준인 1.12**를 우선합니다. 실제 업무에서는 현재 배포 버전의 문서를 사용하세요.

For exam questions, prefer versioned 1.12 documentation when current behavior differs. For production work, use documentation matching the deployed Terraform version.

## 핵심 링크 / Core links

| Purpose | HashiCorp Developer | `web-unified-docs` v1.12 source |
|---|---|---|
| Learning path | [Associate study 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004) | Tutorial content is served separately from the versioned core docs |
| Objectives | [Associate review 004](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004) | Use the published objective page as primary source |
| Tutorial catalog | [Terraform-filtered Tutorials Library](https://developer.hashicorp.com/tutorials/library?product=terraform) | Metadata snapshot: `src/data/tutorial-catalog.json` |
| Terraform intro | [What is Terraform?](https://developer.hashicorp.com/terraform/intro/v1.12.x) | [`docs/intro/index.mdx`](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.12.x/docs/intro/index.mdx) |
| Core workflow | [Core workflow](https://developer.hashicorp.com/terraform/intro/v1.12.x/core-workflow) | [`docs/intro/core-workflow.mdx`](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.12.x/docs/intro/core-workflow.mdx) |
| CLI | [Terraform CLI](https://developer.hashicorp.com/terraform/cli/v1.12.x) | [`docs/cli`](https://github.com/hashicorp/web-unified-docs/tree/main/content/terraform/v1.12.x/docs/cli) |
| Language | [Configuration language](https://developer.hashicorp.com/terraform/language/v1.12.x) | [`docs/language`](https://github.com/hashicorp/web-unified-docs/tree/main/content/terraform/v1.12.x/docs/language) |
| State | [Terraform state](https://developer.hashicorp.com/terraform/language/v1.12.x/state) | [`docs/language/state`](https://github.com/hashicorp/web-unified-docs/tree/main/content/terraform/v1.12.x/docs/language/state) |
| Debugging | [Debugging Terraform](https://developer.hashicorp.com/terraform/internals/v1.12.x/debugging) | [`docs/internals/debugging.mdx`](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.12.x/docs/internals/debugging.mdx) |

## 라이선스와 사용 방식 / License and usage

`web-unified-docs`는 Business Source License 1.1과 Additional Use Grant를 사용합니다. 이 프로젝트는 공식 문서를 통째로 재배포하지 않고, 개인 학습용 요약·인용·링크와 소스 인덱스를 유지합니다. 원문을 직접 복제하거나 외부에 호스팅하기 전에 저장소의 최신 `LICENSE`를 확인하세요.

The repository uses Business Source License 1.1 with an Additional Use Grant. This project keeps summaries, citations, links, and an index rather than republishing the complete official corpus. Review the current repository license before copying or hosting original content.

## 두 개의 source artifact / Two source artifacts

| Artifact | Refresh command | Authority |
|---|---|---|
| `src/data/official-source-index.json` | `bun run sources:update` | Immutable commit-pinned Terraform `v1.12.x` documentation paths |
| `src/data/tutorial-catalog.json` | `bun run tutorials:update` | Current Tutorials Library discovery metadata and local study-scope classification |

The first artifact answers “what did Terraform 1.12 document?” The second answers “what tutorials are currently discoverable under the Terraform product filter?” A current tutorial never overrides versioned 1.12 behavior for an exam claim.

The tutorial snapshot contains metadata and links rather than tutorial bodies. See the [Tutorial Library map](/reference/tutorial-library-map/) for the 257-item taxonomy and the [Objective-Lab-Tutorial map](/reference/objective-lab-map/) for direct exam coverage.
