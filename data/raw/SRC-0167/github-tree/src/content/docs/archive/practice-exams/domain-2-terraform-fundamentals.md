---
title: "Domain 2 문제 20개 / Terraform Fundamentals"
description: "Twenty Terraform Associate 004 provider and state fundamentals practice questions."
---

> **Canonical 200 bank / 200문항 문제은행**  
> 이 페이지는 [200문항 인덱스](/practice/bank-200/)의 Domain 2 문제 20개입니다. Provider constraint와 lock selection은 서로 다른 개념입니다.

## 📚 도메인 개요

Provider, Plugin 아키텍처, Registry, Lock file 등 Terraform 의 기초 개념.

## 🎯 학습 목표

- Provider 이해 (version, alias)
- .terraform.lock.hcl 활용
- terraform init 심화
- Registry 및 Plugin 아키텍처

---

## 📝 연습 문제

### 문제 1: 🟢 Easy

Terraform Provider 의 역할은?

- A) State 파일 저장
- B) 외부 API 와 통신
- C) HCL 문법 검증
- D) 사용자 인증

<details><summary>정답 및 해설</summary>

**정답: B**

Provider 는 외부 서비스 (AWS, Azure 등) 의 API 를 Terraform 이 사용할 수 있게 하는 플러그인.
</details>

### 문제 2: 🟢 Easy

`.terraform.lock.hcl` 파일의 목적은?

- A) State 파일 잠금
- B) Provider 버전과 체크섬 고정
- C) 사용자 credentials 저장
- D) 백업 파일

<details><summary>정답 및 해설</summary>

**정답: B**

Provider version 과 체크섬을 고정하여 팀 전체가 동일한 provider 를 사용하도록 보장. Git 에 커밋 필수.
</details>

### 문제 3: 🟡 Medium

`terraform init` 이 수행하는 작업 3가지를 선택하세요. (**Select THREE**)

- A) Provider 다운로드
- B) Backend 초기화
- C) Child modules 다운로드
- D) 인프라 생성
- E) State 파일 삭제

<details><summary>정답 및 해설</summary>

**정답: A, B, C**

init 은: Provider 설치, Backend 설정, Module 다운로드. 인프라는 apply 로.
</details>

### 문제 4: 🟡 Medium

Provider version 제약이 올바른 것은?

- A) `version = "5.0"` — 정확히 5.0
- B) `version = "~> 5.1"` — 5.1.x 만
- C) `version = "~> 5.1"` — 5.1.x, 5.2.x, ..., 5.9.x (6.0 제외)
- D) `version = ">= 5.0"` — 5.0 만

<details><summary>정답 및 해설</summary>

**정답: C**

`~> 5.1` 은 pessimistic constraint. 마지막 자리 (여기서 minor) 만 자유롭게 증가.
</details>

### 문제 5: 🔴 Hard

Provider alias 를 사용하는 시나리오가 아닌 것은?

- A) 여러 AWS 계정 관리
- B) 다중 리전 배포
- C) 서로 다른 인증 방식
- D) State 파일 분리

<details><summary>정답 및 해설</summary>

**정답: D**

Provider alias 는 동일 provider 의 다른 configuration 을 사용하기 위함. State 분리는 workspace 또는 별도 프로젝트로.
</details>

### 문제 6: 🟡 Medium

**True / False:** `.terraform.lock.hcl` 은 `.gitignore` 에 추가해야 한다.

<details><summary>정답 및 해설</summary>

**정답: False**

Lock 파일은 **Git 에 커밋 필수**. 팀 재현성 보장.
</details>

### 문제 7: 🟢 Easy

Terraform Registry 의 공식 URL 은?

- A) hashicorp.com/registry
- B) registry.terraform.io
- C) terraform.hashicorp.com
- D) registry.hashicorp.com

<details><summary>정답 및 해설</summary>

**정답: B**

registry.terraform.io - Public Terraform Registry.
</details>

### 문제 8: 🟡 Medium

Provider source `hashicorp/aws` 는 전체 형식으로 무엇을 의미하나요?

- A) registry.terraform.io/hashicorp/aws
- B) app.terraform.io/hashicorp/aws
- C) github.com/hashicorp/aws
- D) hashicorp.com/aws

<details><summary>정답 및 해설</summary>

**정답: A**

축약형 `hashicorp/aws` = `registry.terraform.io/hashicorp/aws` (기본 hostname).
</details>

### 문제 9: 🔴 Hard

여러 리전에 배포하기 위한 Provider 설정으로 올바른 것은?

```hcl
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

resource "aws_instance" "example" {
  # ?
}
```

- A) `provider = aws.west`
- B) `region = "us-west-2"`
- C) `alias = "west"`
- D) `provider = "aws.west"`

<details><summary>정답 및 해설</summary>

**정답: A**

리소스에서 특정 alias provider 를 사용하려면 `provider = aws.west` (namespace.alias).
</details>

### 문제 10: 🟢 Easy

`terraform init -upgrade` 의 목적은?

- A) Terraform CLI 업그레이드
- B) Provider 를 최신 버전으로 업데이트
- C) State 파일 마이그레이션
- D) Backend 재구성

<details><summary>정답 및 해설</summary>

