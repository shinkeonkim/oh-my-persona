---
title: 학습 순서 / Learning Path
description: A prerequisite-driven route through every Terraform Associate 004 domain.
---

공식 학습 경로는 난이도 순서를 권장합니다. 이 사이트는 각 개념을 Lab과 시험 대비 자료에 연결해 **읽기만 하고 끝나는 경로**를 없앱니다.

The official path recommends studying in increasing order of complexity. This route makes each prerequisite explicit.

## Stage 1. 선언과 실행 모델 / Declaration and execution model

1. [IaC와 Terraform / IaC and Terraform](/domains/01-iac/): 선언적 목표 상태, 변경 이력, 반복 가능성을 이해합니다.
2. [Terraform 기초 / Fundamentals](/domains/02-fundamentals/): provider가 구성과 API 사이를 연결하고 state가 객체를 추적하는 이유를 이해합니다.
3. [핵심 워크플로우 / Core workflow](/domains/03-workflow/): `write → init → plan → apply`에서 각 단계가 앞 단계의 산출물을 어떻게 소비하는지 확인합니다.

**Checkpoint:** 빈 디렉터리에서 provider를 고정하고, plan을 설명한 뒤, apply와 destroy를 안전하게 수행할 수 있어야 합니다.

**Labs:** [01 First project](/labs/01-first-project/)

## Stage 2. 구성 언어와 재사용 / Language and reuse

4. [Terraform 구성 / Configuration](/domains/04-configuration/): block, expression, type, dependency, validation, sensitive data를 하나의 데이터 흐름으로 읽습니다.
5. [모듈 / Modules](/domains/05-modules/): root/child module 경계, input/output 계약, source/version 제약을 적용합니다.

**Checkpoint:** 반복 가능한 child module을 만들고 호출자가 provider configuration을 전달하도록 설계할 수 있어야 합니다.

**Labs:** [02 Variables/outputs](/labs/02-variables-outputs/), [03 Data sources](/labs/03-data-sources/), [04 count/for_each](/labs/04-count-for-each/), [05 Modules](/labs/05-modules/), [07 Lifecycle](/labs/07-lifecycle/), [08 Conditions](/labs/08-custom-conditions/), [09 Dynamic blocks](/labs/09-dynamic-blocks/), [11 Registry modules](/labs/11-registry-modules/)

## Stage 3. 지속적인 운영 / Ongoing operation

6. [상태 관리 / State management](/domains/06-state/): backend, locking, drift, refresh-only, `moved`, `removed`를 구성과 실제 객체의 정합성 문제로 이해합니다.
7. [인프라 유지보수 / Maintain infrastructure](/domains/07-maintain/): import, state inspection, verbose logging으로 기존 환경과 장애를 다룹니다.
8. [HCP Terraform](/domains/08-hcp-terraform/): 로컬 워크플로우를 원격 실행, 협업, 거버넌스, workspace/project 구조로 확장합니다.

**Checkpoint:** state를 직접 편집하지 않고 리팩터링, import, drift 처리, 원격 실행을 설명할 수 있어야 합니다.

**Labs:** [06 Remote state](/labs/06-remote-state/), [10 State operations](/labs/10-state-operations/), [12 HCP Terraform](/labs/12-hcp-terraform/)

## Stage 4. 시험 대비 정리 / Exam review

1. [시험 준비 checklist](/review/exam-readiness/)에서 objective별 설명 가능 여부를 점검합니다.
2. [Command behavior matrix](/reference/command-behavior-matrix/)로 읽기와 side effect를 구분합니다.
3. [Terraform 1.12 심화](/reference/terraform-1-12-deep-dive/)와 [HCP 경계](/reference/hcp-boundaries/)를 복습합니다.
4. [교정 노트](/reference/corrections/)에서 오래된 자료와 현재 기준의 차이를 확인합니다.

## Stage 5. 문제 풀이 / Practice questions

1. [200-question bank](/practice/bank-200/)를 domain별로 풉니다.
2. 오답은 `BOUNDARY`, `PHASE`, `STATE`, `ADDRESS`, `SECRET`, `HCP`로 분류합니다.
3. 마지막에 [24-question diagnostic](/practice/strategy/)을 시간 제한으로 풉니다.

## 반복 루프 / Study loop

1. **개념 / Learn:** domain 핵심 페이지를 읽습니다.
2. **Lab / Observe:** 연결된 Lab에서 plan과 state 변화를 기록합니다.
3. **공식 확인 / Verify:** Lab의 관련 문서와 versioned 1.12 링크를 확인합니다.
4. **회상 / Recall:** 문서를 닫고 목표와 결과를 자신의 말로 설명합니다.
5. **문제 / Test:** domain 문제를 풀고 오답의 공식 근거를 찾습니다.

Do not use a mock score as proof of mastery. Explain the behavior, reproduce it in a disposable lab, and identify the official source that defines it.
