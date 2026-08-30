---
title: "Terraform Associate (004) 예상 문제 풀이"
description: "Legacy study material imported from practice-exams/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 개요

이 디렉토리에는 HashiCorp Terraform Associate (004) 시험 대비 예상 문제가 포함되어 있습니다. 실제 시험과 유사한 형식으로 구성되었으며, 각 도메인별로 문제가 분류되어 있습니다.

## 문제 구성

### 전체 모의고사
- [모의고사 Set 1 (57문제)](/archive/practice-exams/mock-exam-set-1/) - 실전 시뮬레이션
- [모의고사 Set 2 (57문제)](/archive/practice-exams/mock-exam-set-2/) - 실전 시뮬레이션
- [모의고사 Set 3 (57문제)](/archive/practice-exams/mock-exam-set-3/) - 실전 시뮬레이션

### 도메인별 연습 문제
1. [Infrastructure as Code 개념 (6%)](/archive/practice-exams/domain-1-iac-concepts/)
2. [Terraform 기초 (10%)](/archive/practice-exams/domain-2-terraform-fundamentals/)
3. [Core Workflow (16%)](/archive/practice-exams/domain-3-core-workflow/)
4. [Terraform Configuration (26%)](/archive/practice-exams/domain-4-configuration/)
5. [Terraform Modules (10%)](/archive/practice-exams/domain-5-modules/)
6. [State Management (16%)](/archive/practice-exams/domain-6-state/)
7. [Maintain Infrastructure (10%)](/archive/practice-exams/domain-7-maintain/)
8. [HCP Terraform (6%)](/archive/practice-exams/domain-8-hcp-terraform/)

---

## 시험 준비 가이드

### 문제 유형 이해하기

HashiCorp Terraform Associate 시험은 세 가지 유형의 문제로 구성됩니다:

#### 1. True/False (참/거짓)
단일 진술에 대해 참 또는 거짓을 선택합니다.

**예제:**
```
Usernames and passwords referenced in Terraform code, even as variables, 
will end up in plain text in the state file.

⬜ True
⬜ False

답: True
설명: sensitive = true로 표시된 변수라도 State 파일에는 평문으로 저장됩니다.
State 파일 자체를 암호화하거나 안전하게 보관해야 합니다.
```

#### 2. Multiple Choice (단일 선택)
여러 옵션 중 하나의 정답을 선택합니다.

**예제:**
```
You have defined values for variables in terraform.tfvars in the same 
directory as your Terraform configuration. Which command will use those 
values when creating an execution plan?

A) terraform plan -var-file="terraform.tfvars"
B) terraform plan
C) terraform apply
D) terraform plan -input=false

답: B) terraform plan
설명: terraform.tfvars 파일은 자동으로 로드되므로 별도의 플래그가 필요없습니다.
```

#### 3. Multiple Answer (다중 선택)
여러 옵션 중 복수의 정답을 선택합니다. (선택할 개수가 명시됨)

**예제:**
```
Which Terraform commands automatically refresh the state unless supplied 
with additional flags? (Select TWO)

⬜ A) terraform plan
⬜ B) terraform state
⬜ C) terraform apply
⬜ D) terraform validate
⬜ E) terraform output

답: A, C
설명: 
- terraform plan: State를 자동으로 refresh합니다 (-refresh=false로 비활성화 가능)
- terraform apply: State를 자동으로 refresh합니다 (-refresh=false로 비활성화 가능)
- terraform validate: State에 접근하지 않음
- terraform output: State를 읽기만 하고 refresh하지 않음
```

---

## 학습 전략

### 1단계: 도메인별 학습 (Week 1-7)
각 도메인의 연습 문제를 풀며 개념 정리:
- 틀린 문제는 반드시 이유 파악
- 관련 공식 문서 재학습
- 실습을 통한 검증

### 2단계: 모의고사 (Week 8)
실전 시뮬레이션:
- **월요일**: 모의고사 Set 1 (60분 타이머)
- **화요일**: Set 1 복습 및 취약점 보완
- **수요일**: 모의고사 Set 2 (60분 타이머)
- **목요일**: Set 2 복습 및 취약점 보완
- **금요일**: 모의고사 Set 3 (60분 타이머)
- **토요일**: Set 3 복습 및 최종 정리
- **일요일**: 휴식 및 가벼운 복습

### 목표 점수
- **1차 모의고사**: 65% 이상
- **2차 모의고사**: 75% 이상
- **3차 모의고사**: 80% 이상

---

