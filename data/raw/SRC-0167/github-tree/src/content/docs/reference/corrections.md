---
title: 교정 노트 / Corrections
description: Material corrections discovered while aligning the prior guide with official Terraform 1.12 sources.
---

## 반드시 우선 적용 / High-priority corrections

### S3 state locking

기존 자료의 “S3 backend는 DynamoDB가 있어야 잠금 가능”이라는 설명은 현재 1.12 기준으로 오래되었습니다. S3 backend는 `use_lockfile = true`를 지원하며, **DynamoDB-based locking is deprecated**입니다.

The previous claim that S3 requires DynamoDB for locking is outdated for Terraform 1.12. The S3 backend supports `use_lockfile = true`, while **DynamoDB-based locking is deprecated**.

Source: [S3 backend state locking](https://developer.hashicorp.com/terraform/language/v1.12.x/backend/s3#state-locking)

```hcl
terraform {
  backend "s3" {
    bucket       = "example-terraform-state"
    key          = "production/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }
}
```

### Domain weights and passing score

기존 자료의 6%, 10%, 16%, 26% 같은 도메인 가중치와 “약 70% 합격”은 공식 004 Exam Content List에 근거가 없습니다. 학습 우선순위는 목표 수와 개인 취약도에 따라 정하되, 공식 수치처럼 사용하지 않습니다.

The prior domain percentages and an estimated 70% passing score are not stated in the official 004 Exam Content List. Use them neither as official facts nor as guarantees.

### Pass-probability claims

“이 자료만으로 80% 이상 합격 가능”과 같은 확률은 검증할 수 없습니다. 사이트는 점수 보장이 아니라 목표별 설명, 실습 재현, 공식 근거 확인을 완료 기준으로 사용합니다.

Claims such as an 80% chance of passing cannot be substantiated. Completion means explaining each objective, reproducing relevant behavior, and citing the official source.

## Version-sensitive notes

| Topic | Exam baseline | Study rule |
|---|---|---|
| Terraform behavior | 1.12 | Prefer `/v1.12.x/` docs for exam decisions |
| `terraform taint` | Deprecated | Prefer `terraform apply -replace=...` |
| `terraform refresh` | Deprecated | Prefer `terraform apply -refresh-only` |
| Sensitive values | May still be stored in state | `sensitive` mainly redacts UI/CLI; use ephemeral/write-only features where supported and secure state |
| HCP Terraform features | Service evolves continuously | Learn objectives 8a-8d, then verify current UI separately |

## 편집 원칙 / Editorial rule

보관 문서와 핵심 페이지가 충돌하면 핵심 페이지와 연결된 공식 소스를 우선합니다. Archive pages are historical study notes; official-source core pages take precedence.
