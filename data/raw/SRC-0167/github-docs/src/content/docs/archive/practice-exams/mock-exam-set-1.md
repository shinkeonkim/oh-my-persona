---
title: "Terraform Associate (004) 모의고사 Set 1"
description: "Legacy study material imported from practice-exams/mock-exam-set-1.md"
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
**Infrastructure as Code (IaC) allows you to manage infrastructure in a declarative way. What does "declarative" mean in this context?**

A) You specify the exact sequence of commands to create infrastructure  
B) You describe the desired end state and let the tool determine how to achieve it  
C) You write imperative scripts that execute in order  
D) You manually configure each resource through a GUI

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- Declarative (선언적): 원하는 최종 상태를 정의하면 도구가 현재 상태와 비교하여 필요한 변경 사항을 자동으로 결정
- Imperative (명령적): 단계별 명령어를 순서대로 실행
- Terraform은 선언적(declarative) 접근 방식을 사용합니다

**참고:**
- [IaC Patterns](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004#learn-about-infrastructure-as-code-iac)
</details>

---

### Question 2 🟡
**Which of the following are advantages of using Infrastructure as Code? (Select TWO)**

⬜ A) Infrastructure can be version controlled  
⬜ B) Manual changes are easier to track  
⬜ C) Infrastructure can be tested before deployment  
⬜ D) GUI-based configuration is simplified  
⬜ E) Documentation is automatically generated

<details>
<summary>정답 보기</summary>

**답: A, C**

**설명:**
- **A) 버전 관리 가능**: IaC 코드는 Git 등으로 버전 관리 가능
- **C) 배포 전 테스트**: `terraform plan`으로 변경 사항을 미리 검증 가능
- **B) 틀림**: IaC는 수동 변경을 줄이는 것이 목적
- **D) 틀림**: GUI 대신 코드 기반 접근
- **E) 틀림**: 문서화는 별도로 필요

**참고:**
- [IaC Benefits](https://developer.hashicorp.com/terraform/intro)
</details>

---

### Question 3 🟢
**True or False: Terraform is cloud-agnostic and can manage resources across multiple cloud providers.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: True**

**설명:**
- Terraform은 AWS, Azure, GCP, Kubernetes 등 여러 플랫폼을 지원
- Provider 플러그인 시스템을 통해 다양한 인프라 관리 가능
- 단일 구성 파일에서 멀티 클라우드 인프라 정의 가능

**참고:**
- [Terraform Providers](https://registry.terraform.io/browse/providers)
</details>

---

## Domain 2: Terraform Fundamentals (10% / ~6 questions)

### Question 4 🟢
**What is the purpose of a Terraform provider?**

A) To store Terraform state remotely  
B) To define infrastructure resources for a specific platform or service  
C) To manage Terraform modules  
D) To lock state files during operations

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- Provider는 특정 플랫폼(AWS, Azure 등)의 API와 상호작용하는 플러그인
- 각 Provider는 해당 플랫폼의 리소스 타입을 정의
- 예: `aws` provider는 EC2, S3 등의 리소스 제공

**예제:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

**참고:**
- [Providers Documentation](https://developer.hashicorp.com/terraform/language/providers)
</details>

---

### Question 5 🟡
**Which file is automatically created by Terraform to track provider versions?**

A) terraform.tfstate  
B) .terraform.lock.hcl  
C) provider.lock  
D) versions.tf

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- `.terraform.lock.hcl`: Dependency lock file
- `terraform init` 실행 시 자동 생성
- Provider 버전을 고정하여 일관성 보장
- 버전 관리 시스템에 커밋 필요

**참고:**
- [Dependency Lock File](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
</details>

---

### Question 6 🟢
**True or False: The Terraform state file maps your configuration to real-world resources.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: True**

**설명:**
- State 파일은 구성과 실제 인프라 간의 매핑 정보 저장
- 리소스 메타데이터, 종속성, 속성 값 등 포함
- Terraform이 어떤 리소스를 관리하는지 추적

**State 파일의 주요 역할:**
1. 리소스 매핑 (configuration → real resources)
2. 메타데이터 저장
3. 성능 향상 (대규모 인프라)
4. 협업 지원 (remote state)

**참고:**
- [Purpose of Terraform State](https://developer.hashicorp.com/terraform/language/state/purpose)
</details>

---

### Question 7 🟡
**Which command downloads and installs provider plugins?**

A) terraform apply  
B) terraform init  
C) terraform plan  
D) terraform get

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- `terraform init`: 작업 디렉토리 초기화
  - Provider 플러그인 다운로드
  - Backend 초기화
  - Child 모듈 다운로드

**terraform init가 하는 일:**
```bash
$ terraform init

Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.31.0...
- Installed hashicorp/aws v5.31.0
```

**참고:**
- [terraform init](https://developer.hashicorp.com/terraform/cli/commands/init)
</details>

---

### Question 8 🟡
**You want to use multiple AWS providers in the same configuration to manage resources in different regions. How do you reference the alternate provider?**

A) Use the `region` argument in each resource  
B) Create a provider alias and reference it with `provider = aws.alias`  
C) Terraform automatically detects the region from resource configuration  
D) You cannot use multiple providers of the same type

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
# 기본 provider (us-east-1)
provider "aws" {
  region = "us-east-1"
}

# 별칭을 가진 추가 provider (us-west-2)
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

# 기본 provider 사용
resource "aws_instance" "east" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

# 별칭 provider 사용
resource "aws_instance" "west" {
  provider      = aws.west  # 별칭 참조
  ami           = "ami-87654321"
  instance_type = "t2.micro"
}
```

**참고:**
- [Provider Aliases](https://developer.hashicorp.com/terraform/language/providers/configuration#alias-multiple-provider-configurations)
</details>

---

### Question 9 🔴
**Which of the following statements about Terraform providers are true? (Select TWO)**

⬜ A) Providers must be defined in every .tf file  
⬜ B) Provider configurations can be inherited by child modules  
⬜ C) Each resource block must explicitly specify which provider to use  
⬜ D) Providers are distributed separately from Terraform core  
⬜ E) Provider versions cannot be constrained

<details>
<summary>정답 보기</summary>

**답: B, D**

**설명:**
- **B) True**: Child 모듈은 parent 모듈의 provider 구성을 상속받음
- **D) True**: Provider는 플러그인으로 별도 배포됨 (terraform init 시 다운로드)
- **A) False**: Provider는 한 번만 정의하면 됨
- **C) False**: 명시하지 않으면 기본 provider 사용
- **E) False**: `required_providers` 블록으로 버전 제약 가능

**참고:**
- [Providers in Modules](https://developer.hashicorp.com/terraform/language/modules/develop/providers)
</details>

---

## Domain 3: Core Terraform Workflow (16% / ~9 questions)

### Question 10 🟢
**What is the correct order of the core Terraform workflow?**

A) init → validate → plan → apply  
B) plan → init → apply → destroy  
C) apply → plan → init → validate  
D) validate → plan → init → apply

<details>
<summary>정답 보기</summary>

**답: A**

**설명:**
**Core Terraform Workflow:**
1. **Write**: `.tf` 파일 작성
2. **terraform init**: 작업 디렉토리 초기화
3. **terraform validate**: 구성 검증 (문법 오류 확인)
4. **terraform plan**: 실행 계획 생성
5. **terraform apply**: 인프라 변경 적용

**참고:**
- [The Core Terraform Workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
</details>

---

### Question 11 🟢
**True or False: The `terraform plan` command modifies infrastructure.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: False**

**설명:**
- `terraform plan`은 **읽기 전용** 명령어
- 변경 계획만 생성하고 실제 인프라는 수정하지 않음
- State를 refresh하지만 변경하지는 않음

**terraform plan의 역할:**
- 현재 state와 구성 비교
- 필요한 변경 사항 계산
- 변경 계획 출력 (생성/수정/삭제될 리소스)

**인프라를 변경하는 명령어:**
- `terraform apply`
- `terraform destroy`

**참고:**
- [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
</details>

---

### Question 12 🟡
**Which command checks the syntax and validates the configuration without accessing remote services?**

A) terraform plan  
B) terraform validate  
C) terraform fmt  
D) terraform init

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- **terraform validate**: 
  - 로컬에서만 동작
  - Provider나 remote service에 접근하지 않음
  - 구문 오류, 속성 타입, 리소스 정의 검증
  
- **terraform plan**: Remote API 호출 (실제 인프라 상태 확인)
- **terraform fmt**: 코드 포맷팅만 수행
- **terraform init**: Provider 다운로드 (remote registry 접근)

**예제:**
```bash
$ terraform validate
Success! The configuration is valid.