## 자주 틀리는 함정 문제

### 1. Deprecated 명령어
```
❌ terraform taint resource.name
✅ terraform apply -replace=resource.name

❌ terraform refresh
✅ terraform apply -refresh-only
```

### 2. count vs for_each
```hcl
# count: 인덱스 기반 (0, 1, 2...)
resource "aws_instance" "server" {
  count = 3
  # 접근: aws_instance.server[0], aws_instance.server[1]...
}

# for_each: 키 기반 (map 또는 set)
resource "aws_instance" "server" {
  for_each = toset(["web", "api", "db"])
  # 접근: aws_instance.server["web"], aws_instance.server["api"]...
}
```
**시험 팁**: 리소스를 중간에서 제거할 때 `for_each`가 더 안전합니다.

### 3. sensitive = true의 한계
```hcl
variable "db_password" {
  type      = string
  sensitive = true  # CLI 출력에서만 숨김
}

# ❌ State 파일에는 평문으로 저장됨
# ✅ Remote Backend + Encryption 필수
```

### 4. State Locking
```hcl
# S3 Backend만으로는 State Locking 불가능
terraform {
  backend "s3" {
    bucket         = "my-bucket"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    # ❌ 이것만으로는 Locking 안 됨
  }
}

# ✅ DynamoDB 테이블 추가 필요
terraform {
  backend "s3" {
    bucket         = "my-bucket"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"  # ✅ Locking 활성화
  }
}
```

### 5. Provider Version Constraints
```hcl
# ❌ 잘못된 버전 제약
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.0.0"  # 정확히 4.0.0만 허용 (위험!)
    }
  }
}

# ✅ 올바른 버전 제약
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"  # 4.0.x 버전 허용 (4.1.0은 불허)
    }
  }
}
```

### 6. Module Source 이해
```hcl
# Local path
module "vpc" {
  source = "./modules/vpc"
}

# Terraform Registry
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}

# GitHub
module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc"
}

# Git with specific branch
module "vpc" {
  source = "git::https://example.com/vpc.git?ref=v1.2.0"
}
```

### 7. depends_on vs 암시적 종속성
```hcl
# ✅ 암시적 종속성 (권장)
resource "aws_instance" "app" {
  subnet_id = aws_subnet.main.id  # 자동으로 의존성 생성
}

# ⚠️ 명시적 종속성 (필요한 경우만)
resource "aws_instance" "app" {
  depends_on = [
    aws_iam_role_policy.example  # 참조할 수 없지만 순서 필요
  ]
}
```

### 8. HCP Terraform 워크플로우 순서
```
❌ 잘못된 순서: Plan → Apply
❌ 잘못된 순서: Plan → Policy Check → Cost Estimation → Apply

✅ 올바른 순서: Plan → Cost Estimation → Policy Check → Apply
```

---

## 시험 팁

### DO (해야 할 것)
- ✅ 공식 문서를 1차 자료로 활용
- ✅ 실제 클라우드 환경에서 실습
- ✅ State 파일 내용 직접 확인
- ✅ 각 명령어의 동작 이해 (암기보다 이해)
- ✅ 모의고사는 실전처럼 60분 타이머 설정

### DON'T (하지 말아야 할 것)
- ❌ 단순 암기 (개념 이해 우선)
- ❌ 공식 문서 건너뛰기
- ❌ 실습 없이 이론만 학습
- ❌ 틀린 문제를 그냥 넘기기
- ❌ 모의고사를 여러 번 나눠서 풀기

---

## 추가 학습 자료

### HashiCorp 공식
- [Sample Questions (004)](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004)
- [Exam Content List](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004)
- [Learning Path](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004)

### 커뮤니티 Practice Tests
- [ExamTopics - Terraform Associate](https://www.examtopics.com/exams/hashicorp/terraform-associate/)
- [Whizlabs Practice Tests](https://www.whizlabs.com/hashicorp-certified-terraform-associate/)
- [Udemy Practice Exams](https://www.udemy.com/topic/hashicorp-certified-terraform-associate/)

---

## 문제 난이도 표시

각 문제에는 난이도가 표시되어 있습니다:

- 🟢 **Easy**: 기본 개념, 직관적인 답
- 🟡 **Medium**: 개념 응용, 비교/대조 필요
- 🔴 **Hard**: 복잡한 시나리오, 함정 가능성

---

## 피드백 및 개선

문제에 오류가 있거나 개선 사항이 있다면 Issue를 생성해주세요.

**Good luck with your exam preparation! 🎯**
