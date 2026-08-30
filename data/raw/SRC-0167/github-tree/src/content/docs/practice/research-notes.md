---
title: 문제 자료 조사 노트 / Practice Research Notes
description: Provenance, contradictions, and topic signals used to design original Terraform Associate 004 practice questions.
---

## 수집 원칙 / Collection policy

공식 문서는 사실과 시험 범위의 기준입니다. 공개 문제·덤프 사이트는 **주제 빈도와 오답 패턴만** 수집하며, 실제 시험 문제라고 주장하는 문장과 선택지는 복제하지 않습니다.

Official documentation defines facts and scope. Public practice and dump sites contribute **topic and misconception signals only**; purported live-exam wording and answer choices are not reproduced.

## Source tiers

| Tier | Sources | Allowed use |
|---|---|---|
| Primary | [Official objectives](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004), [learning path](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004), [sample questions](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004), Terraform 1.12 docs | Facts, objective IDs, supported question types, answer explanations |
| Official source | [`web-unified-docs` v1.12](https://github.com/hashicorp/web-unified-docs/tree/main/content/terraform/v1.12.x) | Source-level traceability through `bun run sources:update` |
| Original practice | [Tech Exam Lexicon](https://techexamlexicon.com/hashicorp/terraform-associate-004/sample-questions/), [Mastery Exam Prep](https://masteryexamprep.com/exams/hashicorp/terraform-associate-004/), [Bryan Krausen](https://krausen.io/course/hashicorp-certified-terraform-associate-004-practice-exams/) | Scenario structure, explanation depth, misconception taxonomy |
| Community study | [KodeKloud notes](https://notes.kodekloud.com/docs/HashiCorp-Certified-Terraform-Associate-004/Course-Introduction/Whats-New-in-the-Terraform-Associate-004-Exam/page), [public GitHub prep map](https://github.com/sonukkushwaha0801/Terraform-associate-004-exam-prep), [004 prep article](https://mnourdine.com/blogs/day-24-final-exam-preparation-terraform-associate-004-practice-and-tips) | Coverage gap discovery; claims must be checked against primary sources |
| Dump signal | [ExamTopics 004 index](https://www.examtopics.com/exams/hashicorp/terraform-associate-004/) | Domain labels and recurring concept signals only; no question or answer copying |

## Confirmed format

HashiCorp's official sample page demonstrates three item types:

- True or false
- Multiple choice with one correct answer
- Multiple answer with the required number of selections stated

공식 샘플은 문제가 함정을 위한 철자·사소한 세부가 아니라 Terraform 지식을 검증한다고 명시합니다. 새 문제도 모호한 말장난 대신 책임 경계와 실행 결과를 묻습니다.

## Cross-source topic signals

| Misconception cluster | Why it deserves practice | Objectives |
|---|---|---|
| Provider vs backend vs module | Public practice repeatedly tests noun and responsibility boundaries | 2a-2d, 5a-5d, 6a-6c |
| `fmt` / `validate` / `plan` / `apply` | Learners confuse syntax checks, remote API checks, proposed actions, and mutation | 3a-3g |
| Variable types and references | Official samples directly test map access and variable loading | 4b-4e |
| State, locking, drift, import | Public sources consistently emphasize safe shared-state decisions | 2d, 6a-6d, 7a-7b |
| `moved` / `removed` / refresh-only | Older material often recommends imperative or deprecated alternatives | 6d |
| Implicit dependencies and lifecycle | 004 adds explicit emphasis on dependency and replacement decisions | 4f |
| Validation and checks | Preconditions/postconditions abort in different phases; checks are non-blocking diagnostics | 4g |
| Sensitive, ephemeral, Vault | `sensitive` redacts output but does not itself prevent state storage | 4h |
| HCP workspace vs project | Workspace is a state/run boundary; project groups workspaces without merging state | 8a, 8c |
| HCP auth and governance | CLI token, provider credentials, dynamic credentials, policies, and health solve different problems | 8b, 8d |

## Contradictions closed

### Unofficial weights

Public sites publish incompatible domain percentages. The official 004 content list publishes no percentages. This question bank therefore covers every objective and does not label any external weighting as official.

### Passing score and readiness percentage

Public sites use different passing-score and readiness estimates. HashiCorp does not publish a passing score on the official objective or sample pages. Readiness here means being able to explain and reproduce behavior, not reaching an invented guarantee.

### Live-exam dumps

Some sites label material “actual exam questions.” Such wording is not independently verifiable and may breach exam terms or copyright. The pages in this site contain newly written stems, distractors, and explanations based on official concepts.

## Research date

Sources were accessed on 2026-08-02. Current HCP Terraform service features may change after this date; exam decisions should use the version and objective pages linked above.
