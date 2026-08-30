---
title: "Terraform Associate (004) 모의고사 Set 2"
description: "Legacy study material imported from practice-exams/mock-exam-set-2.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

**시험 정보:**
- 문제 수: 57문항
- 제한 시간: 60분
- 합격 기준: 약 70% (40문항 이상)
- 문제 유형: True/False, Multiple Choice, Multiple Answer

**시험 규칙:**
1. 타이머를 60분으로 설정하세요
2. 모든 문제를 순서대로 풀어주세요
3. 확실하지 않은 문제는 플래그하고 나중에 재검토하세요
4. 실제 시험처럼 메모나 검색 없이 풀어보세요

---

## Domain 1: Infrastructure as Code Concepts (6% / ~3 questions)

### Question 1 🟢
**What is the primary benefit of using Infrastructure as Code over manual configuration?**

A) Faster initial setup time  
B) No need for documentation  
C) Reproducibility and version control  
D) Eliminates the need for testing

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
IaC의 주요 이점은 **재현 가능성(Reproducibility)**과 **버전 관리**입니다.

**IaC 장점:**
1. **재현성**: 동일한 인프라를 반복적으로 생성 가능
2. **버전 관리**: Git으로 변경 이력 추적
3. **협업**: 팀 전체가 동일한 구성 공유
4. **자동화**: CI/CD 파이프라인 통합
5. **문서화**: 코드 자체가 문서

**틀린 선택지:**
- A) 초기 설정은 오히려 시간이 더 걸릴 수 있음
- B) 문서화는 여전히 필요 (README, 주석 등)
- D) 테스트는 여전히 필요 (terraform plan으로 검증)

**참고:**
- [Infrastructure as Code](https://developer.hashicorp.com/terraform/intro)
</details>

---

### Question 2 🟡
**Which statement best describes Terraform's approach to Infrastructure as Code?**

A) Imperative - you specify how to create infrastructure step by step  
B) Declarative - you specify what the desired state should be  
C) Procedural - you write scripts that execute in sequence  
D) Object-oriented - you define classes for infrastructure components

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
Terraform은 **선언적(Declarative)** 접근 방식을 사용합니다.

**Declarative vs Imperative:**

| Declarative (선언적) | Imperative (명령적) |
|---------------------|---------------------|
| "무엇을" 원하는지 정의 | "어떻게" 만들지 정의 |
| 최종 상태 명시 | 단계별 명령어 |
| Terraform, Kubernetes | Bash scripts, Ansible tasks |
| 멱등성(Idempotent) | 순서 의존적 |

**Terraform 예시 (Declarative):**
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```
→ "이런 인스턴스가 있어야 한다"

**Bash 예시 (Imperative):**
```bash
aws ec2 run-instances \
  --image-id ami-12345678 \
  --instance-type t2.micro
```
→ "이 명령을 실행하라"

**참고:**
- [Terraform Language](https://developer.hashicorp.com/terraform/language)
</details>

---

### Question 3 🟢
**True or False: Terraform can only manage cloud resources, not on-premises infrastructure.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: False**

**설명:**
Terraform은 **클라우드뿐만 아니라 온프레미스 인프라도 관리** 가능합니다.

**Terraform이 지원하는 환경:**
- **Public Cloud**: AWS, Azure, GCP
- **Private Cloud**: OpenStack, VMware vSphere
- **On-Premises**: Physical servers (via custom providers)
- **SaaS**: GitHub, Datadog, PagerDuty
- **Databases**: PostgreSQL, MySQL
- **Networking**: Cisco, Palo Alto Networks

**예시 - VMware vSphere (온프레미스):**
```hcl
provider "vsphere" {
  user           = "administrator@vsphere.local"
  password       = var.vsphere_password
  vsphere_server = "vcenter.example.com"
}

