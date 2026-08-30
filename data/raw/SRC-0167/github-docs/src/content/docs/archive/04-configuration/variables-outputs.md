---
title: "Variables 와 Outputs 완전 정복"
description: "Legacy study material imported from 04-configuration/variables-outputs.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Input Variables 의 모든 정의 방식 이해
- Variable Types (primitive, collection, structural) 활용
- Variable 값 제공 7가지 방법과 Precedence 순서
- Custom Validation 규칙 작성
- Sensitive Variables 및 Ephemeral Variables (004 신규)
- Outputs 정의 및 활용
- Module Outputs 참조 패턴

---

## 1. Input Variables 개요

### 목적

Input Variables 는 Terraform 모듈의 **입력 매개변수** 역할을 합니다. 함수의 파라미터와 동일한 개념으로, 코드를 재사용 가능하게 만듭니다.

### 기본 구조

```hcl
variable "<NAME>" {
  type        = <TYPE>
  default     = <DEFAULT_VALUE>
  description = "<DESCRIPTION>"
  sensitive   = <true|false>
  nullable    = <true|false>
  ephemeral   = <true|false>  # Terraform 1.10+

  validation {
    condition     = <EXPRESSION>
    error_message = "<ERROR_MSG>"
  }
}
```

### 참조 방법

```hcl
resource "aws_instance" "example" {
  instance_type = var.instance_type
  ami           = var.ami_id
}
```

---

## 2. Variable Types 상세

### 2.1 Primitive Types

**string:**
```hcl
variable "region" {
  type    = string
  default = "us-east-1"
}
```

**number:**
```hcl
variable "instance_count" {
  type    = number
  default = 3
}
```

**bool:**
```hcl
variable "enable_monitoring" {
  type    = bool
  default = false
}
```

### 2.2 Collection Types

**list(TYPE):** 순서있는 컬렉션 (인덱스 접근)
```hcl
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# 참조: var.availability_zones[0]
```

**set(TYPE):** 순서 없는 유니크 컬렉션
```hcl
variable "unique_ports" {
  type    = set(number)
  default = [80, 443, 8080]
}

# 참조: for_each = var.unique_ports
```

**map(TYPE):** 키-값 쌍 (동일 타입 값)
```hcl
variable "common_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# 참조: var.common_tags["Environment"]
```

### 2.3 Structural Types

**object({...}):** 서로 다른 타입의 속성들을 가진 구조체
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
    instance_type = "t3.micro"
    disk_size     = 20
    monitoring    = true
    tags = {
      Role = "web"
    }
  }
}

# 참조: var.server_config.name
```

**tuple([...]):** 순서와 타입이 고정된 리스트
```hcl
variable "server_specs" {
  type    = tuple([string, number, bool])
  default = ["web-01", 100, true]
}

# 참조: var.server_specs[0]  # string
```

### 2.4 Optional Attributes (Terraform 1.3+)

```hcl
variable "network_config" {
  type = object({
    name = string
    cidr = string
    subnets = optional(list(string), [])
    tags    = optional(map(string), {})
  })

  default = {
    name = "prod-vpc"
    cidr = "10.0.0.0/16"
  }
}
```

### 2.5 any 타입

```hcl
variable "flexible_input" {
  type = any
}
```

⚠️ **주의:** `any`는 타입 검증을 우회합니다. 꼭 필요한 경우에만 사용.

---

## 3. Variable 값 제공 방법 (7가지)

### 1. 명령줄 `-var`

```bash
terraform apply -var="instance_type=t3.small"
terraform apply -var='tags={Environment="prod"}'
```

### 2. 명령줄 `-var-file`

```bash
terraform apply -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars.json"
```

### 3. `terraform.tfvars` (자동 로드)

```hcl
# terraform.tfvars
instance_type = "t3.medium"
region        = "us-west-2"
```

### 4. `terraform.tfvars.json` (자동 로드)

```json
{
  "instance_type": "t3.medium",
  "region": "us-west-2"
}
```

### 5. `*.auto.tfvars` (자동 로드, 알파벳 순)

```hcl
# common.auto.tfvars
region = "us-east-1"

# prod.auto.tfvars
environment = "prod"
```

### 6. 환경 변수 `TF_VAR_*`

```bash
export TF_VAR_instance_type="t3.small"
export TF_VAR_region="us-east-1"
terraform apply
```

### 7. Interactive Input (기본)

```
var.instance_type
  EC2 instance type

  Enter a value:
