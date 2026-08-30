---
title: "Terraform Associate (004) 빠른 시작 가이드"
description: "Legacy study material imported from QUICKSTART.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📌 이 가이드가 제공하는 것

이 학습 자료는 **HashiCorp Terraform Associate (004) 자격증** 취득을 위한 완전한 교육 과정입니다.

### ✅ 포함된 내용

1. **📖 체계적인 학습 커리큘럼**
   - 8주 완성 플랜
   - 도메인별 심화 학습
   - 실무 중심 설명

2. **💻 실습 가이드**
   - 12개 Hands-on Labs
   - 단계별 지시사항
   - 실제 클라우드 환경 실습

3. **📝 예상 문제 풀이**
   - 실전 모의고사 3세트 (각 57문항)
   - 도메인별 연습 문제
   - 상세한 해설 포함

4. **🎯 시험 준비 전략**
   - 함정 문제 파악
   - 시간 관리 전략
   - 최신 004 버전 반영

---

## 🚀 빠른 시작

### Step 1: 자격증 정보 확인 (5분)
[README.md](/archive/project/readme/)의 "자격증 개요" 섹션을 읽으세요.

**핵심 정보:**
- 시험 시간: 60분
- 문제 수: 57문항
- 합격 기준: 약 70%
- 응시 비용: $70.50 USD
- 유효 기간: 2년

### Step 2: 학습 플랜 선택 (10분)

