---
title: "Historical Status Snapshot (2026-07-20)"
description: "Historical 2026-07-20 project snapshot; not the current content status."
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

현재 완료 상태는 [현재 자료 상태 / Content Status](/guide/content-status/)를 사용하세요. 아래 `진행 중 / 확장 가능` 목록은 당시 기록이며 현재 backlog가 아닙니다.

생성 일시: 2026년 7월 20일

---

## ✅ 완성된 자료

### 1. 핵심 가이드 문서
- ✅ **README.md** - 전체 8주 커리큘럼 및 상세 학습 가이드 (16KB)
- ✅ **QUICKSTART.md** - 빠른 시작 가이드 및 핵심 요약
- ✅ **practice-exams/README.md** - 예상 문제 풀이 가이드

### 2. 모의고사
- ✅ **Mock Exam Set 1** - 57문항 (완성)
  - Domain 1: IaC Concepts (3문항)
  - Domain 2: Terraform Fundamentals (6문항)
  - Domain 3: Core Workflow (9문항)
  - Domain 4: Terraform Configuration (15문항)
  - Domain 5: Modules (6문항)
  - Domain 6: State Management (9문항)
  - Domain 7: Maintain Infrastructure (6문항)
  - Domain 8: HCP Terraform (3문항)
  - **모든 문제에 상세 해설 포함**

### 3. 실습 Labs
- ✅ **labs/README.md** - 12개 Lab 개요 및 가이드
- ✅ **Lab 01: 첫 번째 Terraform 프로젝트** (완전한 단계별 가이드)
  - 상세 README (30분-45분 실습)
  - 솔루션 파일 (providers.tf, main.tf, outputs.tf)
  - .gitignore
- ✅ **Lab 02: Variables와 Outputs** (기본 가이드)

---

## 🚧 진행 중 / 확장 가능 자료

### 추가 모의고사 (확장 가능)
- ⏳ Mock Exam Set 2 (57문항) - 템플릿 준비됨
- ⏳ Mock Exam Set 3 (57문항) - 템플릿 준비됨
- ⏳ 도메인별 심화 문제집

### 추가 Labs (확장 가능)
템플릿과 가이드라인이 제공되어 있어 필요 시 추가 생성 가능:
- ⏳ Lab 03: Data Sources 활용
- ⏳ Lab 04: count와 for_each
- ⏳ Lab 05: 첫 번째 Module 만들기
- ⏳ Lab 06: Remote State 설정
- ⏳ Lab 07: Lifecycle Meta-Arguments
- ⏳ Lab 08: Custom Conditions (004 신규)
- ⏳ Lab 09: Dynamic Blocks
- ⏳ Lab 10: State 조작 마스터
- ⏳ Lab 11: Module Registry 활용
- ⏳ Lab 12: HCP Terraform 워크플로우

---

## 📚 제공되는 학습 가치

### 현재 자료로 학습 가능한 내용

#### 1. 체계적인 커리큘럼 (README.md)
- **8주 완성 플랜** - 주차별 학습 목표 및 내용
- **도메인별 가중치 분석** - 시험 출제 비중 명시
- **003 vs 004 비교** - 신규 변경사항 강조
- **핵심 개념 정리** - count vs for_each, State, Lifecycle 등
- **시험 전략** - 시간 관리, 함정 회피, 우선순위

**포함된 내용:**
- Week 1-2: IaC 개념 및 Terraform 기초
- Week 3: Core Terraform Workflow (상세)
- Week 4: Terraform Configuration - HCL 언어 (상세)
- Week 5: Terraform Modules (상세)
- Week 6: State Management (상세)
- Week 7: Lifecycle & Custom Conditions (004 강화)
- Week 8: HCP Terraform & 최종 복습

#### 2. 실전 모의고사 (Mock Exam Set 1)
- **57문항** - 실제 시험과 동일한 형식
- **3가지 문제 유형** - True/False, Single Choice, Multiple Choice
- **난이도 표시** - 🟢 Easy, 🟡 Medium, 🔴 Hard
- **상세 해설** - 모든 문제에 설명 + 공식 문서 링크
- **실전 시뮬레이션** - 60분 타이머로 연습

**특징:**
- 도메인별 가중치 정확히 반영
- 004 신규 기능 충분히 포함
- 함정 문제 및 주의사항 명시
- 실무 시나리오 기반 문제

#### 3. Hands-on 실습 (Lab 01)
- **완전한 단계별 가이드** - 초보자도 따라할 수 있음
- **예상 출력 포함** - 각 단계의 결과 확인 가능
- **문제 해결 섹션** - 일반적인 오류 및 해결 방법
- **학습 포인트 정리** - 핵심 개념 재확인
- **솔루션 파일** - 완성된 코드 제공

**Lab 01 내용:**
- Terraform 설치 및 초기화
- Provider 설정
- S3 Bucket 생성
- State 파일 이해
- Outputs 활용
- 리소스 수정
- 인프라 삭제

#### 4. 빠른 시작 가이드 (QUICKSTART.md)
- **4단계 시작 프로세스**
- **학습 플랜 선택** - 8주/4주/자율
- **환경 설정 가이드**
- **도메인별 우선순위** - High/Medium/Low
- **핵심 암기 사항** - 표로 정리
- **시험 당일 전략**
- **체크리스트** - 진도 관리

---

## 🎯 이 자료만으로 가능한 것

### ✅ 충분히 학습 가능
1. **Terraform 기본 개념** - Core Workflow, State, Providers
2. **시험 문제 유형 파악** - 57문항 실전 연습
3. **도메인별 학습** - 가중치 높은 영역 집중
4. **실습 경험** - 최소 1개 Lab으로 hands-on
5. **시험 전략 수립** - 시간 관리, 우선순위

