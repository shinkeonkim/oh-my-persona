---
title: "Domain 3 문제 25개 / Core Workflow"
description: "Twenty-five Terraform Associate 004 core workflow practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 3 문제 25개입니다. 명령별 side effect는 [명령 동작 매트릭스](/reference/command-behavior-matrix/)에서 검증하세요.

## 📚 도메인 개요

Terraform CLI 명령어와 기본 워크플로우 (Write → Plan → Apply → Destroy).

---

## 📝 연습 문제

### 문제 1: 🟢 Easy

Terraform 기본 워크플로우 순서는?

- A) plan → init → apply
- B) init → plan → apply
- C) init → apply → plan
- D) plan → apply → init

<details><summary>정답 및 해설</summary>

**정답: B**

`init` (준비) → `plan` (계획) → `apply` (실행).
</details>

### 문제 2: 🟢 Easy

`terraform plan` 이 State 를 자동으로 refresh 하나요?

<details><summary>정답 및 해설</summary>

**정답: True**

기본적으로 plan 은 refresh 를 먼저 실행. `-refresh=false` 로 비활성화 가능.
</details>

### 문제 3: 🟡 Medium

State 를 자동 refresh 하는 명령어 2개는? (**Select TWO**)

- A) terraform plan
- B) terraform validate
- C) terraform apply
- D) terraform fmt

<details><summary>정답 및 해설</summary>

**정답: A, C**

plan, apply 는 refresh 자동 실행. validate, fmt 는 state 접근 안 함.
</details>

### 문제 4: 🟢 Easy

`terraform destroy` 는 무엇을 하나요?

- A) State 파일 삭제
- B) Provider 삭제
- C) 관리 중인 모든 리소스 삭제
- D) Terraform CLI 제거

<details><summary>정답 및 해설</summary>

**정답: C**

State 에 있는 모든 관리 리소스를 실제 인프라에서 제거.
</details>

### 문제 5: 🟡 Medium

`terraform.tfvars` 를 사용하려면?

- A) `-var-file="terraform.tfvars"` 필요
- B) 자동 로드됨
- C) 환경변수로 지정
- D) provider block 에 명시

<details><summary>정답 및 해설</summary>

**정답: B**

`terraform.tfvars` 와 `*.auto.tfvars` 는 자동 로드.
</details>

### 문제 6: 🔴 Hard

Deprecated 명령어 대체는?

- A) `terraform taint` → `terraform apply -replace=`
- B) `terraform refresh` → `terraform apply -refresh-only`
- C) 두 개 모두 정답
- D) 없음

<details><summary>정답 및 해설</summary>

**정답: C**

두 명령어 모두 deprecated. 대체 방법 암기 필수.
</details>

### 문제 7: 🟡 Medium

Plan 기호와 의미가 **틀린** 것은?

- A) `+` 생성
- B) `~` 수정
- C) `-` 삭제
- D) `!` 오류

<details><summary>정답 및 해설</summary>

**정답: D**

기호: `+` 생성, `~` 수정, `-` 삭제, `-/+` 재생성, `<=` data source read.
</details>

### 문제 8: 🟢 Easy

`terraform apply -auto-approve` 는 무엇을 건너뛰나요?

- A) plan
- B) refresh
- C) 대화형 승인
- D) validate

<details><summary>정답 및 해설</summary>

**정답: C**

대화형 "yes" 프롬프트 건너뜀. CI/CD 에 사용.
</details>

### 문제 9: 🟡 Medium

Plan 파일을 저장하고 재사용:

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

**True / False:** apply tfplan 은 승인이 필요하다.

<details><summary>정답 및 해설</summary>

**정답: False**

Plan 파일을 지정하면 이미 확정된 계획이므로 승인 불필요.
</details>

### 문제 10: 🔴 Hard

`terraform apply -refresh-only` 의 목적은?

- A) 리소스만 재생성
- B) State 만 실제 인프라와 동기화
- C) Provider 업그레이드
- D) Configuration 검증

<details><summary>정답 및 해설</summary>

**정답: B**

State 를 refresh 만 하고 리소스 변경 없음. Drift 반영에 사용.
</details>

### 문제 11: 🟡 Medium

`terraform validate` 는 무엇을 검증하나요?

- A) 실제 인프라 존재 여부
- B) 구문 및 타입
- C) State 무결성
- D) Provider 인증

<details><summary>정답 및 해설</summary>

**정답: B**

구문 오류, 타입 오류 검출. AWS API 호출 안 함.
</details>

### 문제 12: 🟢 Easy

`terraform fmt` 의 목적은?

- A) 인프라 포맷 변경
- B) 코드 포맷팅
- C) State 정리
- D) Provider 정리

<details><summary>정답 다 해설</summary>

**정답: B**

들여쓰기, 정렬 등 코드 스타일 통일.
</details>

### 문제 13: 🟡 Medium

`terraform apply -target=aws_instance.web` 는?

- A) 모든 리소스 대상
- B) 특정 리소스만 대상
- C) 특정 리소스 제외
- D) Module 만 대상

<details><summary>정답 및 해설</summary>

**정답: B**

지정된 리소스와 의존성만 apply. 프로덕션에서 지양.
</details>

### 문제 14: 🔴 Hard