resource "vsphere_virtual_machine" "vm" {
  name             = "terraform-test"
  resource_pool_id = data.vsphere_resource_pool.pool.id
  datastore_id     = data.vsphere_datastore.datastore.id
  # ...
}
```

**참고:**
- [Terraform Providers](https://registry.terraform.io/browse/providers)
</details>

---

## Domain 2: Terraform Fundamentals (10% / ~6 questions)

### Question 4 🟡
**What is stored in the `.terraform.lock.hcl` file?**

A) Terraform state data  
B) Provider plugin binaries  
C) Exact provider versions and checksums  
D) Terraform configuration backup

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
`.terraform.lock.hcl`은 **Dependency Lock File**로, Provider 버전과 체크섬을 저장합니다.

**Lock 파일의 목적:**
1. **일관성 보장**: 모든 팀원이 동일한 Provider 버전 사용
2. **보안**: 체크섬으로 무결성 검증
3. **재현성**: 동일한 환경 재구성 가능

**Lock 파일 예시:**
```hcl
provider "registry.terraform.io/hashicorp/aws" {
  version     = "5.31.0"
  constraints = "~> 5.0"
  hashes = [
    "h1:abc123...",
    "zh:def456...",
  ]
}
```

**파일 위치 및 관리:**
- 프로젝트 루트에 생성
- Git에 **반드시 커밋** (팀 협업)
- `terraform init -upgrade`로 업데이트

**틀린 선택지:**
- A) State는 `terraform.tfstate`에 저장
- B) Plugin 바이너리는 `.terraform/` 디렉토리
- D) 백업 기능 없음

**참고:**
- [Dependency Lock File](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
</details>

---

### Question 5 🟢
**Which command initializes a Terraform working directory?**

A) terraform start  
B) terraform init  
C) terraform setup  
D) terraform install

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
`terraform init`은 작업 디렉토리를 초기화하는 명령어입니다.

**terraform init이 하는 일:**
1. Backend 초기화
2. Provider 플러그인 다운로드
3. Child 모듈 다운로드
4. `.terraform.lock.hcl` 생성/업데이트

**사용 예시:**
```bash
terraform init

terraform init -upgrade

terraform init -backend-config="bucket=my-state-bucket"

terraform init -reconfigure
```

**옵션:**
- `-upgrade`: Provider 버전 업그레이드
- `-reconfigure`: Backend 재구성
- `-backend=false`: Backend 초기화 건너뛰기

**참고:**
- [terraform init](https://developer.hashicorp.com/terraform/cli/commands/init)
</details>

---

### Question 6 🟡
**You need to use two different AWS accounts in the same Terraform configuration. What should you do?**

A) Create two separate Terraform projects  
B) Use provider aliases  
C) Switch AWS credentials between applies  
D) This is not possible in Terraform

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**Provider Aliases**를 사용하여 동일한 Provider의 여러 구성을 정의할 수 있습니다.

**구현 방법:**
```hcl
provider "aws" {
  region = "us-east-1"
  profile = "account-a"
}

provider "aws" {
  alias   = "account_b"
  region  = "us-west-2"
  profile = "account-b"
}

resource "aws_instance" "account_a" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

resource "aws_instance" "account_b" {
  provider      = aws.account_b
  ami           = "ami-87654321"
  instance_type = "t2.micro"
}
```

**주요 사용 사례:**
- 여러 AWS 계정 관리
- 다중 리전 배포
- 다른 환경 (dev/prod)

**참고:**
- [Provider Aliases](https://developer.hashicorp.com/terraform/language/providers/configuration#alias-multiple-provider-configurations)
</details>

---

### Question 7 🔴
**Which of the following statements about Terraform providers are correct? (Select TWO)**

⬜ A) Providers are installed globally and shared across all Terraform projects  
⬜ B) Each provider has its own versioning independent of Terraform  
⬜ C) Providers are automatically upgraded to the latest version on every `terraform init`  
⬜ D) The `.terraform.lock.hcl` file locks provider versions  
⬜ E) Provider configuration must be in a file named `providers.tf`

<details>
<summary>정답 보기</summary>

**답: B, D**

**설명:**

**B) True - Provider는 독립적인 버전 관리:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}
```

