---
title: "Domain 1 문제 20개 / IaC Concepts"
description: "Twenty Terraform Associate 004 Infrastructure as Code practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 1 문제 20개입니다. 정답을 연 뒤 각 개념을 [공식 목표](/reference/exam-objectives/)와 대조하세요.

## 📚 도메인 개요

IaC 의 기본 개념, Terraform 의 역할, 다른 도구와의 차이점을 다룹니다.

## 🎯 학습 목표

- IaC 개념 및 이점 이해
- Declarative vs Imperative 구분
- Terraform 의 목적과 특징
- 사용 사례 파악

---

## 📝 연습 문제

### 문제 1: 🟢 Easy

Infrastructure as Code (IaC) 의 주요 이점이 **아닌** 것은?

- A) 재현성 (Reproducibility)
- B) 버전 관리
- C) 자동화
- D) 하드웨어 성능 향상

<details><summary>정답 및 해설</summary>

**정답: D**

IaC 는 코드로 인프라를 관리하는 방법론이지, 하드웨어 성능과는 무관합니다. A, B, C 는 IaC 의 대표적 이점입니다.
</details>

### 문제 2: 🟢 Easy

Terraform 은 어떤 접근 방식을 사용하나요?

- A) Imperative (명령적)
- B) Declarative (선언적)
- C) Reactive
- D) Functional

<details><summary>정답 및 해설</summary>

**정답: B) Declarative**

Terraform 은 "무엇을" 원하는지 명시하면, 어떻게 만들지는 Terraform 이 결정합니다.
</details>

### 문제 3: 🟢 Easy

**True / False:** Terraform 은 오직 AWS 만 지원한다.

<details><summary>정답 및 해설</summary>

**정답: False**

Terraform은 public cloud, private cloud, SaaS 등 서로 다른 API를 provider plugin으로 관리할 수 있습니다. Provider 수는 시점에 따라 바뀌므로 고정 숫자를 시험 사실로 외우지 않습니다.
</details>

### 문제 4: 🟡 Medium

Declarative 접근의 특징으로 **틀린** 것은?

- A) 최종 상태를 명시
- B) 순서를 명시적으로 지정해야 함
- C) 멱등성 (Idempotent)
- D) 여러 번 실행해도 동일 결과

<details><summary>정답 및 해설</summary>

**정답: B**

Declarative 는 순서를 신경 쓸 필요가 없습니다. Terraform 이 종속성을 계산하여 자동으로 순서 결정.
Imperative (Shell script 등) 는 순서가 중요합니다.
</details>

### 문제 5: 🟡 Medium

Terraform vs Ansible 의 주요 차이점은? (**Select TWO**)

- A) Terraform 은 프로비저닝, Ansible 은 구성 관리
- B) Terraform 은 State 를 사용, Ansible 은 Stateless
- C) Terraform 은 Imperative, Ansible 은 Declarative
- D) Terraform 은 YAML, Ansible 은 HCL

<details><summary>정답 및 해설</summary>

**정답: A, B**

- Terraform: 인프라 프로비저닝 + State 관리 + Declarative + HCL
- Ansible: 구성 관리 + Stateless + Imperative (Playbook) + YAML
</details>

### 문제 6: 🟡 Medium

Terraform 이 지원하는 Provider 유형이 **아닌** 것은?

- A) Public Cloud (AWS, Azure, GCP)
- B) Private Cloud (VMware, OpenStack)
- C) SaaS (GitHub, Datadog)
- D) Operating System 커널 모듈

<details><summary>정답 및 해설</summary>

**정답: D**

Terraform 은 API 를 노출하는 서비스만 관리 가능. OS 커널 모듈은 Ansible/Puppet 등의 영역.
</details>

### 문제 7: 🟢 Easy

**True / False:** IaC 를 사용하면 인프라를 Git 으로 버전 관리할 수 있다.

<details><summary>정답 및 해설</summary>

**정답: True**

인프라 정의가 코드이므로 Git 등 VCS 로 관리 가능. 모든 변경사항 추적, PR 리뷰, 롤백 가능.
</details>

### 문제 8: 🔴 Hard

다음 시나리오에 가장 적합한 도구는?

시나리오: 이미 존재하는 100대의 EC2 인스턴스에 nginx 를 설치하고 설정 파일을 배포.

- A) Terraform
- B) Ansible
- C) CloudFormation
- D) Pulumi

<details><summary>정답 및 해설</summary>

**정답: B) Ansible**

기존 인스턴스의 **내부 구성 관리** 는 Ansible 의 영역. Terraform 은 인스턴스 자체를 만들고 관리.
</details>

### 문제 9: 🟡 Medium

멱등성 (Idempotency) 이란?

- A) 매번 다른 결과
- B) 여러 번 실행해도 동일 결과
- C) 실행 순서에 따라 결과 변경
- D) 실패 시 자동 재시도

<details><summary>정답 및 해설</summary>

**정답: B**

Terraform apply 를 두 번 실행해도 인프라 상태는 동일. Declarative 도구의 핵심 특성.
</details>

### 문제 10: 🟡 Medium

Multi-cloud 배포에 Terraform 이 적합한 이유는? (**Select TWO**)

- A) 단일 CLI 로 여러 클라우드 관리
- B) HCL 로 통일된 문법
- C) 클라우드 간 자동 마이그레이션
- D) 클라우드 종속성 회피