# 또는
$ terraform validate
Error: Unsupported argument
  on main.tf line 5:
  5:   invalid_argument = "value"
```

**참고:**
- [terraform validate](https://developer.hashicorp.com/terraform/cli/commands/validate)
</details>

---

### Question 13 🟡
**You want to preview changes before applying them. Which command should you use?**

A) terraform show  
B) terraform plan  
C) terraform preview  
D) terraform apply -dry-run

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- `terraform plan`: 변경 사항 미리보기
- 생성/수정/삭제될 리소스 표시
- `-out` 옵션으로 plan 파일 저장 가능

**Plan 출력 기호:**
- `+`: 생성될 리소스
- `~`: 수정될 리소스
- `-`: 삭제될 리소스
- `-/+`: 재생성될 리소스 (destroy → create)
- `<=`: 읽기 작업

**예제:**
```bash
$ terraform plan

Terraform will perform the following actions:

  # aws_instance.example will be created
  + resource "aws_instance" "example" {
      + ami           = "ami-12345678"
      + instance_type = "t2.micro"
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

**참고:**
- [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
</details>

---

### Question 14 🟢
**Which command destroys all resources managed by Terraform?**

A) terraform delete  
B) terraform remove  
C) terraform destroy  
D) terraform apply -destroy

<details>
<summary>정답 보기</summary>

**답: C (또는 D)**

**설명:**
두 명령어 모두 정답:
- `terraform destroy`: 모든 관리 리소스 삭제
- `terraform apply -destroy`: destroy의 별칭

```bash
# 방법 1
$ terraform destroy

# 방법 2 (동일한 결과)
$ terraform apply -destroy
```

**참고:**
- [terraform destroy](https://developer.hashicorp.com/terraform/cli/commands/destroy)
</details>

---

### Question 15 🟡
**What does the `terraform fmt` command do?**

A) Validates the configuration syntax  
B) Formats the configuration files to a canonical style  
C) Creates a formatted plan output  
D) Formats the state file

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- `terraform fmt`: 코드 포맷팅 (일관된 스타일)
- 들여쓰기, 줄바꿈, 정렬 등 자동 수정
- CI/CD 파이프라인에서 코드 스타일 검증에 활용

**예제:**
```bash
$ terraform fmt
main.tf

# 재귀적으로 모든 하위 디렉토리 포맷팅
$ terraform fmt -recursive

# 변경 사항만 확인 (실제 수정 안 함)
$ terraform fmt -check
```

**Before fmt:**
```hcl
resource "aws_instance" "example"{
ami="ami-12345678"
instance_type="t2.micro"
}
```

**After fmt:**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```

**참고:**
- [terraform fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt)
</details>

---

### Question 16 🟡
**Which commands automatically refresh the state unless additional flags are provided? (Select TWO)**

⬜ A) terraform plan  
⬜ B) terraform validate  
⬜ C) terraform apply  
⬜ D) terraform output  
⬜ E) terraform state list

<details>
<summary>정답 보기</summary>

**답: A, C**

**설명:**
- **A) terraform plan**: `-refresh=false`로 비활성화 가능
- **C) terraform apply**: `-refresh=false`로 비활성화 가능
- **B) terraform validate**: State에 접근하지 않음
- **D) terraform output**: State를 읽기만 함 (refresh 안 함)
- **E) terraform state list**: State를 읽기만 함

**Refresh란?**
- 실제 인프라 상태를 조회하여 State 업데이트
- Drift 감지 (State와 실제 인프라 차이)

**예제:**
```bash
# Refresh 비활성화
$ terraform plan -refresh=false
$ terraform apply -refresh=false
```

**참고:**
- [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
</details>

---

### Question 17 🔴
**You want to apply only a specific resource without affecting others. Which command should you use?**

A) terraform apply -resource=aws_instance.example  
B) terraform apply -target=aws_instance.example  
C) terraform apply --only=aws_instance.example  
D) terraform apply -select=aws_instance.example

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
- `-target` 옵션: 특정 리소스만 apply
- 종속성이 있는 리소스도 함께 apply됨
- **주의**: 프로덕션에서는 사용 지양 (부분 적용은 State 불일치 유발 가능)

**예제:**
```bash
# 특정 리소스만 apply
$ terraform apply -target=aws_instance.example

# 여러 리소스 지정
$ terraform apply \
  -target=aws_instance.web \
  -target=aws_security_group.web
```

**참고:**
- [Resource Targeting](https://developer.hashicorp.com/terraform/cli/commands/plan#resource-targeting)
</details>

---

### Question 18 🟡
**What happens when you run `terraform apply`? (Select TWO)**

⬜ A) Terraform makes infrastructure changes defined in the configuration  
⬜ B) Terraform downloads required provider plugins  
⬜ C) Terraform updates the state file with any changes made  
⬜ D) Terraform automatically formats all .tf files  
⬜ E) Terraform validates the configuration syntax

<details>
<summary>정답 보기</summary>

**답: A, C**

**설명:**
**terraform apply의 동작:**
1. State refresh (기본값)
2. 실행 계획 생성 (plan과 동일)
3. 사용자 승인 대기 (자동 승인: `-auto-approve`)
4. **A) 인프라 변경 적용**
5. **C) State 파일 업데이트**

**틀린 선택지:**
- B) Provider 다운로드: `terraform init`
- D) 포맷팅: `terraform fmt`
- E) 검증: `terraform validate`

**참고:**
- [terraform apply](https://developer.hashicorp.com/terraform/cli/commands/apply)
</details>

---

## Domain 4: Terraform Configuration (26% / ~15 questions)

### Question 19 🟢
**What is the difference between a `resource` block and a `data` block?**

A) Resources create infrastructure; data sources read existing infrastructure  
B) Data sources create infrastructure; resources read existing infrastructure  
C) They are identical in functionality  
D) Resources are for AWS; data sources are for Azure

<details>
<summary>정답 보기</summary>

**답: A**

**설명:**

**Resource Block (리소스 생성/관리):**
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```