**D) True - Lock 파일이 버전 고정:**
```hcl
provider "registry.terraform.io/hashicorp/aws" {
  version     = "5.31.0"
  constraints = "~> 5.0"
}
```

**틀린 선택지:**

**A) False - Provider는 프로젝트별로 설치:**
```
project-a/
├── .terraform/
│   └── providers/
│       └── hashicorp/aws/5.31.0/

project-b/
├── .terraform/
│   └── providers/
│       └── hashicorp/aws/5.20.0/
```

**C) False - Lock 파일이 있으면 자동 업그레이드 안 됨:**
```bash
terraform init

terraform init -upgrade
```

**E) False - 파일 이름 제약 없음:**
```hcl
main.tf
configuration.tf
anything.tf
```

**참고:**
- [Providers Documentation](https://developer.hashicorp.com/terraform/language/providers)
</details>

---

### Question 8 🟡
**What does the `source` attribute in the `required_providers` block specify?**

A) The URL to download the provider  
B) The local path to the provider binary  
C) The provider's global unique identifier  
D) The Git repository of the provider

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
`source`는 Provider의 **전역 고유 식별자**입니다.

**Source 형식:**
```
[<HOSTNAME>/]<NAMESPACE>/<TYPE>
```

**예시:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "~> 5.0"
    }
    
    custom = {
      source  = "example.com/mycompany/custom-provider"
      version = "1.0.0"
    }
  }
}
```

**구성 요소:**
- **Hostname** (선택): `registry.terraform.io` (기본값)
- **Namespace**: `hashicorp`
- **Type**: `aws`

**단축 형식:**
```hcl
source = "hashicorp/aws"
```

**참고:**
- [Provider Requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
</details>

---

### Question 9 🟡
**True or False: Terraform automatically detects and uses the latest compatible provider version if no version is specified.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: True**

**설명:**
버전을 명시하지 않으면 Terraform은 **최신 버전**을 다운로드합니다.

**버전 미지정:**
```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}
```
→ 최신 버전 사용 (예: 5.40.0)

**권장 방법 - 버전 제약 명시:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

**버전 제약 연산자:**
```hcl
version = "5.31.0"
version = ">= 5.0.0"
version = "~> 5.0"
version = ">= 5.0, < 6.0"
```

**프로덕션 Best Practice:**
- 항상 버전 제약 명시
- Lock 파일 Git 커밋
- 정기적인 업그레이드 계획

**참고:**
- [Version Constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints)
</details>

---

## Domain 3: Core Terraform Workflow (16% / ~9 questions)

### Question 10 🟢
**In what order should you run Terraform commands for a new project?**

A) apply → init → plan → validate  
B) init → validate → plan → apply  
C) validate → init → plan → apply  
D) plan → init → validate → apply

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
올바른 순서:
```
1. terraform init
2. terraform validate
3. terraform plan
4. terraform apply
```

**각 단계 설명:**

**1. init** - 초기화
```bash
terraform init
```
- Provider 다운로드
- Backend 초기화
- 모듈 다운로드

**2. validate** - 검증 (선택)
```bash
terraform validate
```
- 구문 검사
- 로컬에서만 동작

**3. plan** - 계획
```bash
terraform plan
```
- 실행 계획 생성
- API 호출

**4. apply** - 적용
```bash
terraform apply
```
- 인프라 변경
- State 업데이트

**참고:**
- [Core Workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
</details>

---

### Question 11 🟡
**What is the difference between `terraform plan` and `terraform apply` without the `-auto-approve` flag?**

A) No difference, they do the same thing  
B) `plan` creates a plan file; `apply` executes it  
C) `plan` shows changes; `apply` shows changes and prompts for confirmation  
D) `plan` is read-only; `apply` modifies infrastructure

<details>
<summary>정답 보기</summary>

**답: C와 D 모두 맞지만, 가장 정확한 답은 C**

**실제 시험에서는 C가 정답**

**설명:**

**terraform plan:**
- 실행 계획만 생성
- 변경 사항 표시
- State refresh (기본)
- **인프라 수정 안 함**

**terraform apply (without -auto-approve):**
- 계획 생성
- 변경 사항 표시
- **사용자 승인 대기**
- 승인 후 인프라 수정

**예시:**
```bash
$ terraform plan
Plan: 1 to add, 0 to change, 0 to destroy.

