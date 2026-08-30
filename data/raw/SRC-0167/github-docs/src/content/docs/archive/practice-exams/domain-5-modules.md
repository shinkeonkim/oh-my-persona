---
title: "Domain 5 문제 25개 / Modules"
description: "Twenty-five Terraform Associate 004 module practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 5 문제 25개입니다. Module source와 provider dependency의 version 방식을 구분하세요.

## 📚 도메인 개요

Module 구조, sourcing, versioning, composition.

---

## 📝 연습 문제

### 문제 1: 🟢 Easy

Module 의 주요 목적이 **아닌** 것은?

- A) 재사용성
- B) 조직화
- C) 표준화
- D) 성능 향상

<details><summary>정답 및 해설</summary>

**정답: D**

Module 은 코드 재사용 도구. 성능과는 무관.
</details>

### 문제 2: 🟢 Easy

표준 Module 파일 3가지는?

- A) main.tf, variables.tf, outputs.tf
- B) init.tf, resources.tf, config.tf
- C) module.tf, input.tf, output.tf
- D) tf.main, tf.var, tf.out

<details><summary>정답 및 해설</summary>

**정답: A**

표준: main.tf, variables.tf, outputs.tf (+ versions.tf, README.md)
</details>

### 문제 3: 🟡 Medium

Module Source 5가지 유형에 포함되지 않는 것은?

- A) Local path
- B) Terraform Registry
- C) GitHub
- D) FTP

<details><summary>정답 및 해설</summary>

**정답: D**

지원: Local, Registry, GitHub, Git, HTTP, S3, GCS. FTP 는 없음.
</details>

### 문제 4: 🟡 Medium

Registry module source 문법은?

- A) `<hostname>/<name>/<provider>`
- B) `<namespace>/<name>/<provider>`
- C) `<namespace>/<provider>/<name>`
- D) `<provider>/<namespace>/<name>`

<details><summary>정답 및 해설</summary>

**정답: B**

예: `terraform-aws-modules/vpc/aws`
</details>

### 문제 5: 🔴 Hard

Version constraint `~> 5.1` 이 매칭하는 버전은?

- A) 5.1.0 만
- B) 5.1.0 ~ 5.9.9
- C) 5.0 ~ 6.0
- D) 6.0 이상

<details><summary>정답 및 해설</summary>

**정답: B**

`~> 5.1` = `>= 5.1, < 6.0`
</details>

### 문제 6: 🟡 Medium

`~> 5.1.0` 이 매칭하는 버전은?

- A) 5.1.0 만
- B) 5.1.0 ~ 5.1.9
- C) 5.1.0 ~ 5.9.9
- D) 6.0 미만

<details><summary>정답 및 해설</summary>

**정답: B**

`~> 5.1.0` = `>= 5.1.0, < 5.2.0`
</details>

### 문제 7: 🟢 Easy

Module output 참조:

- A) `module.vpc.vpc_id`
- B) `output.vpc.vpc_id`
- C) `vpc.output.vpc_id`
- D) `vpc.vpc_id`

<details><summary>정답 및 해설</summary>

**정답: A**

`module.<NAME>.<OUTPUT>`
</details>

### 문제 8: 🟡 Medium

GitHub module with specific tag:

- A) `source = "github.com/user/repo"`
- B) `source = "github.com/user/repo?ref=v1.0"`
- C) `source = "github.com/user/repo@v1.0"`
- D) `source = "github.com/user/repo:v1.0"`

<details><summary>정답 및 해설</summary>

**정답: B**

`?ref=<TAG_OR_BRANCH>` 사용.
</details>

### 문제 9: 🟢 Easy

**True / False:** Module 은 다른 Module 을 호출할 수 있다.

<details><summary>정답 및 해설</summary>

**정답: True**

Nested modules 가능. Module composition.
</details>

### 문제 10: 🔴 Hard

Root Module 의 variable 이 Child Module 에 자동으로 전달되나요?

<details><summary>정답 및 해설</summary>

**정답: False**

각 module 은 독립. Root variable 을 명시적으로 전달해야 함.
</details>

### 문제 11: 🟡 Medium

Terraform Registry 공식 URL 은?

- A) registry.terraform.io
- B) terraform.io/registry
- C) hashicorp.com/registry
- D) app.terraform.io

<details><summary>정답 및 해설</summary>

**정답: A**
</details>

### 문제 12: 🔴 Hard

Module 의 `providers` argument 는 언제 사용?

- A) Module 이 새 provider 를 정의할 때
- B) Root 의 다른 provider (alias) 를 module 에 전달할 때
- C) Provider version 지정
- D) 사용할 수 없음

<details><summary>정답 및 해설</summary>

**정답: B**

```hcl
module "example" {
  source = "./module"
  providers = {
    aws = aws.west
  }
}
```
</details>

### 문제 13: 🟡 Medium

**True / False:** Module 내부에서 provider 를 정의하는 것은 권장된다.

<details><summary>정답 및 해설</summary>

**정답: False**

Provider 는 root module 에서 정의. Child module 은 상속.
</details>

### 문제 14: 🟢 Easy

Registry Verified 뱃지의 의미는?

- A) HashiCorp 유료 지원
- B) 커뮤니티 인증
- C) HashiCorp 파트너/공식 검증
- D) 오픈소스