**Data Source Block (기존 리소스 조회):**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-*"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id  # Data source 참조
  instance_type = "t2.micro"
}
```

**참고:**
- [Resources](https://developer.hashicorp.com/terraform/language/resources)
- [Data Sources](https://developer.hashicorp.com/terraform/language/data-sources)
</details>

---

### Question 20 🟡
**Which variable type would you use to represent a list of availability zones?**

A) string  
B) number  
C) list(string)  
D) map(string)

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
```hcl
variable "availability_zones" {
  description = "List of AZs"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  availability_zone = var.availability_zones[count.index]
  # ...
}
```

**Terraform Variable Types:**
- **Primitive**: `string`, `number`, `bool`
- **Collection**: `list(type)`, `set(type)`, `map(type)`
- **Structural**: `object({...})`, `tuple([...])`

**참고:**
- [Variable Types](https://developer.hashicorp.com/terraform/language/expressions/types)
</details>

---

### Question 21 🟡
**True or False: A variable marked with `sensitive = true` will not be stored in the state file.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: False**

**설명:**
- `sensitive = true`는 **CLI 출력에서만** 값을 숨김
- State 파일에는 **평문으로 저장**됨
- State 파일 자체를 암호화하거나 안전하게 관리해야 함

**예제:**
```hcl
variable "db_password" {
  type      = string
  sensitive = true  # CLI 출력만 숨김
}

# Plan 출력:
# + password = (sensitive value)

# State 파일:
# "password": "actual_password_in_plaintext"  ⚠️
```

**State 보안 방법:**
1. Remote Backend + Encryption at Rest
2. State 파일 접근 제어
3. Vault 같은 시크릿 관리 도구 사용

**참고:**
- [Sensitive Variables](https://developer.hashicorp.com/terraform/language/values/variables#suppressing-values-in-cli-output)
</details>

---

### Question 22 🟢
**How do you reference an output from another module?**

A) `output.module_name.output_name`  
B) `module.module_name.output_name`  
C) `var.module_name.output_name`  
D) `resource.module_name.output_name`

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
# Module 정의
module "vpc" {
  source = "./modules/vpc"
  cidr   = "10.0.0.0/16"
}

# Module의 output 참조
resource "aws_instance" "app" {
  subnet_id = module.vpc.subnet_id  # ✅
  # ...
}
```

**Module Output 정의:**
```hcl
# modules/vpc/outputs.tf
output "subnet_id" {
  value = aws_subnet.main.id
}
```

**참고:**
- [Module Outputs](https://developer.hashicorp.com/terraform/language/values/outputs)
</details>

---

### Question 23 🔴
**Which built-in function would you use to convert a list to a set?**

A) `list_to_set()`  
B) `toset()`  
C) `convert()`  
D) `set()`

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
variable "regions" {
  type    = list(string)
  default = ["us-east-1", "us-west-2", "us-east-1"]  # 중복 포함
}

locals {
  unique_regions = toset(var.regions)  # 중복 제거 → ["us-east-1", "us-west-2"]
}

resource "aws_s3_bucket" "regional" {
  for_each = toset(var.regions)  # Set으로 변환
  bucket   = "my-bucket-${each.key}"
}
```

**자주 사용하는 Type Conversion 함수:**
- `tolist()`: Set/Tuple → List
- `toset()`: List → Set (중복 제거)
- `tomap()`: Object → Map
- `tonumber()`: String → Number
- `tostring()`: Number → String

**참고:**
- [Type Conversion Functions](https://developer.hashicorp.com/terraform/language/functions/toset)
</details>

---

### Question 24 🟡
**What is the purpose of the `count` meta-argument?**

A) To count the number of resources in the configuration  
B) To create multiple instances of a resource  
C) To limit the number of resources that can be created  
D) To count the number of providers

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
resource "aws_instance" "server" {
  count         = 3  # 3개 인스턴스 생성
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "Server-${count.index}"  # Server-0, Server-1, Server-2
  }
}

# 참조 방법:
# aws_instance.server[0]
# aws_instance.server[1]
# aws_instance.server[2]
```

**count vs for_each:**
| count | for_each |
|-------|----------|
| 인덱스 기반 (0, 1, 2...) | 키 기반 (map/set) |
| `count.index` | `each.key`, `each.value` |
| 중간 제거 시 재생성 발생 | 안전한 제거 |

**참고:**
- [count Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/count)
</details>

---

### Question 25 🔴
**You have the following configuration:**
```hcl
resource "aws_instance" "app" {
  for_each      = toset(["web", "api", "db"])
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```
**How would you reference the "api" instance?**

A) `aws_instance.app[1]`  
B) `aws_instance.app["api"]`  
C) `aws_instance.app.api`  
D) `aws_instance.app[api]`

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
# for_each는 키 기반 접근
resource "aws_security_group_rule" "ingress" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  
  # ✅ 올바른 참조
  security_group_id = aws_instance.app["api"].security_groups[0]
}

# ❌ 잘못된 참조
# aws_instance.app[1]        - count에서만 사용
# aws_instance.app.api       - 잘못된 구문
# aws_instance.app[api]      - 따옴표 필요
```

**참고:**
- [for_each](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
</details>

---

### Question 26 🟡
**Which expression syntax allows you to perform conditional logic?**

A) if-then-else  
B) switch-case  
C) condition ? true_val : false_val  
D) when-then

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
**Ternary Conditional Expression (삼항 연산자):**
```hcl
variable "environment" {
  type = string
}

resource "aws_instance" "web" {
  # 조건 ? 참일 때 값 : 거짓일 때 값
  instance_type = var.environment == "prod" ? "t3.large" : "t2.micro"
  
  tags = {
    Name = var.environment == "prod" ? "Production Server" : "Dev Server"
  }
}
```

**더 복잡한 예제:**
```hcl
locals {
  # 여러 조건 중첩
  instance_type = (
    var.environment == "prod" ? "t3.large" :
    var.environment == "staging" ? "t3.medium" :
    "t2.micro"  # default
  )
}
```

**참고:**
- [Conditional Expressions](https://developer.hashicorp.com/terraform/language/expressions/conditionals)
</details>

---

### Question 27 🔴
**What is the purpose of the `depends_on` meta-argument?**

A) To create implicit dependencies between resources  
B) To specify explicit dependencies when Terraform cannot infer them  
C) To prevent resources from being created  
D) To define variable dependencies

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**

**Implicit Dependency (암시적 종속성) - 권장:**
```hcl
resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id  # VPC를 참조 → 자동 종속성
}
```

**Explicit Dependency (명시적 종속성) - 필요한 경우만:**
```hcl
resource "aws_iam_role_policy" "example" {
  role   = aws_iam_role.example.id
  policy = jsonencode({...})
}