$ terraform apply
Plan: 1 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Enter a value: yes

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

**참고:**
- [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [terraform apply](https://developer.hashicorp.com/terraform/cli/commands/apply)
</details>

---

### Question 12 🟢
**Which command formats Terraform configuration files to a canonical style?**

A) terraform style  
B) terraform format  
C) terraform fmt  
D) terraform beautify

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
`terraform fmt`는 코드를 **표준 형식**으로 포맷팅합니다.

**사용법:**
```bash
terraform fmt

terraform fmt -recursive

terraform fmt -check

terraform fmt -diff
```

**Before fmt:**
```hcl
resource"aws_instance""example"{
ami="ami-12345678"
instance_type="t2.micro"
tags={Name="Server"}}
```

**After fmt:**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  tags = {
    Name = "Server"
  }
}
```

**CI/CD 활용:**
```bash
terraform fmt -check -recursive
if [ $? -ne 0 ]; then
  echo "Format check failed"
  exit 1
fi
```

**참고:**
- [terraform fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt)
</details>

---

### Question 13 🟡
**Which command would you use to see the current state without making any changes?**

A) terraform show  
B) terraform state list  
C) terraform output  
D) All of the above

<details>
<summary>정답 보기</summary>

**답: D**

**설명:**
세 명령어 모두 State를 **읽기만** 하고 변경하지 않습니다.

**1. terraform show:**
```bash
$ terraform show

resource "aws_instance" "example" {
    ami           = "ami-12345678"
    id            = "i-1234567890abcdef0"
    instance_type = "t2.micro"
}
```
→ 전체 State 내용 표시

**2. terraform state list:**
```bash
$ terraform state list
aws_instance.example
aws_s3_bucket.data
module.vpc.aws_vpc.main
```
→ 리소스 목록만 표시

**3. terraform output:**
```bash
$ terraform output
instance_ip = "54.123.45.67"
bucket_name = "my-bucket"
```
→ Outputs만 표시

**차이점:**
| 명령어 | 출력 내용 |
|--------|----------|
| `show` | 전체 State 상세 |
| `state list` | 리소스 주소 목록 |
| `output` | Output 값만 |

**참고:**
- [terraform show](https://developer.hashicorp.com/terraform/cli/commands/show)
</details>

---

### Question 14 🔴
**You run `terraform plan` and see no changes. What could be the reasons? (Select TWO)**

⬜ A) The infrastructure matches the configuration  
⬜ B) Terraform is not connected to the provider  
⬜ C) The state file is empty  
⬜ D) All resources are configured with `prevent_destroy`  
⬜ E) The configuration has not changed since the last apply

<details>
<summary>정답 보기</summary>

**답: A, E**

**설명:**

**A) True - 인프라가 구성과 일치:**
```bash
$ terraform plan
No changes. Your infrastructure matches the configuration.
```
→ 실제 인프라가 원하는 상태

**E) True - 구성 변경 없음:**
구성 파일을 수정하지 않았고, 외부 Drift도 없으면 변경사항 없음

**틀린 선택지:**

**B) False - Provider 연결 실패 시 에러:**
```bash
Error: error configuring Terraform AWS Provider
```

**C) False - State 비어있으면 모든 리소스 생성 계획:**
```bash
Plan: 10 to add, 0 to change, 0 to destroy.
```

**D) False - prevent_destroy는 삭제만 방지:**
```hcl
lifecycle {
  prevent_destroy = true
}
```
→ 생성/수정은 가능, 삭제만 차단

**참고:**
- [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
</details>

---

### Question 15 🟡
**What does `terraform plan -out=tfplan` do?**

A) Writes the plan output to a text file  
B) Saves the execution plan in binary format  
C) Creates a backup of the state file  
D) Exports the plan to JSON format

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
`-out` 옵션은 실행 계획을 **바이너리 형식**으로 저장합니다.

**사용 패턴:**
```bash
terraform plan -out=tfplan

