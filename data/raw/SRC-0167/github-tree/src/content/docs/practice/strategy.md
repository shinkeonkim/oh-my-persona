---
title: 문제 풀이 전략 / Practice Strategy
description: A source-aware diagnostic loop for using the original 24-question bilingual Terraform Associate 004 bank.
---

## 문제은행 구성 / Bank structure

- [200-question bank](/practice/bank-200/): Domains 1-8, 200 questions
- [Foundations bank](/practice/foundations/): Domains 1-4, 12 questions
- [Operations bank](/practice/operations/): Domains 5-8, 12 questions
- [Research notes](/practice/research-notes/): sources, contradictions, and ethical-use policy
- [Legacy mock exam](/archive/practice-exams/mock-exam-set-1/): migrated long-form practice material

전체 200문항은 domain별 반복 훈련에 사용하고, 새 24문제는 공식 샘플처럼 true/false, single choice, multiple answer를 혼합한 빠른 진단에 사용합니다. 실제 시험 유출 문제를 복제하지 않습니다.

Use the 200-question bank for domain repetition and the 24-question set for a quick diagnostic. The site does not reproduce leaked exam questions.

## Four-pass loop

1. **Classify:** 문제를 workflow, configuration, state, module, HCP 중 하나로 먼저 분류합니다.
2. **Predict:** 명령이나 기능이 configuration, remote object, state 중 무엇을 읽고 바꾸는지 말합니다.
3. **Answer:** 선택지의 Terraform noun과 책임 경계를 비교합니다.
4. **Verify:** 해설을 연 뒤 정답 이유와 오답 이유를 모두 설명하고 공식 링크를 확인합니다.

## 오답 태그 / Miss tags

| Tag | Diagnostic question | Next page |
|---|---|---|
| `BOUNDARY` | provider, backend, module, workspace 중 무엇의 책임인가? | [Glossary](/reference/glossary/) |
| `PHASE` | write/init/plan/apply 중 언제 일어나는가? | [Core workflow](/domains/03-workflow/) |
| `STATE` | binding, snapshot, remote object 중 무엇이 변하는가? | [State](/domains/06-state/) |
| `ADDRESS` | resource address가 이동·제거·import되는가? | [Maintain](/domains/07-maintain/) |
| `SECRET` | 표시 redaction과 저장 방지가 혼동됐는가? | [Configuration 4h](/domains/04-configuration/#4h-sensitive-data) |
| `HCP` | CLI, provider, HCP service 인증을 구분했는가? | [HCP Terraform](/domains/08-hcp-terraform/) |

## Timed use

공식 샘플 형식을 익힌 뒤 새 문제 24개를 25분 안에 풉니다. 속도보다 각 오답을 한 문장으로 설명하는 능력을 우선합니다. 같은 문제를 외워 맞힌 점수는 readiness evidence가 아닙니다.

After reviewing the official format, answer the 24 new questions in 25 minutes. Prioritize explaining each miss over score alone.