resource "aws_instance" "app" {
  # IAM Policy가 먼저 생성되어야 하지만 직접 참조는 없음
  depends_on = [
    aws_iam_role_policy.example  # 명시적 종속성
  ]
}
```

**depends_on을 사용해야 하는 경우:**
1. 리소스 간 참조할 속성이 없지만 순서가 중요한 경우
2. API 호출 순서가 중요한 경우
3. 숨겨진 종속성이 있는 경우

**참고:**
- [depends_on](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
</details>

---

### Question 28 🟡
**True or False: The `lifecycle` block can be used to prevent a resource from being destroyed.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: True**

**설명:**
```hcl
resource "aws_db_instance" "production" {
  identifier = "prod-db"
  # ...

  lifecycle {
    prevent_destroy = true  # ✅ 삭제 방지
  }
}
```

**Lifecycle Meta-Arguments:**
```hcl
resource "aws_instance" "example" {
  # ...

  lifecycle {
    # 재생성 시 새 리소스 먼저 생성
    create_before_destroy = true

    # 삭제 방지 (terraform destroy 시 에러)
    prevent_destroy = false

    # 특정 속성 변경 무시
    ignore_changes = [
      tags["LastModified"],
      user_data,
    ]

    # 특정 리소스 변경 시 재생성 트리거
    replace_triggered_by = [
      aws_security_group.example
    ]
  }
}
```

**참고:**
- [Lifecycle Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
</details>

---

### Question 29 🔴
**Which of the following is a valid way to define a variable validation? (Select ONE)**

A)
```hcl
variable "instance_type" {
  type = string
  validation {
    condition     = var.instance_type == "t2.micro"
    error_message = "Must be t2.micro"
  }
}
```

B)
```hcl
variable "instance_type" {
  type = string
  validate {
    if = var.instance_type == "t2.micro"
    message = "Must be t2.micro"
  }
}
```

C)
```hcl
variable "instance_type" {
  type = string
  check {
    condition = var.instance_type == "t2.micro"
    error = "Must be t2.micro"
  }
}
```

D)
```hcl
variable "instance_type" {
  type = string
  assert = var.instance_type == "t2.micro"
}
```

<details>
<summary>정답 보기</summary>

**답: A**

**설명:**
**올바른 Variable Validation 구문:**
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string

  validation {
    condition     = can(regex("^t[2-3]\\.", var.instance_type))
    error_message = "Instance type must be in t2 or t3 family"
  }

  # 여러 validation 블록 가능
  validation {
    condition     = length(var.instance_type) <= 20
    error_message = "Instance type name too long"
  }
}
```

**자주 사용하는 Validation 패턴:**
```hcl
# 문자열 길이 검증
validation {
  condition     = length(var.name) >= 3 && length(var.name) <= 63
  error_message = "Name must be 3-63 characters"
}

# 정규식 검증
validation {
  condition     = can(regex("^ami-", var.ami_id))
  error_message = "AMI ID must start with 'ami-'"
}

# 리스트 포함 검증
validation {
  condition     = contains(["prod", "staging", "dev"], var.environment)
  error_message = "Environment must be prod, staging, or dev"
}
```

**참고:**
- [Variable Validation](https://developer.hashicorp.com/terraform/language/values/variables#custom-validation-rules)
</details>

---

### Question 30 🟡
**What is the purpose of `dynamic` blocks?**

A) To create resources dynamically at runtime  
B) To generate repeated nested blocks programmatically  
C) To dynamically load modules  
D) To create dynamic variables

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**Without Dynamic Block (반복 코드):**
```hcl
resource "aws_security_group" "example" {
  name = "example"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 더 많은 반복...
}
```

**With Dynamic Block (동적 생성):**
```hcl
variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = [
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
}

resource "aws_security_group" "example" {
  name = "example"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

**참고:**
- [Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
</details>

---

### Question 31 🟢
**Which function returns the number of elements in a list?**

A) `count()`  
B) `size()`  
C) `length()`  
D) `len()`

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
```hcl
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

resource "aws_subnet" "private" {
  count             = length(var.availability_zones)  # 3
  availability_zone = var.availability_zones[count.index]
  # ...
}

# length()는 다양한 타입에 사용 가능
locals {
  list_length   = length(["a", "b", "c"])           # 3
  map_length    = length({a = 1, b = 2})            # 2
  string_length = length("hello")                    # 5
}
```

**참고:**
- [length Function](https://developer.hashicorp.com/terraform/language/functions/length)
</details>

---

### Question 32 🔴
**You want to reference a value from a map variable. Which syntax is correct?**

Given:
```hcl
variable "instance_types" {
  type = map(string)
  default = {
    web = "t2.micro"
    api = "t3.small"
    db  = "t3.medium"
  }
}
```

A) `var.instance_types.web`  
B) `var.instance_types["web"]`  
C) `var.instance_types[web]`  
D) `var.instance_types->web`

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
resource "aws_instance" "web" {
  # ✅ 올바른 Map 접근
  instance_type = var.instance_types["web"]  # "t2.micro"
}

# Lookup Function 사용 (기본값 제공 가능)
resource "aws_instance" "cache" {
  instance_type = lookup(var.instance_types, "cache", "t2.micro")
  # "cache" 키가 없으면 "t2.micro" 사용
}
```

**Map vs Object 차이:**
```hcl
# Map: 같은 타입의 값
variable "ports" {
  type = map(number)
  default = {
    http  = 80
    https = 443
  }
}

# Object: 다른 타입의 값
variable "server_config" {
  type = object({
    name          = string
    instance_type = string
    disk_size     = number
    monitoring    = bool
  })
}
```

**참고:**
- [Map Variables](https://developer.hashicorp.com/terraform/language/expressions/types#maps-objects)
</details>

---

### Question 33 🟡
**Which meta-argument would you use to create multiple instances from a map?**

A) count  
B) for_each  
C) for  
D) each

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
variable "instances" {
  type = map(object({
    instance_type = string
    ami           = string
  }))
  default = {
    web = {
      instance_type = "t2.micro"
      ami           = "ami-12345678"
    }
    api = {
      instance_type = "t3.small"
      ami           = "ami-87654321"
    }
  }
}

resource "aws_instance" "app" {
  for_each = var.instances  # Map 사용

  ami           = each.value.ami
  instance_type = each.value.instance_type

  tags = {
    Name = "Server-${each.key}"  # Server-web, Server-api
  }
}

# 참조:
# aws_instance.app["web"]
# aws_instance.app["api"]
```

**for_each vs count:**
| 특징 | for_each | count |
|------|----------|-------|
| **입력** | Map 또는 Set | Number |
| **접근** | `each.key`, `each.value` | `count.index` |
| **참조** | `resource["key"]` | `resource[index]` |
| **안정성** | 키 기반 (안전) | 인덱스 기반 (재생성 위험) |

**참고:**
- [for_each](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
</details>

---

## Domain 5: Terraform Modules (10% / ~6 questions)

### Question 34 🟢
**What is the purpose of a Terraform module?**

A) To store state files remotely  
B) To organize and reuse Terraform configuration  
C) To manage provider plugins  
D) To execute Terraform commands

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**Module의 주요 목적:**
1. **재사용성**: 공통 인프라 패턴을 캡슐화
2. **조직화**: 복잡한 구성을 논리적 단위로 분리
3. **표준화**: 조직 전체에서 일관된 인프라

**Module 구조:**
```
modules/
└── vpc/
    ├── main.tf        # 주요 리소스
    ├── variables.tf   # 입력 변수
    ├── outputs.tf     # 출력 값
    └── README.md      # 문서
