---
title: "Domain 7 문제 25개 / Maintain Infrastructure"
description: "Twenty-five Terraform Associate 004 maintenance practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 7 문제 25개입니다. Import, state inspection, verbose logging을 공식 7a-7c와 대조하세요.

## 📚 도메인 개요

Import, Drift 대응, Debug, Refactoring, Provider migration.

---

## 📝 연습 문제

### 문제 1: 🔴 Hard

Deprecated 명령어 대응:

- A) `terraform taint` → `terraform apply -replace=`
- B) `terraform refresh` → `terraform apply -refresh-only`
- C) 두 개 모두 정답
- D) 대체 없음

<details><summary>정답 및 해설</summary>

**정답: C**

두 명령어 모두 deprecated. 시험 필수 암기.
</details>

### 문제 2: 🟡 Medium

기존 EC2 인스턴스를 Terraform 으로 가져오기:

- A) `terraform import aws_instance.web i-1234`
- B) `terraform apply -import`
- C) `terraform state add`
- D) `terraform load`

<details><summary>정답 및 해설</summary>

**정답: A**

`terraform import <address> <id>` (CLI 방식).
</details>

### 문제 3: 🟢 Easy

**True / False:** `terraform import` 는 config 파일을 자동 생성한다.

<details><summary>정답 및 해설</summary>

**정답: False**

CLI 방식은 State 만 업데이트. Config 는 수동 작성.
Import block (1.5+) 의 `-generate-config-out` 은 예외.
</details>

### 문제 4: 🟡 Medium

Import block 으로 config 자동 생성:

- A) `terraform apply -generate-config`
- B) `terraform plan -generate-config-out=file.tf`
- C) `terraform import -generate`
- D) 자동으로 항상 생성

<details><summary>정답 및 해설</summary>

**정답: B**
</details>

### 문제 5: 🔴 Hard

`terraform apply -replace=aws_instance.web` 는?

- A) 인스턴스 이름 변경
- B) 인스턴스 재생성 (destroy + create)
- C) 인스턴스 삭제
- D) 인스턴스 복제

<details><summary>정답 및 해설</summary>

**정답: B**

기존 `terraform taint` 의 대체.
</details>

### 문제 6: 🟡 Medium

Drift 감지 시 사용하는 명령어는?

- A) `terraform plan`
- B) `terraform state list`
- C) `terraform validate`
- D) `terraform fmt`

<details><summary>정답 및 해설</summary>

**정답: A**

Plan 실행 시 자동으로 refresh + drift 표시.
</details>

### 문제 7: 🟢 Easy

Debug logging 활성화:

- A) `TF_LOG=DEBUG`
- B) `TF_DEBUG=true`
- C) `TERRAFORM_DEBUG=1`
- D) `--debug`

<details><summary>정답 및 해설</summary>

**정답: A**

`export TF_LOG=DEBUG` (TRACE, DEBUG, INFO, WARN, ERROR).
</details>

### 문제 8: 🟡 Medium

Log 를 파일로 저장:

- A) `TF_LOG_FILE`
- B) `TF_LOG_PATH`
- C) `TF_LOG_OUTPUT`
- D) `--log-file`

<details><summary>정답 및 해설</summary>

**정답: B**

`export TF_LOG_PATH=./terraform.log`
</details>

### 문제 9: 🔴 Hard

`terraform state replace-provider` 는 언제 사용?

- A) Provider version 변경
- B) Provider fork/rename 시 state 업데이트
- C) Provider 삭제
- D) Provider 인증

<details><summary>정답 및 해설</summary>

**정답: B**

`registry.terraform.io/-/aws → registry.terraform.io/hashicorp/aws` 같은 마이그레이션.
</details>

### 문제 10: 🟡 Medium

Refactoring: count → for_each 시 안전한 방법은?

- A) 그냥 변경 → 모두 재생성
- B) `moved` block 으로 각 인덱스 매핑
- C) State 파일 수동 편집
- D) 불가능

<details><summary>정답 및 해설</summary>

**정답: B**

```hcl
moved {
  from = aws_instance.web[0]
  to   = aws_instance.web["primary"]
}
```
</details>

### 문제 11: 🟢 Easy

**True / False:** `terraform import` 는 여러 리소스를 한 번에 import 할 수 있다.

<details><summary>정답 및 해설</summary>

**정답: False (CLI 방식)**

CLI: 한 번에 하나씩.
Import block (1.5+): 여러 개 가능.
</details>

### 문제 12: 🟡 Medium

Module 안의 리소스 import:

- A) `terraform import module.vpc.aws_vpc.main vpc-1234`
- B) `terraform import vpc.main vpc-1234`
- C) `terraform import aws_vpc.main vpc-1234 -module=vpc`
- D) 불가능

<details><summary>정답 및 해설</summary>

**정답: A**

`module.<NAME>.<RESOURCE_TYPE>.<NAME>` 로 참조.
</details>

### 문제 13: 🔴 Hard

`terraform apply -refresh-only` 후 확인해야 할 것은?

- A) State 파일 크기
- B) Real 상태를 반영한 diff 확인
- C) Provider 버전
- D) Backend 상태

<details><summary>정답 및 해설</summary>

**정답: B**

Refresh 후 config 와 real 사이 diff. Config 업데이트 또는 apply 결정.
</details>

### 문제 14: 🟡 Medium

Terraform Cloud 에서 Drift Detection 활성화:

- A) 자동 활성화
- B) Workspace → Settings → Health Assessments
- C) 별도 API 호출
- D) Terraform 코드에서

<details><summary>정답 및 해설</summary>

**정답: B**