terraform show tfplan

terraform apply tfplan
```

**장점:**
1. **일관성**: Plan과 Apply 간 변경 없음 보장
2. **승인 프로세스**: Plan 검토 후 나중에 Apply
3. **CI/CD**: Plan 단계와 Apply 단계 분리

**예시 워크플로우:**
```bash
terraform plan -out=tfplan
if [ $? -eq 0 ]; then
  terraform show tfplan | grep "Plan:"
  echo "Review the plan above. Run 'terraform apply tfplan' to apply."
fi

terraform apply tfplan
```

**Plan 파일 확인:**
```bash
terraform show tfplan

terraform show -json tfplan | jq '.'
```

**주의사항:**
- Plan 파일은 민감 정보 포함 가능
- Git에 커밋하지 말 것
- 짧은 유효 기간 (State 변경 시 무효화)

**참고:**
- [terraform plan -out](https://developer.hashicorp.com/terraform/cli/commands/plan#out-filename)
</details>

---

### Question 16 🟡
**Which commands will modify the Terraform state? (Select TWO)**

⬜ A) terraform plan  
⬜ B) terraform apply  
⬜ C) terraform destroy  
⬜ D) terraform show  
⬜ E) terraform validate

<details>
<summary>정답 보기</summary>

**답: B, C**

**설명:**

**B) terraform apply - State 업데이트:**
```bash
$ terraform apply
Apply complete! Resources: 2 added, 1 changed, 0 destroyed.
```
→ `terraform.tfstate` 수정됨

**C) terraform destroy - State에서 제거:**
```bash
$ terraform destroy
Destroy complete! Resources: 3 destroyed.
```
→ State 파일 비워짐

**State를 수정하지 않는 명령어:**

**A) terraform plan:**
- State refresh만 (메모리에서)
- 파일은 수정 안 함

**D) terraform show:**
- 읽기 전용

**E) terraform validate:**
- State 접근 안 함

**State 수정 명령어 전체 목록:**
```bash
terraform apply
terraform destroy
terraform import
terraform state mv
terraform state rm
terraform state replace-provider
```

**참고:**
- [Terraform State](https://developer.hashicorp.com/terraform/language/state)
</details>

---

### Question 17 🔴
**You want to destroy only a specific resource without affecting others. Which command should you use?**

A) `terraform destroy aws_instance.example`  
B) `terraform destroy -target=aws_instance.example`  
C) `terraform apply -destroy -target=aws_instance.example`  
D) Both B and C are correct

<details>
<summary>정답 보기</summary>

**답: D**

**설명:**
두 명령어 모두 특정 리소스만 삭제합니다.

**방법 1:**
```bash
terraform destroy -target=aws_instance.example
```

**방법 2:**
```bash
terraform apply -destroy -target=aws_instance.example
```

**여러 리소스 타겟팅:**
```bash
terraform destroy \
  -target=aws_instance.web \
  -target=aws_instance.api
```

**주의사항:**
- ⚠️ 프로덕션에서 사용 지양
- 종속성 있는 리소스도 함께 삭제됨
- State 불일치 가능성

**예시:**
```hcl
resource "aws_instance" "web" {
  subnet_id = aws_subnet.main.id
}

resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id
}
```

```bash
terraform destroy -target=aws_vpc.main
```
→ subnet과 instance도 함께 삭제됨 (종속성)

**참고:**
- [Resource Targeting](https://developer.hashicorp.com/terraform/cli/commands/plan#resource-targeting)
</details>

---

### Question 18 🟡
**What happens when you run `terraform apply`? (Select TWO)**

⬜ A) Terraform creates/modifies/deletes infrastructure  
⬜ B) Terraform downloads the latest provider versions  
⬜ C) Terraform updates the state file  
⬜ D) Terraform validates the configuration syntax  
⬜ E) Terraform formats all .tf files

<details>
<summary>정답 보기</summary>

**답: A, C**

**설명:**

**terraform apply의 동작 흐름:**
```
1. State Refresh (기본)
   ↓