```

**Module 사용:**
```hcl
module "vpc" {
  source = "./modules/vpc"
  
  cidr_block = "10.0.0.0/16"
  name       = "production-vpc"
}

# Module output 참조
resource "aws_instance" "app" {
  subnet_id = module.vpc.subnet_id
}
```

**참고:**
- [Modules Overview](https://developer.hashicorp.com/terraform/language/modules)
</details>

---

### Question 35 🟡
**Which of the following are valid module sources? (Select THREE)**

⬜ A) Local file path  
⬜ B) Terraform Registry  
⬜ C) GitHub repository  
⬜ D) Docker Hub  
⬜ E) npm registry

<details>
<summary>정답 보기</summary>

**답: A, B, C**

**설명:**
**Valid Module Sources:**

**1. Local Path:**
```hcl
module "vpc" {
  source = "./modules/vpc"
}
```

**2. Terraform Registry:**
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}
```

**3. GitHub:**
```hcl
# HTTPS
module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc"
}

# SSH
module "vpc" {
  source = "git@github.com:terraform-aws-modules/terraform-aws-vpc.git"
}

# Specific branch/tag
module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc?ref=v5.0.0"
}
```

**4. Generic Git:**
```hcl
module "vpc" {
  source = "git::https://example.com/vpc.git"
}
```

**5. S3 Bucket:**
```hcl
module "vpc" {
  source = "s3::https://s3-us-west-2.amazonaws.com/my-bucket/vpc.zip"
}
```

**6. HTTP URLs:**
```hcl
module "vpc" {
  source = "https://example.com/vpc.zip"
}
```

**참고:**
- [Module Sources](https://developer.hashicorp.com/terraform/language/modules/sources)
</details>

---

### Question 36 🟡
**How do you specify a module version when using the Terraform Registry?**

A) `module_version = "1.0.0"`  
B) `version = "1.0.0"`  
C) `tag = "1.0.0"`  
D) `release = "1.0.0"`

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"  # ✅ Registry 모듈 버전 지정
  
  # Module inputs
  cidr = "10.0.0.0/16"
}
```

**Version Constraints:**
```hcl
# 정확한 버전
version = "1.0.0"

# 버전 범위
version = ">= 1.0.0, < 2.0.0"

# Pessimistic Constraint (권장)
version = "~> 1.0"  # 1.0.x 허용, 1.1.0은 불허

# Latest (비권장 - 프로덕션)
# version 생략 시 최신 버전
```

**참고:**
- [Module Versions](https://developer.hashicorp.com/terraform/language/modules/syntax#version)
</details>

---

### Question 37 🔴
**True or False: Variables defined in a parent module are automatically available in child modules.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: False**

**설명:**
Child 모듈은 **명시적으로 전달된 변수**만 사용 가능합니다.

**Parent Module (root):**
```hcl
variable "environment" {
  type = string
  default = "production"
}

module "vpc" {
  source = "./modules/vpc"
  
  # ✅ 명시적으로 전달
  environment = var.environment
  cidr_block  = "10.0.0.0/16"
}
```

**Child Module (modules/vpc/variables.tf):**
```hcl
variable "environment" {
  type = string
  # Parent의 variable을 받으려면 선언 필요
}

variable "cidr_block" {
  type = string
}
```

**Variable Scope:**
- Root 모듈의 변수는 자동으로 child에 전달되지 **않음**
- 각 모듈은 독립적인 variable namespace
- 명시적 전달을 통한 인터페이스 명확화

**참고:**
- [Module Variables](https://developer.hashicorp.com/terraform/language/modules/develop/composition)
</details>

---

### Question 38 🟡
**What file structure is recommended for a Terraform module?**

A) All code in main.tf  
B) main.tf, variables.tf, outputs.tf  
C) config.tf, vars.tf, out.tf  
D) terraform.tf, input.tf, output.tf

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**Standard Module Structure:**
```
module-name/
├── main.tf          # 주요 리소스 정의
├── variables.tf     # 입력 변수 선언
├── outputs.tf       # 출력 값 정의
├── versions.tf      # Terraform/Provider 버전 제약 (선택)
├── README.md        # 문서화
├── examples/        # 사용 예제
│   └── basic/
│       └── main.tf
└── tests/           # 테스트 (선택)
    └── ...
```

**main.tf:**
```hcl
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
  
  tags = merge(
    var.tags,
    {
      Name = var.name
    }
  )
}

resource "aws_subnet" "public" {
  count      = length(var.public_subnet_cidrs)
  vpc_id     = aws_vpc.main.id
  cidr_block = var.public_subnet_cidrs[count.index]
}
```

**variables.tf:**
```hcl
variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
}

variable "name" {
  description = "Name of the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of public subnet CIDR blocks"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

**outputs.tf:**
```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}
```

**참고:**
- [Standard Module Structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
</details>

---

### Question 39 🟡
**How can you access the output of a module?**

A) `output.module_name.output_name`  
B) `module.module_name.output_name`  
C) `var.module_name.output_name`  
D) `data.module_name.output_name`

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```hcl
# Module 호출
module "vpc" {
  source = "./modules/vpc"
  cidr   = "10.0.0.0/16"
}

# Module output 참조
resource "aws_instance" "app" {
  # ✅ module.<module_name>.<output_name>
  subnet_id         = module.vpc.public_subnet_ids[0]
  vpc_security_group_ids = [module.vpc.security_group_id]
}

# Output에서 module output 노출
output "vpc_id" {
  value = module.vpc.vpc_id
}
```

**Module Output 정의 (modules/vpc/outputs.tf):**
```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}
```

**참고:**
- [Module Outputs](https://developer.hashicorp.com/terraform/language/values/outputs)
</details>

---

## Domain 6: State Management (16% / ~9 questions)

### Question 40 🟢
**What is the primary purpose of the Terraform state file?**

A) To store provider credentials  
B) To map configuration to real-world resources  
C) To cache downloaded providers  
D) To store Terraform CLI preferences

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**State 파일의 주요 역할:**
1. **리소스 매핑**: Configuration → Real Resources
2. **메타데이터 저장**: 리소스 종속성, 속성 값
3. **성능 향상**: 대규모 인프라에서 API 호출 최소화
4. **협업 지원**: Remote state로 팀 협업

**State 파일 예제:**
```json
{
  "version": 4,
  "terraform_version": "1.12.0",
  "serial": 1,
  "lineage": "...",
  "outputs": {},
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "example",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "id": "i-1234567890abcdef0",
            "ami": "ami-12345678",
            "instance_type": "t2.micro",
            "public_ip": "54.123.45.67"
          }
        }
      ]
    }
  ]
}
```