**Option A: 8주 완성 플랜 (권장)**
- 주당 8-10시간 투자
- 체계적인 진도 관리
- [8주 학습 플랜 보기](/archive/project/readme/#8주-완성-학습-플랜)

**Option B: 집중 4주 플랜**
- 주당 15-20시간 투자
- 빠른 자격증 취득 목표
- 핵심 도메인 우선 학습

**Option C: 자율 학습**
- 본인 페이스대로 진행
- 취약 영역 집중 공략

### Step 3: 환경 설정 (30분)

**필수 설치:**
```bash
# Terraform 설치
brew install terraform  # macOS
# 또는 https://www.terraform.io/downloads

# 버전 확인
terraform version
# Terraform v1.12.0 이상

# AWS CLI 설치 (선택)
brew install awscli
aws configure
```

**권장 도구:**
- VS Code + HashiCorp Terraform 확장
- Git
- AWS/Azure/GCP 무료 계정

### Step 4: 첫 번째 실습 시작 (1시간)

[Lab 01: 첫 번째 Terraform 프로젝트](/archive/labs/lab-01-first-project/readme/)

**학습 내용:**
- Terraform 기본 워크플로우
- 간단한 리소스 생성
- State 파일 이해

---

## 📅 8주 학습 로드맵

### Week 1-2: 기초 다지기
**이론:**
- [IaC 개념](/archive/project/readme/#week-1-2-terraform-기초-및-iac-개념)
- Terraform 설치 및 초기 설정
- Provider 이해

**실습:**
- Lab 01: 첫 번째 Terraform 프로젝트
- Lab 02: Variables와 Outputs
- Lab 03: Data Sources 활용

**목표:**
- Core Workflow 완벽 이해
- `init → plan → apply → destroy` 숙달

---

### Week 3: Core Workflow
**이론:**
- [Core Terraform Workflow](/archive/project/readme/#week-3-core-terraform-workflow-핵심-워크플로우)
- CLI 명령어 마스터

**실습:**
- 모든 CLI 명령어 직접 실행
- `terraform fmt`, `terraform validate` 활용

**목표:**
- 각 명령어의 역할 명확히 구분
- State 파일 구조 이해

---

### Week 4: HCL 언어
**이론:**
- [Terraform Configuration](/archive/project/readme/#week-4-terraform-configuration-hcl-언어)
- Variables, Outputs, Functions
- Complex Types

**실습:**
- Lab 04: count와 for_each

**목표:**
- HCL 문법 완벽 숙달
- Built-in Functions 활용

---

### Week 5: Modules
**이론:**
- [Terraform Modules](/archive/project/readme/#week-5-terraform-modules-모듈-시스템)
- Module 구조 및 재사용

**실습:**
- Lab 05: 첫 번째 Module 만들기
- Lab 11: Module Registry 활용

**목표:**
- Module 작성 능력
- Terraform Registry 활용

---

### Week 6: State Management
**이론:**
- [State Management](/archive/project/readme/#week-6-state-management-상태-관리)
- Remote Backend
- State Locking

**실습:**
- Lab 06: Remote State 설정
- Lab 10: State 조작 마스터

**목표:**
- State 파일의 역할 완벽 이해
- `terraform import` 숙달

---

### Week 7: Lifecycle & Validation (004 강화)
**이론:**
- [Lifecycle & Custom Conditions](/archive/project/readme/#week-7-lifecycle--custom-conditions-004-신규-강화)
- Preconditions/Postconditions
- Check Blocks

**실습:**
- Lab 07: Lifecycle Meta-Arguments
- Lab 08: Custom Conditions
- Lab 09: Dynamic Blocks

**목표:**
- 004 신규 기능 숙달
- 안전한 리소스 관리

---

### Week 8: HCP Terraform & 최종 복습
**이론:**
- [HCP Terraform](/archive/project/readme/#week-8-hcp-terraform--최종-복습)
- Workspaces vs Projects
- 협업 기능

**실습:**
- Lab 12: HCP Terraform 워크플로우

**모의고사:**
- 월요일: [모의고사 Set 1](/archive/practice-exams/mock-exam-set-1/) (60분)
- 화요일: Set 1 복습 및 취약점 보완
- 수요일: 모의고사 Set 2 (60분)
- 목요일: Set 2 복습
- 금요일: 모의고사 Set 3 (60분)
- 토요일: 최종 복습
- 일요일: 휴식

**목표:**
- 모의고사 80% 이상
- 전 도메인 균형있는 이해

---

## 📊 도메인별 학습 우선순위

### High Priority (총 58% - 약 33문항)

#### 1. Terraform Configuration (26% - 15문항)
**핵심 주제:**
- Variables, Outputs
- count vs for_each
- Dynamic Blocks
- Built-in Functions
- Lifecycle Meta-Arguments
- Custom Conditions ⭐ (004 신규)

**학습 자료:**
- [Week 4 커리큘럼](/archive/project/readme/#week-4-terraform-configuration-hcl-언어)
- Lab 02, 04, 07, 08, 09
- [Configuration 예상문제](/archive/practice-exams/mock-exam-set-1/#domain-4-terraform-configuration-26--15-questions)

#### 2. State Management (16% - 9문항)
**핵심 주제:**
- State 파일의 역할
- Remote Backend (S3 + DynamoDB)
- State Locking
- terraform import
- Drift Detection

**학습 자료:**
- [Week 6 커리큘럼](/archive/project/readme/#week-6-state-management-상태-관리)
- Lab 06, 10
- [State 예상문제](/archive/practice-exams/mock-exam-set-1/#domain-6-state-management-16--9-questions)

#### 3. Core Workflow (16% - 9문항)
**핵심 주제:**
- `init → plan → apply → destroy` 순서
- `terraform fmt`, `terraform validate`
- `-refresh=false`, `-auto-approve` 플래그
- State refresh 동작

**학습 자료:**
- [Week 3 커리큘럼](/archive/project/readme/#week-3-core-terraform-workflow-핵심-워크플로우)
- Lab 01
- [Core Workflow 예상문제](/archive/practice-exams/mock-exam-set-1/#domain-3-core-terraform-workflow-16--9-questions)

---

### Medium Priority (총 30% - 17문항)

#### 4. Terraform Modules (10% - 6문항)
- Module 구조 (main.tf, variables.tf, outputs.tf)
- Module 소스 (local, registry, GitHub)
- Module 버전 관리

#### 5. Terraform Fundamentals (10% - 6문항)
- Provider 개념
- `.terraform.lock.hcl`
- Provider Aliases

#### 6. Maintain Infrastructure (10% - 6문항)
- terraform import
- `terraform state` 명령어
- Deprecated 명령어 (`taint` → `-replace`)

---

### Lower Priority (총 12% - 7문항)

#### 7. HCP Terraform (6% - 3문항)
- Workspaces vs Projects
- Run Workflow 순서
- Remote Execution

#### 8. IaC Concepts (6% - 3문항)
- Declarative vs Imperative
- IaC 장점
- Terraform 특징

---

## 🎯 시험 당일 전략

### 시험 전날
- [ ] 가벼운 복습만 (핵심 개념 재확인)
- [ ] [함정 문제](/archive/practice-exams/readme/#자주-틀리는-함정-문제) 다시 보기
- [ ] 충분한 수면 (7-8시간)

### 시험 당일 아침
- [ ] [CLI 명령어 치트시트](/archive/03-core-workflow/cli-commands/) 빠르게 훑기
- [ ] Deprecated 명령어 확인
  - `terraform taint` → `terraform apply -replace=`
  - `terraform refresh` → `terraform apply -refresh-only`

### 시험 중
1. **시간 관리 (60분 / 57문항)**
   - 문제당 약 1분
   - 쉬운 문제 30초 안에 해결
   - 어려운 문제 플래그 후 나중에

2. **문제 읽기 전략**
   - 키워드 주목 (always, never, best, recommended)
   - 다중 선택: 몇 개 선택할지 확인
   - True/False: 반례 찾기

3. **확신이 안 서는 문제**
   - 플래그 표시
   - 명백히 틀린 선택지부터 제거
   - 최선의 답 선택 후 넘어가기

4. **마지막 10분**
   - 플래그된 문제 재검토
   - 모든 문제 답변 완료 확인

---

## 🔥 핵심 암기 사항

### 명령어 차이

| 구분 | 명령어 | State 접근 | 인프라 변경 |
|------|--------|-----------|-----------|
| **Plan** | `terraform plan` | Read (refresh) | ❌ |
| **Apply** | `terraform apply` | Read/Write | ✅ |
| **Validate** | `terraform validate` | ❌ | ❌ |
| **Fmt** | `terraform fmt` | ❌ | ❌ |
| **Destroy** | `terraform destroy` | Read/Write | ✅ (삭제) |

### count vs for_each

```hcl
# count: 인덱스 기반 (0, 1, 2...)
resource "aws_instance" "server" {
  count = 3
  # 참조: aws_instance.server[0]
}

# for_each: 키 기반 (map/set)
resource "aws_instance" "server" {
  for_each = toset(["web", "api"])
  # 참조: aws_instance.server["web"]
}
```

**차이점:**
- count: 중간 제거 시 재생성 위험 ⚠️
- for_each: 안전한 제거 ✅

### sensitive = true 함정

```hcl
variable "password" {
  sensitive = true  # CLI 출력만 숨김
}

# ⚠️ State 파일에는 평문 저장!
# ✅ Remote Backend + Encryption 필수
```

### Backend Locking

```hcl
# ❌ S3만으로는 Locking 안 됨
terraform {
  backend "s3" {
    bucket = "my-bucket"
  }
}

# ✅ DynamoDB 추가 필요
terraform {
  backend "s3" {
    bucket         = "my-bucket"
    dynamodb_table = "terraform-lock"
  }
}
```

### HCP Terraform Run Order

```
✅ Plan → Cost Estimation → Policy Check → Apply

❌ Plan → Apply
❌ Plan → Policy → Cost → Apply
```

---

## 📚 참고 자료

### 공식 자료 (필수)
- [Terraform Associate 004 Learning Path](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004)
- [Exam Content List](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004)
- [Sample Questions](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)

### 이 가이드 내부 링크
- [README.md](/archive/project/readme/) - 전체 커리큘럼
- [실습 가이드](/archive/labs/readme/) - Hands-on Labs
- [예상 문제](/archive/practice-exams/readme/) - 모의고사 3세트

### 커뮤니티
- [HashiCorp Discuss](https://discuss.hashicorp.com/)
- [r/Terraform](https://www.reddit.com/r/Terraform/)

---

## ✅ 학습 체크리스트

### Week 1-2: 기초
- [ ] Terraform 설치 완료
- [ ] AWS/클라우드 계정 생성
- [ ] Lab 01, 02, 03 완료
- [ ] Core Workflow 이해

### Week 3-4: 중급
- [ ] CLI 명령어 숙달
- [ ] HCL 문법 완벽 이해
- [ ] Lab 04 완료
- [ ] Variables/Outputs 자유자재 활용

### Week 5-6: 고급
- [ ] Module 작성 능력
- [ ] Remote State 설정
- [ ] State 조작 명령어 숙달
- [ ] Lab 05, 06, 10, 11 완료

### Week 7: 004 신규 기능
- [ ] Lifecycle 완벽 이해
- [ ] Custom Conditions 작성
- [ ] Dynamic Blocks 활용
- [ ] Lab 07, 08, 09 완료

### Week 8: 최종 점검
- [ ] HCP Terraform 이해
- [ ] Lab 12 완료
- [ ] 모의고사 Set 1: ___%
- [ ] 모의고사 Set 2: ___%
- [ ] 모의고사 Set 3: ___%
- [ ] 목표: 모든 모의고사 80% 이상

---

## 🎓 시험 신청

### 준비 완료 기준
- ✅ 모의고사 3세트 모두 80% 이상
- ✅ 모든 실습 완료
- ✅ 취약 도메인 없음

### 시험 등록
1. [HashiCorp Certification 페이지](https://www.hashicorp.com/certification/terraform-associate) 방문
2. "Schedule Exam" 클릭
3. Certiverse 계정 생성/로그인
4. 시험 날짜 선택
5. $70.50 결제

### 시험 환경
- 온라인 감독 (웹캠 필요)
- 조용한 공간 확보
- 신분증 준비
- 안정적인 인터넷 연결

---

## 💡 성공 팁

### DO (해야 할 것)
✅ 매일 조금씩 꾸준히 학습  
✅ 실습 우선 (이론:실습 = 4:6)  
✅ 틀린 문제 철저히 복습  
✅ 공식 문서 1차 자료로 활용  
✅ 모의고사는 실전처럼 60분 타이머  

### DON'T (하지 말 것)
❌ 벼락치기  
❌ 단순 암기  
❌ 실습 건너뛰기  
❌ 모의고사 여러 번 나눠서 풀기  
❌ 비공식 덤프 사용  

---

## 📞 도움이 필요하면

### 질문하기 좋은 곳
- [HashiCorp Discuss - Certification](https://discuss.hashicorp.com/c/terraform-core/certification/33)
- [r/Terraform](https://www.reddit.com/r/Terraform/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/terraform)

### 추가 학습이 필요하면
- [Udemy Terraform Courses](https://www.udemy.com/topic/terraform/)
- [A Cloud Guru](https://acloudguru.com/)
- [Linux Academy](https://linuxacademy.com/)

---

**여러분의 자격증 취득을 응원합니다! 🎉**

**Remember:** 
> "The best way to learn Terraform is to actually use it."

첫 번째 실습부터 시작하세요:  
👉 [Lab 01: 첫 번째 Terraform 프로젝트](/archive/labs/lab-01-first-project/readme/)