### 📈 학습 효과 극대화 방법

**1단계: 이론 학습 (README.md)**
- Week 1-8 커리큘럼 순서대로 학습
- 각 도메인의 핵심 개념 이해
- 공식 문서 병행 학습

**2단계: 실습 (Lab 01)**
- 실제 Terraform 설치 및 실행
- 각 명령어의 동작 체험
- State 파일 직접 확인

**2.5단계: 추가 Lab 자체 생성**
- Lab README.md의 다른 Lab 개요 참고
- 공식 HashiCorp Learn 튜토리얼 활용
- 직접 시나리오 만들어 실습

**3단계: 문제 풀이 (Mock Exam Set 1)**
- 60분 타이머 설정하고 실전처럼 풀기
- 틀린 문제 철저히 복습
- 해설의 공식 문서 링크 확인

**4단계: 취약점 보완**
- Mock Exam 결과 분석
- 낮은 점수 도메인 집중 학습
- README.md 해당 섹션 재학습

**5단계: 최종 점검**
- QUICKSTART.md 핵심 암기사항 재확인
- 함정 문제 다시 보기
- 시험 당일 전략 숙지

---

## 💡 추가 학습 자료 활용

### HashiCorp 공식 자료 (무료)
현재 가이드와 병행하면 최상의 효과:

1. **[Terraform Associate 004 Learning Path](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004)**
   - 공식 튜토리얼
   - 단계별 hands-on
   
2. **[Exam Content List](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004)**
   - 도메인별 문서 링크
   - 정확한 시험 범위
   
3. **[Sample Questions](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004)**
   - 공식 예제 문제
   - 문제 유형 확인

4. **[Terraform Documentation](https://developer.hashicorp.com/terraform/docs)**
   - 전체 레퍼런스
   - 상세 설명

### 실습 환경
1. **AWS Free Tier**
   - S3, EC2 (t2.micro 750시간/월)
   - 실제 클라우드 환경

2. **LocalStack** (선택)
   - 로컬에서 AWS 시뮬레이션
   - 비용 없이 실습

3. **Terraform Cloud Free Tier**
   - HCP Terraform 실습
   - 500 managed resources

---

## 📊 학습 로드맵 추천

### 최소 4주 집중 플랜

**Week 1: 기초 + 모의고사 1회**
- README Week 1-2 학습
- Lab 01 완료
- Mock Exam Set 1 풀이 (1차)
- 목표: 50-60%

**Week 2: 핵심 도메인**
- README Week 3-5 학습 (Workflow, Configuration, Modules)
- 공식 튜토리얼 병행
- Mock Exam Set 1 재풀이 (2차)
- 목표: 65-75%

**Week 3: 고급 + State**
- README Week 6-7 학습 (State, Lifecycle)
- 추가 실습 (자체 생성 또는 공식 튜토리얼)
- 취약 도메인 집중 보완
- 목표: 도메인별 균형

**Week 4: 최종 점검**
- README Week 8 + HCP Terraform
- QUICKSTART 핵심 암기
- Mock Exam Set 1 최종 (3차)
- 목표: 80% 이상 → 시험 신청

---

## 🎓 시험 신청 시점

다음 조건을 모두 만족할 때:
- ✅ Mock Exam Set 1에서 3회 연속 80% 이상
- ✅ 모든 도메인에서 70% 이상
- ✅ 최소 1개 이상의 실습 완료
- ✅ QUICKSTART 핵심 암기사항 숙지
- ✅ 함정 문제 패턴 파악

---

## 🔥 이 자료의 강점

### 1. 한국어 완벽 지원
- 모든 설명이 한국어
- 기술 용어 정확한 번역
- 이해하기 쉬운 설명

### 2. 004 최신 버전 반영
- Lifecycle 강화
- Custom Conditions
- Ephemeral Values
- HCP Terraform Projects

### 3. 실전 중심
- 실제 시험 형식
- 프로덕션 시나리오
- Best Practices

### 4. 체계적 구성
- 도메인별 가중치 반영
- 난이도 순차 상승
- 점진적 학습

### 5. 즉시 활용 가능
- 별도 등록 불필요
- 추가 비용 없음
- 모든 자료 로컬 보유

---

## 📞 추가 확장

### 더 많은 연습이 필요하면

**추가 모의고사:**
- 이 가이드의 Mock Exam Set 1 형식을 참고
- 공식 Sample Questions 활용
- 커뮤니티 Practice Tests 활용

**추가 Labs:**
- HashiCorp Learn 튜토리얼 직접 실습
- 자신만의 시나리오 생성
- GitHub 공개 Module 분석

**커뮤니티 활용:**
- r/Terraform
- HashiCorp Discuss
- Stack Overflow

---

## ✨ 결론

**현재 제공된 자료:**
- ✅ 완전한 8주 커리큘럼
- ✅ 57문항 실전 모의고사 (상세 해설)
- ✅ Hands-on Lab (단계별 가이드)
- ✅ 빠른 시작 가이드
- ✅ 시험 전략 및 팁

**이 자료만으로도:**
- 체계적인 학습 가능
- 실전 감각 익히기 가능
- 자격증 취득 준비 완료 가능

**성공적인 학습을 위한 조언:**
1. 공식 문서를 1차 자료로 활용
2. 실습을 절대 건너뛰지 말 것
3. 틀린 문제는 반드시 이해할 것
4. 모의고사는 실전처럼 풀 것
5. 꾸준히, 매일 조금씩

---

**Good luck with your certification journey! 🚀**

시작하려면: [QUICKSTART.md](/archive/project/quickstart/)