Variable Precedence (높음 → 낮음) 순서는?

- A) default → CLI → tfvars → env
- B) env → tfvars → CLI → default
- C) CLI → tfvars → env → default
- D) tfvars → CLI → env → default

<details><summary>정답 및 해설</summary>

**정답: C**

`-var` (CLI) > `-var-file` > `terraform.tfvars` > `*.auto.tfvars` > `TF_VAR_*` > default.
</details>

### 문제 15: 🟡 Medium

`terraform output` 옵션이 **아닌** 것은?

- A) `-json`
- B) `-raw`
- C) `-state`
- D) `-refresh`

<details><summary>정답 및 해설</summary>

**정답: D**

Output 옵션: `-json`, `-raw`, `-state=FILE`. Refresh 는 없음.
</details>

### 문제 16: 🟡 Medium

`terraform show tfplan` 은?

- A) 인프라 상태 표시
- B) Plan 파일 내용 표시
- C) Provider 정보
- D) Logs 표시

<details><summary>정답 및 해설</summary>

**정답: B**

Plan 파일을 사람이 읽을 수 있는 형식으로 표시.
</details>

### 문제 17: 🔴 Hard

CI/CD 에서 사용할 명령어 조합:

```bash
terraform plan -out=tfplan -detailed-exitcode
```

Exit code 2 는 무엇을 의미?

- A) 에러
- B) 변경사항 없음
- C) 변경사항 있음
- D) 인증 실패

<details><summary>정답 및 해설</summary>

**정답: C**

`-detailed-exitcode`: 0=변경 없음, 1=에러, 2=변경 있음.
</details>

### 문제 18: 🟡 Medium

**True / False:** `terraform destroy` 는 State 파일도 삭제한다.

<details><summary>정답 및 해설</summary>

**정답: False**

Destroy 는 인프라만 삭제. State 파일은 유지 (빈 state 로).
</details>

### 문제 19: 🟢 Easy

환경변수 `TF_LOG=DEBUG` 는 무엇을 하나요?

- A) 로그 파일 위치 지정
- B) 로그 레벨 설정
- C) Provider 디버그
- D) 자동 재시도

<details><summary>정답 및 해설</summary>

**정답: B**

TRACE, DEBUG, INFO, WARN, ERROR 중 선택.
</details>

### 문제 20: 🟡 Medium

Variables 를 명령줄로 전달:

```bash
terraform apply -var="instance_type=t3.large"
```

이 값의 우선순위는?

- A) 가장 낮음
- B) 가장 높음
- C) 중간
- D) default 다음

<details><summary>정답 및 해설</summary>

**정답: B**

`-var` 는 최우선.
</details>

### 문제 21: 🟢 Easy

`terraform init -reconfigure` vs `-migrate-state` 차이는?

- A) 같은 명령어
- B) reconfigure 는 state 마이그레이션 없음
- C) migrate-state 는 backend 변경 안 함
- D) 순서만 다름

<details><summary>정답 및 해설</summary>

**정답: B**

`-reconfigure`: state 옮기지 않음 (위험).
`-migrate-state`: state 옮김.
</details>

### 문제 22: 🔴 Hard

**True / False:** `terraform validate` 는 provider 다운로드 없이도 실행할 수 있다.

<details><summary>정답 및 해설</summary>

**정답: False**

Validate 는 provider schema 를 사용하여 타입 검증. init 후에만 가능.
</details>

### 문제 23: 🟡 Medium

`terraform console` 의 용도는?

- A) State 편집
- B) 대화형 표현식 평가
- C) 원격 실행
- D) 로그 확인

<details><summary>정답 및 해설</summary>

**정답: B**

함수 테스트, 리소스 속성 확인, 표현식 검증.
</details>

### 문제 24: 🟢 Easy

`terraform apply` 실행 후 무엇이 State 파일에 저장되나요?

- A) 모든 리소스 attributes
- B) Terraform 명령어 이력
- C) 사용자 credentials
- D) Provider 소스코드

<details><summary>정답 및 해설</summary>

**정답: A**

모든 관리 리소스의 attributes 와 metadata.
</details>

### 문제 25: 🔴 Hard

여러 리소스에 대해 `apply -replace` 를 실행하는 방법은?

- A) 한번에 하나씩만
- B) 콤마로 구분: `-replace=a,b,c`
- C) 여러 번 사용: `-replace=a -replace=b`
- D) 지원 안 됨

<details><summary>정답 및 해설</summary>

**정답: C**

`terraform apply -replace=aws_instance.web -replace=aws_instance.app` 처럼 여러 번 사용.
</details>

---

## 🎯 핵심 개념 정리

1. **Workflow: init → validate → fmt → plan → apply**
2. **Plan 기호: + ~ - -/+**
3. **Deprecated: taint → apply -replace, refresh → apply -refresh-only**
4. **State refresh: plan/apply 자동**
5. **Variable precedence: CLI > tfvars > env > default**
6. **Exit codes: 0/1/2 (with -detailed-exitcode)**

---

## 📚 관련 학습 자료

- [Core Workflow](/archive/03-core-workflow/readme/)
- [CLI 명령어 상세](/archive/03-core-workflow/cli-commands/)
- [State 기본](/archive/03-core-workflow/state-basics/)