**참고:**
- [Purpose of Terraform State](https://developer.hashicorp.com/terraform/language/state/purpose)
</details>

---

### Question 41 🟡
**True or False: By default, Terraform stores state locally in a file named `terraform.tfstate`.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: True**

**설명:**
- Backend 구성이 없으면 **local backend** 사용
- State 파일: `terraform.tfstate`
- 백업 파일: `terraform.tfstate.backup` (이전 버전)

**Local State 구조:**
```
project/
├── main.tf
├── terraform.tfstate         # 현재 state
└── terraform.tfstate.backup  # 이전 state
```

**프로덕션에서는 Remote State 권장:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}
```

**참고:**
- [Local Backend](https://developer.hashicorp.com/terraform/language/settings/backends/local)
</details>

---

### Question 42 🟡
**Which backend provides state locking for S3?**

A) S3 automatically provides state locking  
B) DynamoDB  
C) RDS  
D) State locking is not available for S3

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**S3 Backend + DynamoDB Locking:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    
    # ✅ DynamoDB를 통한 State Locking
    dynamodb_table = "terraform-state-lock"
  }
}
```

**DynamoDB 테이블 생성:**
```hcl
resource "aws_dynamodb_table" "terraform_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

**State Locking의 목적:**
- 동시 `terraform apply` 방지
- State 파일 손상 방지
- 협업 환경에서 필수

**참고:**
- [S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3)
</details>

---

### Question 43 🟢
**Which command displays all resources tracked in the state file?**

A) terraform show  
B) terraform state list  
C) terraform resources  
D) terraform inventory

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```bash
$ terraform state list
aws_instance.web
aws_instance.api
aws_security_group.web
aws_vpc.main
module.vpc.aws_subnet.public[0]
module.vpc.aws_subnet.public[1]
```

**State 관련 명령어:**
```bash
# 모든 리소스 목록
$ terraform state list

# 특정 리소스 상세 정보
$ terraform state show aws_instance.web

# State에서 리소스 제거 (실제 인프라는 유지)
$ terraform state rm aws_instance.old

# 리소스 이름 변경/이동
$ terraform state mv aws_instance.old aws_instance.new

# Remote state 다운로드
$ terraform state pull > terraform.tfstate

# Remote state 업로드
$ terraform state push terraform.tfstate
```

**참고:**
- [terraform state list](https://developer.hashicorp.com/terraform/cli/commands/state/list)
</details>

---

### Question 44 🔴
**You renamed a resource in your configuration from `aws_instance.old` to `aws_instance.new`. What happens when you run `terraform apply`?**

A) Terraform updates the resource name in place  
B) Terraform destroys `aws_instance.old` and creates `aws_instance.new`  
C) Terraform automatically detects the rename  
D) Nothing happens

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
Terraform은 리소스 이름 변경을 **새 리소스 생성 + 기존 리소스 삭제**로 인식합니다.

**문제 상황:**
```hcl
# Before
resource "aws_instance" "old" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

# After
resource "aws_instance" "new" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```

```bash
$ terraform plan
# Terraform will perform the following actions:

  # aws_instance.old will be destroyed
  - resource "aws_instance" "old" { ... }

  # aws_instance.new will be created
  + resource "aws_instance" "new" { ... }

Plan: 1 to add, 0 to change, 1 to destroy.
```

**해결 방법 1: moved 블록 (Terraform 1.1+):**
```hcl
resource "aws_instance" "new" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

moved {
  from = aws_instance.old
  to   = aws_instance.new
}
```

**해결 방법 2: terraform state mv:**
```bash
$ terraform state mv aws_instance.old aws_instance.new
```

**참고:**
- [Refactoring with moved](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
</details>

---

### Question 45 🟡
**What command would you use to import an existing EC2 instance with ID `i-1234567890abcdef0` into your Terraform state?**

A) `terraform import aws_instance.example i-1234567890abcdef0`  
B) `terraform add aws_instance.example i-1234567890abcdef0`  
C) `terraform state add aws_instance.example i-1234567890abcdef0`  
D) `terraform attach aws_instance.example i-1234567890abcdef0`

<details>
<summary>정답 보기</summary>

**답: A**

**설명:**
**Import 프로세스:**

**1. 먼저 리소스 블록 작성 (빈 블록도 가능):**
```hcl
resource "aws_instance" "example" {
  # Import 후 실제 값으로 채울 예정
}
```

**2. Import 실행:**
```bash
$ terraform import aws_instance.example i-1234567890abcdef0

aws_instance.example: Importing from ID "i-1234567890abcdef0"...
aws_instance.example: Import prepared!
aws_instance.example: Import complete!
  Imported aws_instance (ID: i-1234567890abcdef0)
```

**3. State에서 실제 값 확인:**
```bash
$ terraform state show aws_instance.example
# 출력된 값을 확인하여 구성 파일 업데이트
```

**4. 구성 파일 업데이트:**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"  # State에서 확인한 값
  instance_type = "t2.micro"
  # ...
}
```

**5. Plan으로 검증:**
```bash
$ terraform plan
# No changes가 나와야 함
```

**참고:**
- [terraform import](https://developer.hashicorp.com/terraform/cli/commands/import)
</details>

---

### Question 46 🔴
**True or False: The `terraform refresh` command is the recommended way to sync state with real infrastructure.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: False**

**설명:**
`terraform refresh` 명령어는 **Deprecated** 되었습니다.

**❌ Deprecated:**
```bash
$ terraform refresh
Warning: This command is deprecated
```

**✅ 권장 방법:**
```bash
# Read-only refresh (State 업데이트 안 함)
$ terraform plan -refresh-only

# State 업데이트하며 refresh
$ terraform apply -refresh-only
```

**-refresh-only의 장점:**
1. 명시적인 사용자 승인 필요
2. Plan 단계에서 변경 사항 확인 가능
3. 실수로 State 변경하는 것 방지

**예제:**
```bash
$ terraform apply -refresh-only

# Terraform will perform the following actions:

  # aws_instance.example will be updated in state
  ~ resource "aws_instance.example" {
      ~ public_ip = "54.123.45.67" -> "54.987.65.43"
    }

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

**참고:**
- [terraform apply -refresh-only](https://developer.hashicorp.com/terraform/cli/commands/apply#refresh-only-mode)
</details>

---

### Question 47 🟡
**Which command removes a resource from the state file without destroying the actual infrastructure?**

A) terraform delete  
B) terraform state rm  
C) terraform remove  
D) terraform destroy -target

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```bash
# State에서만 제거 (실제 인프라는 유지)
$ terraform state rm aws_instance.example

Removed aws_instance.example
Successfully removed 1 resource instance(s).
```

**사용 사례:**
1. 리소스를 Terraform 관리에서 제외하고 싶을 때
2. 다른 Terraform 프로젝트로 리소스 이관
3. 수동으로 관리하던 리소스를 Terraform에서 분리

**주의사항:**
- State에서만 제거되고 **실제 인프라는 그대로 유지**됨
- 이후 `terraform apply` 시 해당 리소스 재생성 시도하지 않음

**반대 상황 (State 유지, 인프라만 삭제):**
```bash
# 실제 인프라만 삭제, State는 유지
# (일반적으로 이렇게 하지 않음 - 수동 삭제)
$ aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# 이후 terraform plan 시 Drift 감지됨
```

**참고:**
- [terraform state rm](https://developer.hashicorp.com/terraform/cli/commands/state/rm)
</details>

---

### Question 48 🟡
**What is infrastructure drift?**

A) The gradual increase in infrastructure costs  
B) When the actual infrastructure differs from the Terraform state  
C) When Terraform configuration changes over time  
D) The movement of resources between regions

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**Infrastructure Drift:**
- State 파일과 실제 인프라 간의 불일치
- 수동 변경, 외부 도구, 콘솔 변경 등으로 발생

**Drift 발생 예:**
```hcl
# Terraform 구성
resource "aws_instance" "web" {
  instance_type = "t2.micro"
}
```

**수동 변경:**
- AWS 콘솔에서 instance_type을 `t2.small`로 변경

**Drift 감지:**
```bash
$ terraform plan

Terraform will perform the following actions:

  # aws_instance.web will be updated in-place
  ~ resource "aws_instance" "web" {
      ~ instance_type = "t2.small" -> "t2.micro"  # Drift 감지!
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

**Drift 해결 방법:**

**1. Terraform으로 복구 (구성대로 복원):**
```bash
$ terraform apply
# instance_type을 t2.micro로 되돌림
```

**2. State 업데이트 (실제 상태 수용):**
```bash
# 1. 구성 파일 업데이트
resource "aws_instance" "web" {
  instance_type = "t2.small"  # 실제 상태에 맞춤
}

# 2. Apply
$ terraform apply
```

**3. Refresh-only로 State만 동기화:**
```bash
$ terraform apply -refresh-only
```

**참고:**
- [Detect and Manage Drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)
</details>

---

## Domain 7: Maintain Infrastructure (10% / ~6 questions)

### Question 49 🟡
**Which command should you use instead of the deprecated `terraform taint`?**

A) terraform mark  
B) terraform replace  
C) terraform apply -replace=RESOURCE  
D) terraform force-recreate

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
**❌ Deprecated (Terraform 0.15.2+):**
```bash
$ terraform taint aws_instance.example
Warning: "terraform taint" is deprecated
```

