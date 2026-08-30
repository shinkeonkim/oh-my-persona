---
title: "Module 작성 가이드"
description: "Legacy study material imported from 05-modules/creating-modules.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- 표준 Module 구조 및 파일 조직
- variables.tf, main.tf, outputs.tf, versions.tf 작성
- 재사용 가능한 Module 설계 원칙
- Module 테스트 및 문서화
- 실전 예제: 완전한 VPC Module

---

## 1. Module 작성 원칙

### 단일 책임 (SRP)

**Good:**
```
modules/
├── vpc/
├── ecs-cluster/
└── rds/
```

**Bad:**
```
modules/
└── everything/
```

### 명확한 인터페이스

Module 은 **함수처럼** 동작해야 합니다:
- **Input**: variables
- **Output**: outputs
- **Body**: main.tf

### 조합성 (Composition over Inheritance)

작은 Module 들을 조합해서 큰 시스템 구성.

---

## 2. 표준 Module 구조

### 전체 파일 구조

```
my-module/
├── main.tf              # 주요 리소스 정의
├── variables.tf         # 입력 변수
├── outputs.tf           # 출력 값
├── versions.tf          # Terraform/Provider 버전
├── README.md            # 문서화
├── LICENSE              # 라이선스
├── examples/            # 사용 예제
│   ├── basic/
│   │   └── main.tf
│   └── complete/
│       └── main.tf
└── tests/               # 테스트 (1.6+)
    └── main.tftest.hcl
```

### 최소 구조

```
simple-module/
├── main.tf
├── variables.tf
├── outputs.tf
└── README.md
```

---

## 3. variables.tf 작성

### 필수 요소

```hcl
variable "name" {
  description = "Name prefix for all resources"   # 필수
  type        = string                             # 명시
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"                         # 기본값 (선택)
}
```

### Validation 규칙

```hcl
variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

variable "cidr_block" {
  type = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid CIDR."
  }
}
```

### Sensitive 처리

```hcl
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

### Optional Attributes (1.3+)

```hcl
variable "server_config" {
  type = object({
    name          = string
    instance_type = optional(string, "t3.micro")
    monitoring    = optional(bool, false)
    tags          = optional(map(string), {})
  })
}
```

자세한 내용은 [Variables 상세](/archive/04-configuration/variables-outputs/) 참고.

---

## 4. main.tf 작성

### Naming Conventions

```hcl
# ✅ Good: 명확하고 일관된 이름
resource "aws_vpc" "main" { }
resource "aws_subnet" "public" { count = 3 }
resource "aws_subnet" "private" { count = 3 }