**정답: B**

`-upgrade` 는 provider 및 module 을 constraint 내에서 최신 버전으로 업데이트.
</details>

### 문제 11: 🟡 Medium

Terraform Provider Plugin 은 어디에 저장되나요?

- A) ~/.terraform/
- B) .terraform/providers/
- C) /usr/local/terraform/
- D) State 파일 내부

<details><summary>정답 및 해설</summary>

**정답: B**

`.terraform/providers/registry.terraform.io/<NAMESPACE>/<NAME>/<VERSION>/<OS_ARCH>/`
</details>

### 문제 12: 🔴 Hard

**True / False:** `terraform init` 없이 `terraform plan` 을 실행할 수 있다.

<details><summary>정답 및 해설</summary>

**정답: False**

Provider 가 다운로드되어 있지 않아 실행 불가. `terraform init` 이 선행되어야 함.
</details>

### 문제 13: 🟡 Medium

Provider version constraint 예시 중 **가장 안전한** (프로덕션) 것은?

- A) `version = "5.31.0"` (정확한 버전)
- B) `version = ">= 5.0"`
- C) `version` 생략
- D) `version = "*"`

<details><summary>정답 및 해설</summary>

**정답: A**

프로덕션은 정확한 버전 pin 이 가장 안전. 자동 업그레이드 방지.
개발은 `~> 5.0` 정도가 유연성/안전 밸런스.
</details>

### 문제 14: 🟡 Medium

Multi-platform 개발 팀 (macOS, Linux, Windows) 을 위한 lock file 준비 방법은?

- A) `terraform init`
- B) `terraform providers lock -platform=<OS>`
- C) `terraform providers mirror`
- D) 수동으로 hash 추가

<details><summary>정답 및 해설</summary>

**정답: B**

```bash
terraform providers lock \
  -platform=darwin_amd64 \
  -platform=linux_amd64 \
  -platform=windows_amd64
```
</details>

### 문제 15: 🟢 Easy

Terraform Community Provider vs Verified Provider 차이는?

- A) 성능
- B) HashiCorp 검증 여부
- C) 언어 지원
- D) 라이선스 비용

<details><summary>정답 및 해설</summary>

**정답: B**

Verified = HashiCorp 파트너/공식 검증. Community = 커뮤니티 유지관리.
</details>

### 문제 16: 🔴 Hard

특정 리전 Provider 를 default 로 하고 다른 리전은 alias 로 사용:

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu"
  region = "eu-west-1"
}
```

**True / False:** default provider 를 사용하는 리소스에는 `provider` argument 를 명시해야 한다.

<details><summary>정답 및 해설</summary>

**정답: False**

Default provider (alias 없음) 는 자동으로 사용. Alias 사용 시에만 명시적 `provider = aws.eu`.
</details>

### 문제 17: 🟡 Medium

Terraform 1.12 의 신규 기능이 **아닌** 것은?

- A) Ephemeral values
- B) Write-only arguments
- C) Custom conditions
- D) moved block

<details><summary>정답 및 해설</summary>

**정답: D**

moved block 은 Terraform 1.1+. 다른 것들은 1.10+, 1.11+.
</details>

### 문제 18: 🟢 Easy

Terraform CLI 를 어떻게 설치하나요? (**Select TWO**)

- A) `brew install terraform` (macOS)
- B) `apt install terraform` (Ubuntu)
- C) `choco install terraform` (Windows)
- D) `npm install terraform`

<details><summary>정답 및 해설</summary>

**정답: A, B, C**

npm 은 Node.js 패키지. Terraform 은 Go 로 작성된 단일 바이너리.
</details>

### 문제 19: 🔴 Hard

`terraform init` 실행 시 오류 발생: `Error: Failed to query available provider packages`

가능한 원인이 **아닌** 것은?

- A) 인터넷 연결 없음
- B) Provider registry 접근 불가
- C) 잘못된 provider source
- D) State 파일 손상

<details><summary>정답 및 해설</summary>

**정답: D**

State 파일은 init 단계에서 접근하지 않음. Provider 다운로드 관련 문제.
</details>

### 문제 20: 🟡 Medium

Private Registry 를 사용하는 provider 참조는?

- A) `hashicorp/aws`
- B) `app.terraform.io/my-org/custom`
- C) `github.com/my-org/aws`
- D) `custom.company.com/aws`

<details><summary>정답 및 해설</summary>

**정답: B**

Private Registry 는 `<hostname>/<namespace>/<name>` 형식. HCP Terraform 은 `app.terraform.io`.
</details>

---

## 🎯 핵심 개념 정리

1. **Provider = 외부 API 통신 플러그인**
2. **`.terraform.lock.hcl` = 버전 고정 (Git 커밋 필수)**
3. **`init` = Provider + Backend + Module 초기화**
4. **Version constraint: `~>` (Pessimistic)**
5. **Registry: registry.terraform.io (Public)**
6. **Alias: 동일 provider 여러 configuration**

---

## 📚 관련 학습 자료

- [Week 1-2: IaC 개념](/archive/01-iac-concepts/readme/)
- [Module Versioning](/archive/05-modules/versioning/)
- [Module Registry](/archive/05-modules/registry/)