**✅ 권장 방법:**
```bash
$ terraform apply -replace="aws_instance.example"

# Plan 단계에서도 사용 가능
$ terraform plan -replace="aws_instance.example"
```

**-replace의 동작:**
- 기존 리소스 삭제 후 재생성
- `lifecycle { create_before_destroy = true }` 설정 존중
- 여러 리소스 동시 replace 가능

**예제:**
```bash
# 단일 리소스
$ terraform apply -replace="aws_instance.web"

# 여러 리소스
$ terraform apply \
  -replace="aws_instance.web" \
  -replace="aws_instance.api"
```

**참고:**
- [Replace Resources](https://developer.hashicorp.com/terraform/cli/commands/plan#replace)
</details>

---

### Question 50 🟡
**How do you enable verbose logging in Terraform?**

A) `terraform apply --verbose`  
B) Set the `TF_LOG` environment variable  
C) `terraform apply -log-level=debug`  
D) Enable logging in terraform.tfvars

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**Logging 레벨 설정:**
```bash
# Linux/macOS
export TF_LOG=TRACE
export TF_LOG=DEBUG
export TF_LOG=INFO
export TF_LOG=WARN
export TF_LOG=ERROR

# Windows (PowerShell)
$env:TF_LOG = "TRACE"

# Windows (CMD)
set TF_LOG=TRACE
```

**로그 파일로 저장:**
```bash
export TF_LOG=TRACE
export TF_LOG_PATH=./terraform.log

$ terraform apply
# 로그가 terraform.log 파일에 저장됨
```

**로깅 레벨:**
- **TRACE**: 가장 상세 (모든 정보)
- **DEBUG**: 디버그 정보
- **INFO**: 일반 정보
- **WARN**: 경고
- **ERROR**: 에러만

**Provider별 로깅:**
```bash
# Core Terraform만 로깅
export TF_LOG_CORE=TRACE

# Provider만 로깅
export TF_LOG_PROVIDER=TRACE
```

**사용 사례:**
- 복잡한 에러 디버깅
- Provider 동작 분석
- 성능 이슈 조사
- Support 티켓 제출 시 로그 첨부

**참고:**
- [Debugging Terraform](https://developer.hashicorp.com/terraform/internals/debugging)
</details>

---

### Question 51 🟢
**True or False: `terraform import` automatically generates configuration for imported resources.**

⬜ True  
⬜ False

<details>
<summary>정답 보기</summary>

**답: False**

**설명:**
`terraform import`는 **State만 업데이트**하고 구성 파일은 생성하지 않습니다.

**Import 프로세스:**

**1. 수동으로 리소스 블록 작성:**
```hcl
resource "aws_instance" "imported" {
  # 빈 블록 또는 기본 속성만
}
```

**2. Import 실행:**
```bash
$ terraform import aws_instance.imported i-1234567890abcdef0
```

**3. State에서 실제 값 확인:**
```bash
$ terraform state show aws_instance.imported
```

**4. 구성 파일 수동 업데이트:**
```hcl
resource "aws_instance" "imported" {
  ami           = "ami-12345678"  # State에서 확인
  instance_type = "t2.micro"
  
  tags = {
    Name = "Imported Instance"
  }
}
```

**5. Plan으로 검증:**
```bash
$ terraform plan
# No changes. Your infrastructure matches the configuration.
```

**Note:** 
- Terraform 1.5+에서는 `-generate-config-out` 플래그로 자동 생성 가능 (실험적 기능)

**참고:**
- [terraform import](https://developer.hashicorp.com/terraform/cli/commands/import)
</details>

---

### Question 52 🟡
**You want to see the current state of a specific resource. Which command should you use?**

A) terraform get aws_instance.example  
B) terraform show aws_instance.example  
C) terraform state show aws_instance.example  
D) terraform inspect aws_instance.example

<details>
<summary>정답 보기</summary>

**답: C**

**설명:**
```bash
$ terraform state show aws_instance.example

# aws_instance.example:
resource "aws_instance" "example" {
    ami                          = "ami-12345678"
    arn                          = "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"
    associate_public_ip_address  = true
    availability_zone            = "us-east-1a"
    cpu_core_count               = 1
    cpu_threads_per_core         = 1
    id                           = "i-1234567890abcdef0"
    instance_state               = "running"
    instance_type                = "t2.micro"
    ipv6_address_count           = 0
    ipv6_addresses               = []
    monitoring                   = false
    primary_network_interface_id = "eni-0123456789abcdef0"
    private_dns                  = "ip-10-0-1-10.ec2.internal"
    private_ip                   = "10.0.1.10"
    public_dns                   = "ec2-54-123-45-67.compute-1.amazonaws.com"
    public_ip                    = "54.123.45.67"
    # ... more attributes
}
```

**terraform show vs terraform state show:**
```bash
# 전체 State 내용 출력
$ terraform show

# 특정 리소스만 출력
$ terraform state show aws_instance.example
```

**참고:**
- [terraform state show](https://developer.hashicorp.com/terraform/cli/commands/state/show)
</details>

---

### Question 53 🔴
**Which command moves a resource from one state file to another?**

A) terraform state mv -state-out=destination.tfstate SOURCE DEST  
B) terraform state pull SOURCE | terraform state push DEST  
C) terraform state mv -state-in=source.tfstate SOURCE DEST  
D) You must use `terraform state pull` and `terraform state rm` manually

<details>
<summary>정답 보기</summary>

**답: A (실제로는 약간 다른 구문)**

**실제 정답:**
```bash
# 동일 State 내에서 이동/이름 변경
$ terraform state mv SOURCE DEST

# 다른 State 파일로 이동
$ terraform state mv \
  -state=source.tfstate \
  -state-out=destination.tfstate \
  SOURCE \
  DEST
```

