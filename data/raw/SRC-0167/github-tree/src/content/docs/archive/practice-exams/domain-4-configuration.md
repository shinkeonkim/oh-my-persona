---
title: "Domain 4 문제 35개 / Configuration"
description: "Thirty-five Terraform Associate 004 configuration practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 4 문제 35개입니다. Sensitive와 ephemeral의 차이는 [1.12 심화 포인트](/reference/terraform-1-12-deep-dive/)를 함께 확인하세요.

## 📚 도메인 개요

HCL, Variables, Outputs, Data Sources, Functions, Complex Types, Meta-arguments, Custom Conditions, Ephemeral Values를 다룹니다. HashiCorp는 공식 목표 목록에 domain별 가중치를 공개하지 않습니다.

---

## 📝 연습 문제

### 문제 1: 🟢 Easy

Resource vs Data Source 차이는?

- A) Resource 는 생성, Data Source 는 조회
- B) Resource 는 조회, Data Source 는 생성
- C) 같은 개념
- D) Resource 는 무료, Data Source 는 유료

<details><summary>정답 및 해설</summary>

**정답: A**

`resource` 는 인프라 생성/관리. `data` 는 기존 정보 조회 (읽기 전용).
</details>

### 문제 2: 🟢 Easy

`sensitive = true` 가 하는 일은?

- A) 값을 암호화
- B) State 파일에 저장 안 됨
- C) CLI 출력에서 숨김
- D) 자동 로테이션

<details><summary>정답 및 해설</summary>

**정답: C**

CLI 출력만 마스킹. State 파일에는 평문 저장! (주의)
</details>

### 문제 3: 🟡 Medium

count vs for_each 의 주요 차이는? (**Select TWO**)

- A) count 는 인덱스 기반
- B) for_each 는 키 기반
- C) count 만 module 에 사용 가능
- D) for_each 만 리스트에 사용 가능

<details><summary>정답 및 해설</summary>

**정답: A, B**

count: 인덱스, 중간 제거 시 재생성 위험.
for_each: 키 (map/set), 안전한 제거.
</details>

### 문제 4: 🟡 Medium

Variable Precedence (높음 → 낮음) 순서는?

- A) -var → tfvars → auto.tfvars → env → default
- B) -var → auto.tfvars → tfvars → env → default
- C) env → -var → tfvars → auto.tfvars → default
- D) default → tfvars → -var → env

<details><summary>정답 및 해설</summary>

**정답: B**

`-var` > `*.auto.tfvars` > `terraform.tfvars` > `TF_VAR_*` > default.
</details>

### 문제 5: 🔴 Hard

다음 중 for_each 에 직접 사용할 수 있는 타입은? (**Select TWO**)

- A) list(string)
- B) set(string)
- C) map(string)
- D) tuple

<details><summary>정답 및 해설</summary>

**정답: B, C**

for_each 는 set 또는 map 만. list 는 `toset()` 로 변환 필요.
</details>

### 문제 6: 🟢 Easy

Module Output 참조 형식은?

- A) `module.<name>.<output>`
- B) `output.<module>.<name>`
- C) `module.<output>.<name>`
- D) `<module>.output.<name>`

<details><summary>정답 및 해설</summary>

**정답: A**

`module.<MODULE_NAME>.<OUTPUT_NAME>`
</details>

### 문제 7: 🟡 Medium

Variable Validation 예제:

```hcl
variable "env" {
  type = string
  validation {
    condition = contains(["dev", "prod"], var.env)
    error_message = "Invalid env."
  }
}
```

`terraform apply -var="env=staging"` 결과는?

- A) 성공
- B) Error: Invalid env.
- C) 무시하고 계속
- D) 경고만

<details><summary>정답 및 해설</summary>

**정답: B**

Validation 실패 시 Apply 중단.
</details>

### 문제 8: 🔴 Hard

Custom Conditions 종류 4가지가 아닌 것은?

- A) Variable Validation
- B) Precondition
- C) Postcondition
- D) Refresh Check

<details><summary>정답 및 해설</summary>

**정답: D**

정답: Validation, Precondition, Postcondition, Check Block. Refresh Check 는 존재 안 함.
</details>

### 문제 9: 🟡 Medium

Check Block 의 특징은?

- A) 실패 시 apply 중단
- B) 경고만 표시 (non-blocking)
- C) Provider 다운로드 검증
- D) State 검증

<details><summary>정답 및 해설</summary>

**정답: B**

Check Block 은 non-blocking. 경고만 표시.
</details>

### 문제 10: 🔴 Hard

Ephemeral Values 는 언제 도입되었나요?

- A) Terraform 1.0
- B) Terraform 1.5
- C) Terraform 1.10
- D) Terraform 1.12

<details><summary>정답 및 해설</summary>

**정답: C**

Ephemeral variables: 1.10+. 004 시험 신규 영역.
</details>

### 문제 11: 🟡 Medium

`file("${path.module}/config.json")` 은 무엇을 하나요?

- A) 파일 생성
- B) 파일 내용을 문자열로 읽음
- C) 파일 삭제
- D) 파일 존재 확인