# ❌ Bad: 모호한 이름
resource "aws_vpc" "vpc1" { }
resource "aws_subnet" "s1" { }
```

### Locals 활용

```hcl
locals {
  # 공통 태그
  common_tags = merge(
    var.tags,
    {
      Module      = "vpc"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  )

  # 계산된 값
  subnet_count = length(var.availability_zones)
  public_subnets = [for i in range(local.subnet_count) : cidrsubnet(var.cidr_block, 8, i)]
  private_subnets = [for i in range(local.subnet_count) : cidrsubnet(var.cidr_block, 8, i + 100)]
}
```

### count vs for_each

**count (인덱스 기반):**
```hcl
resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.public_subnets[count.index]
  availability_zone = var.availability_zones[count.index]
}
```

**for_each (키 기반, 안전):**
```hcl
resource "aws_subnet" "public" {
  for_each          = toset(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, index(var.availability_zones, each.key))
  availability_zone = each.key
}
```

### Dynamic Blocks

```hcl
resource "aws_security_group" "example" {
  name = "${var.name}-sg"

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

---

## 5. outputs.tf 작성

### 유용한 Output 원칙

```hcl
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "vpc_arn" {
  description = "ARN of the VPC"
  value       = aws_vpc.main.arn
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "all_subnet_ids" {
  description = "All subnet IDs (public + private)"
  value       = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
}
```

### Sensitive Output

```hcl
output "db_connection_string" {
  description = "Database connection string"
  value       = "postgres://${aws_db_instance.example.endpoint}"
  sensitive   = true
}
```

### Precondition (1.2+)

```hcl
output "public_url" {
  description = "Public URL of the application"
  value       = "https://${aws_lb.example.dns_name}"

  precondition {
    condition     = aws_lb.example.dns_name != ""
    error_message = "Load balancer must have a DNS name."
  }
}
```

---

## 6. versions.tf 작성

### 필수 구조

```hcl
terraform {
  required_version = ">= 1.12.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }

    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}
```

### Version Constraint 원칙

- **Module 개발자**: 최소 요구 버전만 지정 (`>= 5.0`)
- **Root Module**: 정확한 버전 pin (`~> 5.31.0`)

이유: Module 사용자가 유연하게 상위 호환 버전 선택 가능.

---

## 7. README.md 작성

### 표준 템플릿

````markdown
# VPC Module

VPC 와 public/private subnets 을 생성하는 Module.

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"

  name               = "production-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  environment        = "prod"

  tags = {
    Team = "DevOps"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.12.0 |
| aws | >= 5.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| name | Name prefix | string | - | yes |
| cidr_block | VPC CIDR | string | - | yes |
| availability_zones | AZ 목록 | list(string) | - | yes |
| environment | Environment | string | - | yes |
| tags | Additional tags | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | ID of the VPC |
| public_subnet_ids | Public subnet IDs |
| private_subnet_ids | Private subnet IDs |

## Examples

- [Basic](./examples/basic)
- [Complete](./examples/complete)
````

### terraform-docs 활용

```bash
brew install terraform-docs

terraform-docs markdown table --output-file README.md .
```

---

## 8. 실전 예제: 완전한 VPC Module

### modules/vpc/versions.tf

```hcl
terraform {
  required_version = ">= 1.12.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

### modules/vpc/variables.tf

```hcl
variable "name" {
  description = "Name prefix for all resources"
  type        = string

  validation {
    condition     = length(var.name) > 0 && length(var.name) <= 32
    error_message = "Name must be 1-32 characters."
  }
}

variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 AZs required for HA."
  }
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Create NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway (cost saving, less HA)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

### modules/vpc/main.tf

```hcl
locals {
  common_tags = merge(
    var.tags,
    {
      Module    = "vpc"
      Name      = var.name
      ManagedBy = "Terraform"
    }
  )

  az_count = length(var.availability_zones)

  public_subnet_cidrs  = [for i in range(local.az_count) : cidrsubnet(var.cidr_block, 8, i)]
  private_subnet_cidrs = [for i in range(local.az_count) : cidrsubnet(var.cidr_block, 8, i + 100)]

  nat_gateway_count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : local.az_count) : 0
}

resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = var.name
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.name}-igw"
  })
}

resource "aws_subnet" "public" {
  count = local.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.name}-public-${count.index + 1}"
    Type = "public"
  })
}

resource "aws_subnet" "private" {
  count = local.az_count

  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(local.common_tags, {
    Name = "${var.name}-private-${count.index + 1}"
    Type = "private"
  })
}

resource "aws_eip" "nat" {
  count = local.nat_gateway_count

  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${var.name}-nat-eip-${count.index + 1}"
  })
}

resource "aws_nat_gateway" "main" {
  count = local.nat_gateway_count

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(local.common_tags, {
    Name = "${var.name}-nat-${count.index + 1}"
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.name}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  count = local.az_count

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  count = local.az_count

  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${var.name}-private-rt-${count.index + 1}"
  })
}

resource "aws_route_table_association" "private" {
  count = local.az_count

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

### modules/vpc/outputs.tf

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_arn" {
  description = "ARN of the VPC"
  value       = aws_vpc.main.arn
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_cidrs" {
  description = "CIDR blocks of public subnets"
  value       = aws_subnet.public[*].cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}
```

### 사용 예제

```hcl
# main.tf (Root)
module "vpc" {
  source = "./modules/vpc"

  name               = "production-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  enable_nat_gateway = true
  single_nat_gateway = false

  tags = {
    Environment = "production"
    Team        = "Platform"
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnet_ids[0]

  tags = {
    Name = "web-server"
  }
}
```

---

## 9. Testing (Terraform 1.6+)

### tests/basic.tftest.hcl

```hcl
variables {
  name               = "test-vpc"
  cidr_block         = "10.99.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
}

run "verify_vpc_creation" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == "10.99.0.0/16"
    error_message = "VPC CIDR mismatch"
  }
}

run "verify_subnets" {
  command = plan

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "Expected 2 public subnets"
  }

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "Expected 2 private subnets"
  }
}

run "verify_apply" {
  command = apply

  assert {
    condition     = aws_vpc.main.id != ""
    error_message = "VPC ID not generated"
  }
}
```

**실행:**
```bash
terraform test
```

---

## 10. Anti-Patterns

### ❌ God Module

```hcl
# 모든 것을 하나의 module 에
module "everything" {
  source = "./modules/everything"
}
```

### ❌ Provider 를 module 안에 정의

```hcl
# modules/vpc/provider.tf (X)
provider "aws" {
  region = var.region
}
```
→ **Root module 에서 provider 정의**, module 은 상속.

### ❌ Hardcoded Region/Account

```hcl
resource "aws_instance" "web" {
  ami = "ami-us-east-1-specific"  # X
}
```
→ Variables 사용.

### ❌ Recursive Module

```hcl
module "vpc" {
  source = "./modules/vpc"

  module "sub_vpc" {  # X
    source = "./modules/vpc"
  }
}
```

---

## 11. Best Practices

### ✅ DO

- **작고 집중된 module** (단일 책임)
- **명확한 variable/output 이름**
- **모든 variable 에 description**
- **Validation 규칙**
- **완전한 README.md**
- **Version constraint (>= 최소)**
- **Examples 디렉토리**
- **Test 파일**

### ❌ DON'T

- 너무 많은 variables (10개 이상 재고)
- Provider 를 module 안에 정의
- Absolute path 사용 (../../../modules/...)
- 하드코딩된 값
- 문서화 없이 배포

---

## 참고 자료

- [Module Development](https://developer.hashicorp.com/terraform/language/modules/develop)
- [Module Structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [Standard Module Structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [terraform-docs](https://terraform-docs.io/)
- 관련 문서: [Module Registry](/archive/05-modules/registry/), [Module Versioning](/archive/05-modules/versioning/)
- 실습: [Lab 05: 첫 번째 Module 만들기](/archive/labs/lab-05-first-module/readme/)