<details><summary>정답 및 해설</summary>

**정답: C**
</details>

### 문제 15: 🟡 Medium

Private Registry (HCP Terraform) 참조:

- A) `hashicorp/vpc/aws`
- B) `app.terraform.io/my-org/vpc/aws`
- C) `mycompany/vpc/aws`
- D) `private/vpc/aws`

<details><summary>정답 및 해설</summary>

**정답: B**

`<HOSTNAME>/<NAMESPACE>/<NAME>/<PROVIDER>`
</details>

### 문제 16: 🔴 Hard

`terraform get` 명령어는?

- A) 리소스 조회
- B) State 다운로드
- C) Module 다운로드
- D) Output 조회

<details><summary>정답 및 해설</summary>

**정답: C**

`terraform init` 에 포함된 단계. Module 만 재다운로드.
</details>

### 문제 17: 🟡 Medium

Module test file 확장자는? (Terraform 1.6+)

- A) `.tftest.hcl`
- B) `_test.tf`
- C) `.test.hcl`
- D) `.tf.test`

<details><summary>정답 및 해설</summary>

**정답: A**

`example.tftest.hcl`
</details>

### 문제 18: 🟢 Easy

Module 을 재사용하는 방법:

```hcl
module "vpc_dev" { source = "./modules/vpc" }
module "vpc_prod" { source = "./modules/vpc" }
```

**True / False:** 두 module 은 독립된 State 를 가진다.

<details><summary>정답 및 해설</summary>

**정답: False**

State 는 동일 (root module 의 state).
Module 은 코드 재사용이지 state 분리 아님.
</details>

### 문제 19: 🔴 Hard

Version 없이 registry module 사용:

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  # version 없음
}
```

- A) 항상 최신 다운로드 (매번)
- B) 첫 init 시 최신, 이후 lock
- C) Error
- D) 이전 버전 사용

<details><summary>정답 및 해설</summary>

**정답: A**

Version 없으면 매 init 마다 최신. 예측 불가.
</details>

### 문제 20: 🟡 Medium

Module 의 output 이 module 밖에서 접근되려면?

- A) 그냥 정의
- B) `sensitive = true`
- C) `depends_on` 필요
- D) 자동 노출

<details><summary>정답 및 해설</summary>

**정답: A**

Module output 은 자동으로 module.<name>.<output> 로 접근 가능.
</details>

### 문제 21: 🔴 Hard

Sub-module 참조 문법 (Registry):

- A) `terraform-aws-modules/security-group/aws.web`
- B) `terraform-aws-modules/security-group/aws//modules/web`
- C) `terraform-aws-modules/security-group/aws/web`
- D) 지원 안 됨

<details><summary>정답 및 해설</summary>

**정답: B**

`//` 로 subdirectory 참조.
</details>

### 문제 22: 🟡 Medium

Best Practice: Module 개발자의 version constraint 는?

- A) 정확한 버전 (`= 5.1.2`)
- B) 최소 버전 (`>= 5.0`)
- C) Version 생략
- D) 매번 변경

<details><summary>정답 및 해설</summary>

**정답: B**

Module 개발자: 최소 버전만 (사용자 유연성).
Root: pessimistic (`~> 5.1`) 또는 pin.
</details>

### 문제 23: 🟢 Easy

Module 의 examples/ 디렉토리 목적은?

- A) 필수 파일
- B) 사용 예제 제공
- C) 테스트만
- D) 자동 생성

<details><summary>정답 및 해설</summary>

**정답: B**

사용자에게 예제 제공. 선택이지만 권장.
</details>

### 문제 24: 🔴 Hard

Local module 을 registry module 로 변경 시 필요한 조치는?

- A) State 만 그대로
- B) `terraform init -upgrade` 실행
- C) `terraform init` 실행
- D) 자동 전환

<details><summary>정답 및 해설</summary>

**정답: C**

Source 변경 후 `terraform init` 필요. State 는 module.<name>.<resource> 유지.
</details>

### 문제 25: 🟡 Medium

Module 에 `count` 사용 (Terraform 0.13+):

```hcl
module "vpc" {
  source = "./modules/vpc"
  count  = var.enabled ? 1 : 0
}
```

`module.vpc[0].vpc_id` 참조 가능?

<details><summary>정답 및 해설</summary>

**정답: True**

Module 에도 count/for_each 가능. 인덱스로 접근.
</details>

---

## 🎯 핵심 개념 정리

1. **표준 파일:** main.tf, variables.tf, outputs.tf, versions.tf
2. **Source:** Local, Registry, GitHub, Git, HTTP, S3, GCS
3. **Registry:** `<namespace>/<name>/<provider>`
4. **Version:** `~>` (pessimistic), `=` (pin), `>=` (min)
5. **Output 참조:** `module.<NAME>.<OUTPUT>`
6. **Sub-module:** `//modules/<name>` 문법
7. **Provider 상속:** Root 에서 정의, child 는 자동 상속

---

## 📚 관련 학습 자료

- [Modules](/archive/05-modules/readme/)
- [Module 작성](/archive/05-modules/creating-modules/)
- [Registry](/archive/05-modules/registry/)
- [Versioning](/archive/05-modules/versioning/)