Health Assessments 를 UI 에서 활성화 필요.
</details>

### 문제 15: 🟢 Easy

**True / False:** `terraform state rm` 후 리소스가 다시 필요하면 `terraform import` 해야 한다.

<details><summary>정답 및 해설</summary>

**정답: True**

State rm 은 관리 해제. 다시 관리하려면 import.
</details>

### 문제 16: 🔴 Hard

`ignore_changes` 로 관리 해제 vs `state rm` 차이는?

- A) 동일
- B) ignore_changes 는 특정 속성만, state rm 은 전체 리소스
- C) state rm 은 인프라 삭제, ignore_changes 는 유지
- D) 둘 다 인프라 삭제

<details><summary>정답 및 해설</summary>

**정답: B**

- ignore_changes: 리소스는 관리, 특정 속성 변경만 무시
- state rm: 리소스 자체 관리 해제 (실제 인프라 유지)
</details>

### 문제 17: 🟡 Medium

`terraform apply -target=aws_instance.web` 의 위험성은?

- A) 종속성 무시
- B) Config drift 유발
- C) 부분 apply 로 인프라 불일치
- D) 위 모두

<details><summary>정답 및 해설</summary>

**정답: D**

프로덕션에서는 지양. 응급 상황용.
</details>

### 문제 18: 🟢 Easy

Provider 문제 진단 명령어:

- A) `terraform providers`
- B) `terraform version`
- C) `terraform show`
- D) A, B 모두

<details><summary>정답 및 해설</summary>

**정답: D**

`terraform providers` 로 사용 중인 provider 확인, `terraform version` 으로 CLI + provider 버전.
</details>

### 문제 19: 🔴 Hard

CI/CD 에서 Terraform 실행 시 필요한 환경 변수는? (**Select TWO**)

- A) `TF_INPUT=false`
- B) `TF_IN_AUTOMATION=true`
- C) `TF_AUTO=1`
- D) `TF_QUIET=true`

<details><summary>정답 및 해설</summary>

**정답: A, B**

- `TF_INPUT=false`: 대화형 입력 비활성화
- `TF_IN_AUTOMATION=true`: 자동화 환경 (출력 조정)
</details>

### 문제 20: 🟡 Medium

`terraform force-unlock <LOCK_ID>` 를 사용해야 하는 상황은?

- A) Apply 시작할 때
- B) Stale lock 이 확실할 때
- C) 매일 정기적으로
- D) 다른 사람이 apply 중일 때

<details><summary>정답 및 해설</summary>

**정답: B**

Crash 등으로 lock 이 해제되지 않을 때만. 다른 사람 작업 중이면 위험.
</details>

### 문제 21: 🟢 Easy

Refactoring - Module 로 리소스 이동:

- A) `terraform state mv aws_vpc.main module.network.aws_vpc.main`
- B) `moved` block 사용 (권장)
- C) 코드에서 이동 후 apply
- D) A, B 모두 가능

<details><summary>정답 및 해설</summary>

**정답: D**

CLI 방식 (A) 또는 moved block (B). Moved block 이 권장.
</details>

### 문제 22: 🔴 Hard

Legacy state 를 새 Terraform 버전으로 마이그레이션 시 주의사항은? (**Select TWO**)

- A) State 백업 필수
- B) Version 호환성 확인
- C) 자동 마이그레이션이라 걱정 없음
- D) Provider 재다운로드

<details><summary>정답 및 해설</summary>

**정답: A, B**

Downgrade 는 대부분 불가능. 백업 + 호환성 확인 필수.
</details>

### 문제 23: 🟡 Medium

**True / False:** `terraform destroy` 후 State 는 비어있다.

<details><summary>정답 및 해설</summary>

**정답: True**

리소스 모두 destroy 후 state 는 outputs 등 minimal 만 유지.
</details>

### 문제 24: 🟢 Easy

Drift 발견 후 config 를 real 로 맞추는 방식은?

- A) `terraform apply -refresh-only`
- B) Config 수동 업데이트 후 `terraform plan`
- C) State 삭제
- D) `terraform destroy`

<details><summary>정답 및 해설</summary>

**정답: B**

Real 상태를 코드로 반영 후 plan 확인. No changes 이면 성공.
</details>

### 문제 25: 🔴 Hard

Deprecated 명령어를 대체하는 이유는?

- A) 성능
- B) UX 개선 및 명확성
- C) 하위 호환성
- D) Backend 지원

<details><summary>정답 및 해설</summary>

**정답: B**

`taint` 는 즉시 mark, `-replace` 는 plan 에서 확인 가능 (더 안전).
`refresh` 는 대화형 승인 없음, `apply -refresh-only` 는 승인 포함.
</details>

---

## 🎯 핵심 개념 정리

1. **Deprecated:** taint → apply -replace, refresh → apply -refresh-only
2. **Import:** CLI 방식 (기존) vs Block 방식 (1.5+, 권장)
3. **Refactoring:** moved (1.1+), removed (1.7+), import (1.5+) blocks
4. **Debug:** `TF_LOG=DEBUG`, `TF_LOG_PATH`
5. **Provider migration:** `terraform state replace-provider`
6. **CI/CD:** `TF_INPUT=false`, `TF_IN_AUTOMATION=true`
7. **force-unlock:** Stale lock 만 (위험!)

---

## 📚 관련 학습 자료

- [State 명령어](/archive/06-state/state-commands/)
- [Drift Detection](/archive/06-state/drift-detection/)
- [CLI 명령어](/archive/03-core-workflow/cli-commands/)
- [Lab 10: State 조작](/archive/labs/lab-10-state-manipulation/readme/)