<details><summary>정답 및 해설</summary>

**정답: B**

`file()` 은 파일 내용을 string 으로 반환.
</details>

### 문제 12: 🟢 Easy

`length(["a", "b", "c"])` 결과는?

- A) 0
- B) 1
- C) 3
- D) "abc"

<details><summary>정답 및 해설</summary>

**정답: C**
</details>

### 문제 13: 🟡 Medium

`toset(["a", "b", "a", "c"])` 결과는?

- A) ["a", "b", "a", "c"]
- B) ["a", "b", "c"] (set)
- C) 4
- D) Error

<details><summary>정답 및 해설</summary>

**정답: B**

Set 은 중복 제거.
</details>

### 문제 14: 🔴 Hard

Dynamic Block 문법으로 올바른 것은?

- A) `for = var.rules { content { ... } }`
- B) `dynamic "ingress" { for_each = var.rules content { ... } }`
- C) `dynamic ingress = var.rules { ... }`
- D) `each { for_each = var.rules }`

<details><summary>정답 및 해설</summary>

**정답: B**

```hcl
dynamic "block_name" {
  for_each = collection
  content { ... }
}
```
</details>

### 문제 15: 🟡 Medium

`sensitive = true` 로 표시된 output 을 nonsensitive() 없이 참조하면?

- A) 자동으로 sensitive 로 전파
- B) 에러 발생
- C) 자동 마스킹 해제
- D) 무시됨

<details><summary>정답 및 해설</summary>

**정답: A**

Sensitive 값을 참조하는 것도 sensitive 로 전파.
</details>

### 문제 16: 🟢 Easy

`data "aws_ami" "ubuntu" {...}` 를 참조하는 방식은?

- A) `aws_ami.ubuntu.id`
- B) `data.aws_ami.ubuntu.id`
- C) `data.ubuntu.id`
- D) `${aws_ami.ubuntu.id}`

<details><summary>정답 및 해설</summary>

**정답: B**

Data source 는 `data.<TYPE>.<NAME>.<ATTR>`.
</details>

### 문제 17: 🔴 Hard

Locals 를 사용하는 이유가 **아닌** 것은?

- A) 반복 표현식 재사용
- B) 계산된 값 저장
- C) 코드 가독성
- D) 실행 순서 제어

<details><summary>정답 및 해설</summary>

**정답: D**

Locals 는 값 저장용. 실행 순서는 dependencies 로.
</details>

### 문제 18: 🟡 Medium

Write-only Arguments (Terraform 1.11+) 의 특징은?

- A) State 에 저장 안 됨
- B) CLI 출력에서만 숨김
- C) 자동 암호화
- D) 로테이션 자동

<details><summary>정답 및 해설</summary>

**정답: A**

Write-only 는 State 저장 안 됨. `password_wo_version` 으로 변경 감지.
</details>

### 문제 19: 🟡 Medium

`terraform_remote_state` data source 로 접근 가능한 것은?

- A) 원본 state 의 resources
- B) 원본 state 의 outputs
- C) 원본 state 의 variables
- D) 모든 데이터

<details><summary>정답 및 해설</summary>

**정답: B**

Outputs 만 접근 가능. Resource attribute 직접 접근 불가.
</details>

### 문제 20: 🟢 Easy

Object type 예시:

```hcl
variable "config" {
  type = object({
    name = string
    port = number
  })
}
```

`var.config.name` 참조 가능?

<details><summary>정답 및 해설</summary>

**정답: True**

Object 는 dot notation 으로 접근.
</details>

### 문제 21: 🔴 Hard

Precondition 이 postcondition 과 다른 점은? (**Select TWO**)

- A) Precondition 은 생성 전 실행
- B) Precondition 에서 self 사용 가능
- C) Postcondition 은 생성 후 실행
- D) Postcondition 에서 self 사용 가능

<details><summary>정답 및 해설</summary>

**정답: A, C, D**

Precondition: 생성 전, self 사용 불가.
Postcondition: 생성 후, self 사용 가능.
</details>

### 문제 22: 🟡 Medium

`cidrsubnet("10.0.0.0/16", 8, 2)` 결과는?

- A) 10.0.0.2/16
- B) 10.0.2.0/24
- C) 10.0.0.0/24
- D) 10.2.0.0/16

<details><summary>정답 및 해설</summary>

**정답: B**

`/16` + 8-bit 확장 = `/24`. index 2 = 10.0.2.0/24.
</details>

### 문제 23: 🟢 Easy

for expression 결과:

```hcl
[for s in ["a", "b"] : upper(s)]
```

- A) ["A", "B"]
- B) ["a", "b"]
- C) "AB"
- D) Error

<details><summary>정답 및 해설</summary>

**정답: A**

for expression 으로 list comprehension.
</details>

### 문제 24: 🔴 Hard

Terraform 이 자동 순서 결정하는 방식은?

- A) Alphabetical
- B) File order
- C) Dependency graph
- D) Random

<details><summary>정답 및 해설</summary>

**정답: C**

Terraform 은 리소스 간 참조를 분석하여 dependency graph 생성 → 병렬 처리.
</details>

