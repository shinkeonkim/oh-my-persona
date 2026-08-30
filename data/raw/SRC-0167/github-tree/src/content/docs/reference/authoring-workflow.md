---
title: 자료 생성 워크플로우 / Authoring Workflow
description: A repeatable process for extending bilingual content from official versioned sources.
---

## 원칙 / Principle

공식 문서를 그대로 복제하지 않고, **시험 목표 → versioned source → 실행 가능한 예제 → 한영 설명 → 검증 질문**의 흐름으로 학습 자료를 작성합니다.

Do not blindly republish official documentation. Author each lesson as **objective → versioned source → executable example → Korean-English explanation → verification question**.

## 1. 공식 소스 고정 / Pin official sources

```bash
bun run sources:update
```

This resolves the current `web-unified-docs` commit and checks the curated Terraform 1.12 paths in `src/data/official-source-index.json`. Use `repositoryUrl` for an immutable source view and `developerUrl` for the rendered official documentation.

## 2. 목표 선택 / Select an objective

[공식 목표 1a-8d](/reference/exam-objectives/)에서 한 개의 검증 가능한 목표를 선택합니다. 한 페이지가 너무 많은 목표를 섞으면 prerequisite와 오답 원인을 추적하기 어렵습니다.

Select one testable objective from the [official objective map](/reference/exam-objectives/). Keep prerequisites and failure modes explicit.

## 3. 한영 병기 구조 / Bilingual structure

1. 한국어로 mental model과 오해하기 쉬운 경계를 설명합니다.
2. English canonical terms and the concise official behavior follow immediately.
3. 명령, block name, argument는 번역하지 않고 backtick으로 표시합니다.
4. 처음 등장하는 용어는 `상태 잠금 (state locking)`처럼 병기합니다.

English is not decorative translation. It preserves the vocabulary used in the exam, CLI diagnostics, and official documentation.

## 4. 예제와 반례 / Example and counterexample

- 최소 예제는 한 개의 행동만 증명해야 합니다.
- Include expected plan/state consequences, not only syntax.
- deprecated 방식은 현재 대안과 함께 명확히 표시합니다.
- Secret, account ID, bucket name, and credentials must be fictional and non-sensitive.

## 5. 근거 표시 / Cite evidence

페이지 마지막에 다음을 연결합니다.

- Official objective or learning-path page
- Versioned Terraform 1.12 documentation
- SHA-pinned `web-unified-docs` source when source-level traceability helps
- Related lab and archive detail

## 6. 검증 / Verify

```bash
bun run build
bun run preview
```

Check the page at 375px and desktop width, verify every internal link, run the example in a disposable environment when feasible, and update [corrections](/reference/corrections/) when an archived statement changes.

## Definition of done

- 목표 ID와 prerequisite가 명확합니다.
- Korean explanation and English canonical terminology are adjacent.
- At least one official primary source is linked.
- Version-sensitive behavior names Terraform 1.12 or the relevant version.
- 예제가 실제 동작과 state/plan 결과를 설명합니다.
- 페이지가 production search index와 sidebar에서 발견됩니다.