2. Plan 생성
   ↓
3. 사용자 승인 대기 (또는 -auto-approve)
   ↓
4. A) 인프라 변경 실행 ✅
   ↓
5. C) State 파일 업데이트 ✅
```

**예시 출력:**
```bash
$ terraform apply

Terraform will perform the following actions:
  + aws_instance.web

Do you want to perform these actions?
  Enter a value: yes

aws_instance.web: Creating...
aws_instance.web: Creation complete after 30s

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

**틀린 선택지:**

**B) Provider 다운로드:**
→ `terraform init`

**D) 구문 검증:**
→ `terraform validate`

**E) 파일 포맷팅:**
→ `terraform fmt`

**참고:**
- [terraform apply](https://developer.hashicorp.com/terraform/cli/commands/apply)
</details>

---

## Domain 4: Terraform Configuration (26% / ~15 questions)

### Question 19 🟢
**What is the correct syntax to reference an attribute of a resource?**

A) `resource.type.name.attribute`  
B) `type.name.attribute`  
C) `resource_type.resource_name.attribute`  
D) `name.attribute`

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
리소스 속성 참조 형식:
```
<resource_type>.<resource_name>.<attribute>
```

**예시:**
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

resource "aws_eip" "web_ip" {
  instance = aws_instance.web.id
}

output "public_ip" {
  value = aws_instance.web.public_ip
}
```

**참조 패턴:**
```hcl
aws_instance.web.id
aws_instance.web.public_ip
aws_instance.web.private_ip
aws_subnet.main.id
module.vpc.vpc_id
```

**참고:**
- [References to Named Values](https://developer.hashicorp.com/terraform/language/expressions/references)
</details>

---

### Question 20 🟡
**Which variable type allows you to store multiple values with different types?**

A) list  
B) map  
C) object  
D) tuple

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
`object` 타입은 **서로 다른 타입의 값**을 가질 수 있습니다.

**Object 예시:**
```hcl
variable "server_config" {
  type = object({
    name          = string
    instance_type = string
    disk_size     = number
    monitoring    = bool
    tags          = map(string)
  })
  
  default = {
    name          = "web-server"
    instance_type = "t2.micro"
    disk_size     = 20
    monitoring    = true
    tags = {
      Environment = "dev"
    }
  }
}

resource "aws_instance" "server" {
  instance_type = var.server_config.instance_type
  
  root_block_device {
    volume_size = var.server_config.disk_size
  }
  
  monitoring = var.server_config.monitoring
  tags       = var.server_config.tags
}
```

**다른 타입과 비교:**

**List - 동일 타입만:**
```hcl
variable "azs" {
  type = list(string)
  default = ["us-east-1a", "us-east-1b"]
}
```

**Map - 동일 타입만:**
```hcl
variable "tags" {
  type = map(string)
  default = {
    Name = "Server"
    Env  = "Dev"
  }
}
```

**Tuple - 다른 타입 가능하지만 순서 고정:**
```hcl
variable "mixed" {
  type = tuple([string, number, bool])
  default = ["web", 8080, true]
}
```

**참고:**
- [Type Constraints](https://developer.hashicorp.com/terraform/language/expressions/type-constraints)
</details>

---

이제 나머지 문제들을 계속 생성하겠습니다. Set 2의 나머지 38문항을 완성하겠습니다.

계속해서 Mock Exam Set 2의 나머지 문제들을 생성하겠습니다:

<function_calls>
<invoke name="mcp_Bash">
<parameter name="command">wc -l Terraform-Associate-004-Study-Guide/practice-exams/mock-exam-set-2.md