**예제 시나리오:**

**1. 리소스 이름 변경 (동일 State):**
```bash
$ terraform state mv aws_instance.old aws_instance.new
```

**2. 다른 State 파일로 이동:**
```bash
# project-a의 리소스를 project-b로 이동
$ terraform state mv \
  -state=../project-a/terraform.tfstate \
  -state-out=../project-b/terraform.tfstate \
  aws_instance.web \
  aws_instance.web
```

**3. Module로 이동:**
```bash
# Root 리소스를 module로 이동
$ terraform state mv \
  aws_instance.example \
  module.compute.aws_instance.example
```

**참고:**
- [terraform state mv](https://developer.hashicorp.com/terraform/cli/commands/state/mv)
</details>

---

### Question 54 🟡
**What is the purpose of the `terraform state pull` command?**

A) To push local state to remote backend  
B) To download and output the remote state  
C) To refresh the state file  
D) To merge multiple state files

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
```bash
# Remote state를 stdout으로 출력
$ terraform state pull

# 파일로 저장
$ terraform state pull > backup.tfstate
```

**state pull vs state push:**
```bash
# Remote → Local (다운로드)
$ terraform state pull > local-state.tfstate

# Local → Remote (업로드)
$ terraform state push local-state.tfstate
```

**사용 사례:**

**1. State 백업:**
```bash
$ terraform state pull > backup-$(date +%Y%m%d).tfstate
```

**2. State 검사:**
```bash
$ terraform state pull | jq '.resources[] | {type, name}'
```

**3. State 복구:**
```bash
# 백업에서 복구
$ terraform state push backup.tfstate
```

**주의사항:**
- `state push`는 위험 (force 옵션 필요)
- State locking 우회 가능성
- 가능하면 `terraform import`나 `terraform state mv` 사용

**참고:**
- [terraform state pull/push](https://developer.hashicorp.com/terraform/cli/commands/state/pull)
</details>

---

## Domain 8: HCP Terraform (6% / ~3 questions)

### Question 55 🟡
**What is the primary benefit of using HCP Terraform over local Terraform?**

A) Faster execution  
B) Remote state storage and collaboration features  
C) Access to more providers  
D) Automatic infrastructure creation

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**HCP Terraform (구 Terraform Cloud) 주요 기능:**

**1. Remote State Management:**
- 자동 State 암호화
- State Locking 기본 제공
- Version history
- 안전한 State 접근 제어

**2. 협업 기능:**
- Team permissions
- Workspace 조직화
- VCS 연동 (GitHub, GitLab 등)
- Collaborative runs

**3. 거버넌스:**
- Policy as Code (Sentinel/OPA)
- Cost estimation
- Drift detection
- Health assessments

**4. Remote Execution:**
- 중앙화된 실행 환경
- 일관된 Terraform 버전
- Secure variable storage

**HCP Terraform 구성:**
```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "production"
    }
  }
}
```

**참고:**
- [HCP Terraform](https://developer.hashicorp.com/terraform/cloud-docs)
</details>

---

### Question 56 🟡
**What is the correct HCP Terraform run workflow order?**

A) Plan → Apply → Policy Check → Cost Estimation  
B) Plan → Cost Estimation → Policy Check → Apply  
C) Plan → Policy Check → Cost Estimation → Apply  
D) Cost Estimation → Plan → Policy Check → Apply

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**
**HCP Terraform Run Lifecycle:**

```
1. Plan 단계
   ↓
2. Cost Estimation
   ↓
3. Policy Check (Sentinel/OPA)
   ↓
4. Apply 단계 (수동 승인 또는 자동)
```

**상세 워크플로우:**
```
VCS Push
  ↓
Trigger Run
  ↓
Queue Run
  ↓
【Plan Phase】
  - terraform init
  - terraform plan
  ↓
【Cost Estimation】
  - 예상 비용 계산
  - Diff 표시
  ↓
【Policy Check】
  - Sentinel policies 검증
  - OPA policies 검증
  - Advisory / Soft Mandatory / Hard Mandatory
  ↓
【Apply Phase】
  - Manual approval (기본)
  - Auto-apply (선택)
  - terraform apply
  ↓
Complete
```

**Policy Check 결과:**
- **Pass**: Apply 진행 가능
- **Advisory**: 경고만 표시, Apply 가능
- **Soft Mandatory Failure**: Override 가능
- **Hard Mandatory Failure**: Apply 불가

**참고:**
- [Run Workflow](https://developer.hashicorp.com/terraform/cloud-docs/run/states)
</details>

---

### Question 57 🟡
**What is the difference between HCP Terraform Workspaces and Terraform CLI workspaces?**

A) They are identical  
B) HCP Workspaces are collections of infrastructure; CLI workspaces are State file variants  
C) CLI workspaces are more powerful  
D) HCP Workspaces don't support remote backends

<details>
<summary>정답 보기</summary>

**답: B**

**설명:**

| Feature | HCP Terraform Workspaces | Terraform CLI Workspaces |
|---------|--------------------------|--------------------------|
| **목적** | 독립적인 인프라 환경 관리 | 동일 구성의 State 분리 |
| **State** | 완전히 분리된 State | 같은 디렉토리, 다른 State 파일 |
| **Variables** | Workspace별 고유 변수 | CLI 변수로만 구분 |
| **Permissions** | 세밀한 접근 제어 | 로컬 파일 시스템 권한 |
| **VCS** | VCS 연동 지원 | 지원 안 함 |
| **실행 환경** | Remote execution | Local execution |

**HCP Terraform Workspace:**
```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "production-us-east-1"
    }
  }
}
```

**특징:**
- 각 Workspace는 독립적인 인프라 환경
- 고유한 State, Variables, Settings
- Projects로 그룹화 가능

**CLI Workspace:**
```bash
$ terraform workspace list
  default
* development
  staging
  production

$ terraform workspace select production
$ terraform apply
# production.tfstate 사용
```

**특징:**
- 같은 구성 파일, 다른 State 파일
- `terraform.tfstate.d/` 디렉토리에 저장
- 주로 간단한 환경 분리에 사용

**HCP Terraform Projects:**
```
Organization: my-company
├── Project: Infrastructure
│   ├── Workspace: prod-vpc
│   ├── Workspace: prod-compute
│   └── Workspace: prod-database
├── Project: Applications
│   ├── Workspace: app-frontend
│   └── Workspace: app-backend
└── Project: Security
    └── Workspace: iam-policies
```

**참고:**
- [HCP Terraform Workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)
- [CLI Workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces)
</details>

---

## 시험 종료

**모의고사를 완료하신 것을 축하합니다! 🎉**

### 다음 단계:
1. 정답을 확인하고 점수를 계산하세요
2. 틀린 문제는 관련 문서를 다시 학습하세요
3. 취약한 도메인을 집중 복습하세요
4. [모의고사 Set 2](/archive/practice-exams/mock-exam-set-2/)로 실력을 점검하세요

### 점수 계산:
- 총 57문항
- 합격 기준: 약 70% (40문항)
- 목표 점수: 80% 이상 (46문항)

**Good luck! 🚀**