```

### Precedence (높음 → 낮음)

```
1. -var / -var-file (명령줄) — 최우선
2. *.auto.tfvars / *.auto.tfvars.json (알파벳 순)
3. terraform.tfvars.json
4. terraform.tfvars
5. TF_VAR_* 환경 변수
6. variable 블록의 default 값 — 최하위
```

⚠️ **시험 자주 나오는 함정:** `-var`가 항상 최우선입니다. 여러 소스에서 동일 변수 정의 시 위 순서로 병합.

---

## 4. Custom Validation

### 4.1 기본 Validation

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

### 4.2 Regex 활용

```hcl
variable "ami_id" {
  type = string

  validation {
    condition     = can(regex("^ami-[a-f0-9]{8,17}$", var.ami_id))
    error_message = "AMI ID must start with 'ami-' followed by hex characters."
  }
}
```

### 4.3 여러 Validation 규칙

```hcl
variable "instance_type" {
  type = string

  validation {
    condition     = can(regex("^t[2-3]\\.", var.instance_type))
    error_message = "Must be t2 or t3 family."
  }

  validation {
    condition     = !contains(["t2.nano", "t3.nano"], var.instance_type)
    error_message = "Nano instances not allowed in production."
  }
}
```

### 4.4 Complex Validation

```hcl
variable "vpc_config" {
  type = object({
    cidr_block           = string
    enable_dns_hostnames = bool
    availability_zones   = list(string)
  })

  validation {
    condition     = can(cidrhost(var.vpc_config.cidr_block, 0))
    error_message = "cidr_block must be a valid CIDR."
  }

  validation {
    condition     = length(var.vpc_config.availability_zones) >= 2
    error_message = "At least 2 availability zones required."
  }
}
```

### 4.5 Cross-Variable Validation (Terraform 1.9+)

```hcl
variable "min_size" {
  type = number
}

variable "max_size" {
  type = number

  validation {
    condition     = var.max_size >= var.min_size
    error_message = "max_size must be >= min_size."
  }
}
```

---

## 5. Sensitive Variables

### 5.1 sensitive = true

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "example" {
  password = var.db_password
}
```

**CLI 출력:**
```
db_password = <sensitive>
```

⚠️ **CRITICAL:** `sensitive = true`는 **CLI 출력만 마스킹**합니다.
- ❌ State 파일에는 **평문 저장**
- ❌ Plan 파일에도 저장 가능
- ✅ Remote Backend 암호화 필수

### 5.2 Ephemeral Variables (Terraform 1.10+, 004 신규!)

```hcl
variable "api_token" {
  type      = string
  ephemeral = true
}
```

**특징:**
- ✅ State 파일에 저장 안 됨
- ✅ Plan 파일에 저장 안 됨
- ✅ 실행 중에만 존재
- 사용 사례: 임시 토큰, 세션 자격증명

자세한 내용은 [Sensitive Data 관리](/archive/07-lifecycle/sensitive-data/) 참고.

### 5.3 nonsensitive() 함수

```hcl
output "processed_data" {
  value = nonsensitive(var.some_sensitive_var)  # 명시적 해제
}
```

---

## 6. Outputs

### 6.1 기본 구조

```hcl
output "<NAME>" {
  value       = <EXPRESSION>
  description = "<DESCRIPTION>"
  sensitive   = <true|false>
  ephemeral   = <true|false>  # Terraform 1.11+
  depends_on  = [<RESOURCES>]

  precondition {
    condition     = <EXPRESSION>
    error_message = "<ERROR_MSG>"
  }
}
```

### 6.2 실전 예제

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "instance_public_ip" {
  description = "Public IP address"
  value       = aws_instance.web.public_ip
}

output "instance_details" {
  description = "Full instance details"
  value = {
    id         = aws_instance.web.id
    public_ip  = aws_instance.web.public_ip
    private_ip = aws_instance.web.private_ip
    ami        = aws_instance.web.ami
  }
}
```

### 6.3 Sensitive Outputs

```hcl
output "db_connection_string" {
  value = "postgresql://${aws_db_instance.example.username}:${var.db_password}@${aws_db_instance.example.endpoint}"
  sensitive = true
}
```

**CLI 출력:**
```
db_connection_string = <sensitive>
```

⚠️ Sensitive input을 참조하는 output은 자동으로 sensitive 처리됨. 명시적 `sensitive = true`도 권장.

### 6.4 depends_on in Outputs

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
  
  # 명시적 종속성 (드문 경우)
  depends_on = [
    aws_internet_gateway.main
  ]
}
```

### 6.5 Precondition in Outputs (Terraform 1.2+)

```hcl
output "public_url" {
  value = "https://${aws_lb.example.dns_name}"

  precondition {
    condition     = aws_lb.example.dns_name != ""
    error_message = "Load balancer DNS name must be set."
  }
}
```

---

## 7. Output 조회 명령어

### 기본 조회

```bash
terraform output

# 결과:
# instance_id = "i-1234567890abcdef0"
# instance_public_ip = "54.123.45.67"
```

