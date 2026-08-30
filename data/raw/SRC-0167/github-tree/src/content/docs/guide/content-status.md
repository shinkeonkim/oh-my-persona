---
title: 현재 자료 상태 / Content Status
description: Current completion status for canonical concepts, labs, review pages, and question banks.
---

과거 project report의 `진행 중 / 확장 가능` 표시는 2026-07-20 당시 snapshot이며 현재 상태가 아닙니다. 현재 학습 경로는 아래 canonical 자료를 기준으로 합니다.

The old “in progress / expandable” project reports are historical snapshots, not the current roadmap.

## Canonical coverage

| Area | Current status | Canonical entry |
|---|---|---|
| 시작과 학습 순서 | Complete | [Learning path](/guide/learning-path/) |
| Domain 1-8 개념 | Complete | [Domain 1](/domains/01-iac/) |
| Lab 01-12 companion guides | Complete | [Lab index](/labs/) |
| Standalone downloadable solutions | Labs 01-03 | [Downloads](/guide/labs-and-practice/) |
| 시험 대비 정리 | Complete | [Exam readiness](/review/exam-readiness/) |
| Canonical domain question bank | 200 questions | [200-question bank](/practice/bank-200/) |
| Original diagnostic | 24 questions | [Practice strategy](/practice/strategy/) |
| Official source traceability | 23 pinned Terraform 1.12 paths | [Official sources](/reference/official-sources/) |

## Lab completion definition

Lab이 complete라는 뜻은 다음 조건을 충족한다는 의미입니다.

- 선행 개념과 official objective가 명시되어 있습니다.
- 실행할 observation과 예상 판단 기준이 있습니다.
- 성공 여부를 확인하는 명령과 cleanup 단계가 있습니다.
- 관련 concept, review, question page로 돌아가는 링크가 있습니다.
- credential이나 state를 repository에 commit하지 않는 안전 규칙이 있습니다.

Labs 04-12는 별도 solution directory 대신 canonical page의 단계와 historical detailed walkthrough를 사용합니다. Download artifact가 없는 것을 미완성으로 표시하지 않습니다.

## Historical material

- 과거 project status/completion report는 현재 navigation과 search에서 제외합니다.
- 불완전한 Mock Set 2/3 template은 canonical practice 자료가 아닙니다.
- Historical Lab walkthrough는 상세 참고 자료이며 canonical Lab page가 최신 기준과 안전 경계를 우선합니다.
- Canonical 200-question bank와 24-question diagnostic만 현재 문제 풀이 경로에 포함됩니다.

## Maintenance rule

새 자료는 반드시 다섯 단계 중 하나에 연결해야 합니다: **시작, 개념, Lab, 시험 정리, 문제 풀이**. 연결할 위치가 없는 문서는 sidebar에 추가하지 않고 reference 또는 historical archive로 분류합니다.
