---
title: 예상 문제 200개 / 200-Question Bank
description: Canonical Terraform Associate 004 practice bank with exactly 200 explained questions across all eight official domains.
---

이 문제은행은 공식 Associate 004 목표 1a-8d에 맞춰 Domain 1-8의 예상 문제를 한곳에서 연결합니다. 총 문항 수는 각 페이지의 `### 문제 N` heading을 기준으로 검증하며 **정확히 200개**입니다.

This index connects exactly 200 explained practice questions across all eight official domains. Public practice sites informed topic coverage only; purported live-exam wording is not reproduced.

## Domain index

| Domain | Questions | Objectives | Practice page |
|---|---:|---|---|
| 1. IaC with Terraform | 20 | 1a-1c | [Start Domain 1](/archive/practice-exams/domain-1-iac-concepts/) |
| 2. Terraform fundamentals | 20 | 2a-2d | [Start Domain 2](/archive/practice-exams/domain-2-terraform-fundamentals/) |
| 3. Core workflow | 25 | 3a-3g | [Start Domain 3](/archive/practice-exams/domain-3-core-workflow/) |
| 4. Configuration | 35 | 4a-4h | [Start Domain 4](/archive/practice-exams/domain-4-configuration/) |
| 5. Modules | 25 | 5a-5d | [Start Domain 5](/archive/practice-exams/domain-5-modules/) |
| 6. State management | 30 | 6a-6d | [Start Domain 6](/archive/practice-exams/domain-6-state/) |
| 7. Maintain infrastructure | 25 | 7a-7c | [Start Domain 7](/archive/practice-exams/domain-7-maintain/) |
| 8. HCP Terraform | 20 | 8a-8d | [Start Domain 8](/archive/practice-exams/domain-8-hcp-terraform/) |
| **Total** | **200** | **1a-8d** | |

## How to use the bank

1. Domain core page를 읽고 hands-on lab을 한 번 수행합니다.
2. 해당 domain 문제를 answer disclosure를 열지 않고 풉니다.
3. 정답뿐 아니라 각 distractor가 틀린 이유를 한 문장으로 설명합니다.
4. 오래된 명령·서비스 설명은 아래 공식 기준 페이지로 역추적합니다.
5. Domain 반복 후 [24-question diagnostic](/practice/strategy/)을 시간 제한으로 풉니다.

## Verification references

- [Official objectives 1a-8d](/reference/exam-objectives/)
- [Terraform 1.12 deep dive](/reference/terraform-1-12-deep-dive/)
- [Command behavior matrix](/reference/command-behavior-matrix/)
- [HCP Terraform boundaries](/reference/hcp-boundaries/)
- [Corrections to legacy claims](/reference/corrections/)
- [Research and provenance notes](/practice/research-notes/)

## Editorial status

- Unofficial domain percentages were removed from canonical page titles.
- S3 locking questions use Terraform 1.12 `use_lockfile`; DynamoDB locking is marked deprecated.
- Volatile provider-count claims are not treated as exam facts.
- The official objective list does not publish a passing score or domain weights.
- HCP Terraform service capabilities may depend on plan and can change; responsibility boundaries are more durable than UI labels.

## Count contract

문항 수를 변경할 때는 8개 domain file의 `### 문제 N` heading 합계가 200인지 다시 확인해야 합니다. Mock exams와 24-question diagnostic은 이 숫자에 포함하지 않습니다.