### 특정 Output 조회

```bash
terraform output instance_id
```

### JSON 형식

```bash
terraform output -json

# 결과:
# {
#   "instance_id": {
#     "sensitive": false,
#     "type": "string",
#     "value": "i-1234567890abcdef0"
#   }
# }
```

### Raw 값 (스크립트에서 활용)

```bash
INSTANCE_ID=$(terraform output -raw instance_id)
echo "Instance: $INSTANCE_ID"
```

### 특정 State 파일에서 조회

```bash
terraform output -state=production.tfstate
```

---

## 8. Module Outputs

### 8.1 Child Module 정의

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_ids" {
  value = aws_subnet.public[*].id
}
```

### 8.2 Parent에서 참조

```hcl
module "vpc" {
  source = "./modules/vpc"
  # ...
}

resource "aws_instance" "web" {
  subnet_id = module.vpc.subnet_ids[0]
}

output "vpc_id" {
  value = module.vpc.vpc_id  # Module output 재노출
}
```

자세한 내용은 [Module 작성 가이드](/archive/05-modules/creating-modules/) 참고.

---

## 9. tfvars 파일 종류

| 파일명 | 자동 로드 | 우선순위 |
|--------|-----------|----------|
| `terraform.tfvars` | ✅ | 낮음 |
| `terraform.tfvars.json` | ✅ | 낮음 |
| `*.auto.tfvars` | ✅ (알파벳순) | 중간 |
| `*.auto.tfvars.json` | ✅ (알파벳순) | 중간 |
| `<custom>.tfvars` | ❌ (-var-file 필요) | 높음 |

### 예제

```
project/
├── main.tf
├── variables.tf
├── terraform.tfvars       # 자동 로드
├── dev.tfvars             # -var-file 필요
├── prod.tfvars            # -var-file 필요
└── common.auto.tfvars     # 자동 로드
```

```bash
terraform apply -var-file="prod.tfvars"
```

---

## 10. 실전 시나리오

### 시나리오 1: 환경별 배포 (dev/staging/prod)

**variables.tf:**
```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Invalid environment."
  }
}

variable "instance_config" {
  type = object({
    type  = string
    count = number
  })
}
```

**dev.tfvars:**
```hcl
environment = "dev"
instance_config = {
  type  = "t3.micro"
  count = 1
}
```

**prod.tfvars:**
```hcl
environment = "prod"
instance_config = {
  type  = "t3.large"
  count = 5
}
```

**배포:**
```bash
terraform apply -var-file="dev.tfvars"
terraform apply -var-file="prod.tfvars"
```

### 시나리오 2: 민감 정보 관리

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

```bash
export TF_VAR_db_password=$(aws secretsmanager get-secret-value \
  --secret-id prod/db/password --query SecretString --output text)

terraform apply
```

---

## 11. Best Practices

### ✅ DO

- 모든 variable 에 `description` 명시
- Type constraints 항상 명시
- Sensitive 변수는 `sensitive = true`
- Validation 규칙 적극 활용
- 환경별로 `.tfvars` 파일 분리
- `.tfvars` 파일은 `.gitignore` (민감 정보 포함 시)

### ❌ DON'T

- `type` 생략 (any 사용 금지)
- 민감 정보를 코드에 하드코딩
- `sensitive = true`만 믿고 backend 암호화 미설정
- 모든 것을 variable 로 만들기 (과도한 추상화)

---

## 12. 시험 자주 나오는 함정

### 함정 1: sensitive의 한계
```
Q: sensitive = true 로 설정하면 State 파일에도 암호화되나요?
A: ❌ NO. CLI 출력만 마스킹. State 는 평문.
```

### 함정 2: Variable Precedence
```
Q: terraform.tfvars 와 -var 중 우선순위는?
A: -var 가 최우선.
```

### 함정 3: 자동 로드되는 파일
```
Q: my.tfvars 는 자동 로드되나요?
A: ❌ NO. terraform.tfvars, *.auto.tfvars 만 자동.
```

### 함정 4: Ephemeral 개념
```
Q: ephemeral = true 는 언제 도입되었나요?
A: Terraform 1.10+ (Variables), 1.11+ (Outputs). 004 시험 신규 영역.
```

---

## 참고 자료

- [Input Variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Output Values](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Custom Conditions](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)
- [Ephemeral Values](https://developer.hashicorp.com/terraform/language/values/variables#exclude-values-from-state)
- 관련 문서: [Functions 상세](/archive/04-configuration/functions/), [Complex Types](/archive/04-configuration/complex-types/), [Data Sources](/archive/04-configuration/data-sources/)
- 실습: [Lab 02: Variables와 Outputs](/archive/labs/lab-02-variables-outputs/readme/)