<details><summary>정답 및 해설</summary>

**정답: A, B, D**

Terraform 은 각 클라우드의 API 를 provider 로 통합. 단일 CLI, 일관된 문법, vendor lock-in 회피.
</details>

### 문제 11: 🟢 Easy

**True / False:** Terraform 은 Immutable Infrastructure 를 지원한다.

<details><summary>정답 및 해설</summary>

**정답: True**

`create_before_destroy` 로 무중단 재생성 지원. AMI 기반 배포로 immutable pattern 구현.
</details>

### 문제 12: 🔴 Hard

전통적인 방식 (Manual/Click-ops) vs IaC 의 차이점이 **아닌** 것은?

- A) IaC 는 재현성이 높음
- B) IaC 는 버전 관리 가능
- C) IaC 는 성능이 더 빠름
- D) IaC 는 협업이 용이

<details><summary>정답 및 해설</summary>

**정답: C**

IaC 는 재현성, 버전관리, 협업, 자동화의 이점이 있지만 성능 자체는 인프라 성능에 의존.
</details>

### 문제 13: 🟡 Medium

CloudFormation vs Terraform 비교로 **틀린** 것은?

- A) Terraform 은 멀티 클라우드
- B) CloudFormation 은 AWS 전용
- C) CloudFormation 은 HCL 사용
- D) Terraform 은 HCL 사용

<details><summary>정답 및 해설</summary>

**정답: C**

CloudFormation 은 YAML/JSON 사용. Terraform 은 HCL.
</details>

### 문제 14: 🟢 Easy

Terraform 의 State 파일 목적은?

- A) Provider 다운로드
- B) 현재 인프라 상태 저장
- C) 실행 로그
- D) 사용자 인증

<details><summary>정답 및 해설</summary>

**정답: B**

State 는 Terraform 이 관리하는 인프라의 현재 상태를 JSON 으로 저장.
</details>

### 문제 15: 🟡 Medium

Immutable Infrastructure 의 특징은?

- A) 서버를 in-place 로 업데이트
- B) 새 서버를 만들고 기존을 삭제
- C) 서버 성능이 변하지 않음
- D) 서버 이름을 절대 변경 안 함

<details><summary>정답 및 해설</summary>

**정답: B**

Immutable 은 기존 서버를 수정하지 않고 새로 만드는 패턴. Terraform 의 `create_before_destroy` 와 잘 맞음.
</details>

### 문제 16: 🔴 Hard

다음 중 IaC 도구의 예가 **아닌** 것은?

- A) Terraform
- B) CloudFormation
- C) Pulumi
- D) Nagios

<details><summary>정답 및 해설</summary>

**정답: D) Nagios**

Nagios 는 인프라 모니터링 도구. IaC 도구 아님.
</details>

### 문제 17: 🟡 Medium

**True / False:** Terraform 은 GUI 관리 콘솔을 제공한다.

<details><summary>정답 및 해설</summary>

**정답: False**

Terraform CLI 는 command-line 만 제공. GUI 는 HCP Terraform (별도 SaaS) 에서 제공.
</details>

### 문제 18: 🟢 Easy

Terraform 을 사용하면 다음 중 어떤 작업이 자동화되나요? (**Select TWO**)

- A) 인프라 생성
- B) 인프라 변경 감지
- C) 서비스 모니터링 (real-time)
- D) 애플리케이션 배포

<details><summary>정답 및 해설</summary>

**정답: A, B**

Terraform: 인프라 CRUD, State 관리, Drift 감지. 실시간 모니터링과 애플리케이션 배포는 다른 도구 영역.
</details>

### 문제 19: 🟡 Medium

시나리오: 개발/스테이징/프로덕션 3개 환경을 동일 구성으로 관리. IaC 의 어떤 이점을 활용하나요?

- A) 자동 스케일링
- B) 재현성 (Reproducibility)
- C) 로드 밸런싱
- D) 모니터링

<details><summary>정답 및 해설</summary>

**정답: B) 재현성**

동일 코드로 여러 환경에 동일한 인프라를 생성. IaC 의 대표적 이점.
</details>

### 문제 20: 🔴 Hard

HashiCorp Configuration Language (HCL) 의 특징이 **아닌** 것은?

- A) 사람이 읽기 쉬움
- B) JSON 과 호환 가능
- C) Terraform 외의 다른 HashiCorp 도구도 사용
- D) 튜링 완전 (Turing complete)

<details><summary>정답 및 해설</summary>

**정답: D**

HCL 은 declarative 설정 언어로 튜링 완전 아님. 복잡한 로직은 함수와 표현식으로 처리.
</details>

---

## 🎯 핵심 개념 정리

1. **IaC = 인프라를 코드로**
2. **Declarative (Terraform) vs Imperative (Shell)**
3. **Terraform 특징:** Multi-cloud, State, Provider 아키텍처
4. **Terraform vs Ansible:** 프로비저닝 vs 구성 관리
5. **HCL:** Human-readable, JSON 호환

---

## 📚 관련 학습 자료

- [Week 1-2: IaC 개념](/archive/01-iac-concepts/readme/)
- [Terraform 설치](/archive/01-iac-concepts/installation/)
- [Mock Exam Set 1](/archive/practice-exams/mock-exam-set-1/)