### 문제 25: 🟡 Medium

`terraform.tfvars.json` 은 자동 로드되나요?

<details><summary>정답 및 해설</summary>

**정답: True**

JSON 형식도 자동 로드. HCL 과 동일 우선순위.
</details>

### 문제 26: 🟢 Easy

`merge({a=1}, {b=2}, {a=3})` 결과는?

- A) {a=3, b=2}
- B) {a=1, b=2}
- C) {a=1, a=3, b=2}
- D) Error

<details><summary>정답 및 해설</summary>

**정답: A**

나중 값이 우선 (a: 1 → 3).
</details>

### 문제 27: 🔴 Hard

`try(var.might_not_exist, "default")` 는?

- A) 항상 var 값 반환
- B) 에러 시 "default" 반환
- C) 항상 "default" 반환
- D) Error

<details><summary>정답 및 해설</summary>

**정답: B**

`try()` 는 첫 인자가 에러이면 다음 값 반환.
</details>

### 문제 28: 🟡 Medium

Splat expression `aws_instance.web[*].id` 는?

- A) 모든 인스턴스 삭제
- B) 모든 인스턴스의 id 리스트
- C) 첫 번째 인스턴스 id
- D) 마지막 인스턴스 id

<details><summary>정답 및 해설</summary>

**정답: B**

`[*]` 는 splat, 각 element 의 attribute 를 list 로 반환.
</details>

### 문제 29: 🟢 Easy

conditional expression:

```hcl
var.env == "prod" ? "t3.large" : "t2.micro"
```

`var.env = "staging"` 이면?

- A) "t3.large"
- B) "t2.micro"
- C) null
- D) Error

<details><summary>정답 및 해설</summary>

**정답: B**

조건이 false 이므로 두 번째 값.
</details>

### 문제 30: 🔴 Hard

Cross-variable validation (Terraform 1.9+) 예제:

```hcl
variable "max" {
  type = number
  validation {
    condition = var.max >= var.min
    error_message = "..."
  }
}
```

**True / False:** 이 기능은 Terraform 1.9 이전에도 가능했다.

<details><summary>정답 및 해설</summary>

**정답: False**

이전에는 다른 variable 참조 불가. 1.9+ 에서 지원.
</details>

### 문제 31: 🟡 Medium

Meta-arguments 가 **아닌** 것은?

- A) count
- B) for_each
- C) depends_on
- D) source

<details><summary>정답 및 해설</summary>

**정답: D**

`source` 는 module 의 argument. Meta-arguments: count, for_each, depends_on, provider, lifecycle.
</details>

### 문제 32: 🟢 Easy

**True / False:** Optional attributes 는 object 타입에서만 사용 가능하다.

<details><summary>정답 및 해설</summary>

**정답: True**

`optional()` 은 object type constraint 내에서만.
</details>

### 문제 33: 🔴 Hard

Templatefile 사용:

```hcl
templatefile("script.tpl", { name = "web" })
```

script.tpl:
```
Hello, ${name}
```

결과는?

- A) "Hello, ${name}"
- B) "Hello, web"
- C) Error
- D) "Hello, name"

<details><summary>정답 및 해설</summary>

**정답: B**

Templatefile 은 변수를 interpolate.
</details>

### 문제 34: 🟡 Medium

`ignore_changes = all` 의 효과는?

- A) 모든 변경 무시 (Terraform 이 관리 안 함)
- B) 리소스 삭제
- C) 자동 승인
- D) 로그만 출력

<details><summary>정답 및 해설</summary>

**정답: A**

거의 사용 안 함. Terraform 이 이 리소스를 관리하지 않는 것과 유사.
</details>

### 문제 35: 🟢 Easy

Ephemeral output (Terraform 1.11+) 의 특징은?

- A) State 에 저장 안 됨
- B) 실행 중에만 존재
- C) 다른 module 로 전달 가능
- D) 위 모두

<details><summary>정답 및 해설</summary>

**정답: D**

Ephemeral output 은 위 모두 해당.
</details>

---

## 🎯 핵심 개념 정리

1. **Resource vs Data:** 생성 vs 조회
2. **count vs for_each:** 인덱스 vs 키
3. **Variable Precedence:** -var > tfvars > env > default
4. **Sensitive 한계:** CLI 만 마스킹, State 는 평문
5. **Ephemeral (1.10+), Write-only (1.11+):** 004 신규
6. **Custom Conditions 4종:** Validation, Precondition, Postcondition, Check
7. **Meta-arguments:** count, for_each, depends_on, provider, lifecycle
8. **Dynamic blocks:** for_each + content

---

## 📚 관련 학습 자료

- [Configuration](/archive/04-configuration/readme/)
- [Variables 상세](/archive/04-configuration/variables-outputs/)
- [Functions](/archive/04-configuration/functions/)
- [Complex Types](/archive/04-configuration/complex-types/)
- [Data Sources](/archive/04-configuration/data-sources/)
- [Custom Conditions](/archive/07-lifecycle/custom-conditions/)
- [Sensitive Data](/archive/07-lifecycle/sensitive-data/)
