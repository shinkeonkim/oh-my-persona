---
title: "Week 5: Terraform Modules"
description: "Legacy study material imported from 05-modules/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Module의 개념과 구조 완벽 이해
- Module 작성 및 재사용 방법
- Module 소싱 및 버전 관리
- Module 간 데이터 전달
- Terraform Registry 활용

---

## 1. Module이란?

### 정의

**Module**은 재사용 가능한 Terraform 구성의 컨테이너입니다. 여러 리소스를 논리적으로 그룹화하여 패키징합니다.

### Module의 목적

**1. 재사용성 (Reusability)**
```hcl
module "vpc_dev" {
  source = "./modules/vpc"
  env    = "dev"
}

module "vpc_prod" {
  source = "./modules/vpc"
  env    = "prod"
}
```

**2. 조직화 (Organization)**
```
infrastructure/
├── modules/
│   ├── networking/
│   ├── compute/
│   └── database/
└── main.tf
```

**3. 표준화 (Standardization)**
- 팀 전체가 동일한 패턴 사용
- 모범 사례 강제
- 일관된 인프라

**4. 추상화 (Abstraction)**
```hcl
module "web_app" {
  source = "./modules/web-app"
  
  name = "my-app"
}
```
→ 내부 복잡성 숨김

---

## 2. Module 구조

### 표준 Module 구조

```
my-module/
├── main.tf              # 주요 리소스 정의
├── variables.tf         # 입력 변수
├── outputs.tf           # 출력 값
├── versions.tf          # Terraform 및 Provider 버전
├── README.md            # 문서화
├── LICENSE              # 라이선스
├── examples/            # 사용 예제
│   └── basic/
│       └── main.tf
└── tests/               # 테스트 (선택)
    └── basic_test.go
```

### 최소 Module

```
simple-module/
├── main.tf
├── variables.tf
└── outputs.tf
```

---

## 3. Module 작성

### Example: VPC Module

**modules/vpc/main.tf:**
```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    {
      Name = var.name
    },
    var.tags
  )
}

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    {
      Name = "${var.name}-public-${count.index + 1}"
      Type = "public"
    },
    var.tags
  )
}

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    {
      Name = "${var.name}-private-${count.index + 1}"
      Type = "private"
    },
    var.tags
  )
}

resource "aws_internet_gateway" "main" {
  count = length(var.public_subnet_cidrs) > 0 ? 1 : 0

  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.name}-igw"
    },
    var.tags
  )
}
```

**modules/vpc/variables.tf:**
```hcl
variable "name" {
  description = "Name prefix for all resources"
  type        = string
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
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = []
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = []
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
```

**modules/vpc/outputs.tf:**
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

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = length(aws_internet_gateway.main) > 0 ? aws_internet_gateway.main[0].id : null
}
```

**modules/vpc/versions.tf:**
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

**modules/vpc/README.md:**
```markdown
# VPC Module

Creates a VPC with public and private subnets.

## Usage

\`\`\`hcl
module "vpc" {
  source = "./modules/vpc"

  name               = "my-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
  
  tags = {
    Environment = "dev"
  }
}
\`\`\`

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| name | Name prefix | string | - | yes |
| cidr_block | VPC CIDR | string | - | yes |
| availability_zones | AZs | list(string) | - | yes |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| public_subnet_ids | Public subnet IDs |
```

---

## 4. Module 사용

### Root Module에서 호출

**main.tf:**
```hcl
terraform {
  required_version = ">= 1.12.0"

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

module "vpc" {
  source = "./modules/vpc"

  name               = "production-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  
  public_subnet_cidrs  = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ]
  
  private_subnet_cidrs = [
    "10.0.11.0/24",
    "10.0.12.0/24",
    "10.0.13.0/24"
  ]

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  subnet_id     = module.vpc.public_subnet_ids[0]

  tags = {
    Name = "Web Server"
  }
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "web_instance_ip" {
  value = aws_instance.web.public_ip
}
```

### Module 초기화

```bash
terraform init

terraform get

terraform get -update
```

---

## 5. Module Sources

### Local Path

```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "vpc" {
  source = "../shared-modules/vpc"
}
```

### Terraform Registry

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
}
```

### GitHub

```hcl
module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc"
}

module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc?ref=v5.1.2"
}

module "vpc" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git"
}

module "vpc" {
  source = "git::ssh://git@github.com/terraform-aws-modules/terraform-aws-vpc.git"
}
```

### Generic Git

```hcl
module "vpc" {
  source = "git::https://example.com/vpc.git"
}

module "vpc" {
  source = "git::https://example.com/vpc.git?ref=v1.2.0"
}

module "vpc" {
  source = "git::https://example.com/vpc.git//modules/vpc?ref=main"
}
```

### HTTP URLs

```hcl
module "vpc" {
  source = "https://example.com/vpc-module.zip"
}
```

### S3

```hcl
module "vpc" {
  source = "s3::https://s3-us-west-2.amazonaws.com/my-bucket/vpc.zip"
}
```

### GCS

```hcl
module "vpc" {
  source = "gcs::https://www.googleapis.com/storage/v1/my-bucket/vpc.zip"
}
```

---

## 6. Module 버전 관리

### Version Constraints

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = ">= 5.0.0"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = ">= 5.0, < 6.0"
}
```

### Version Constraint Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `=` | `= 5.1.2` | 정확히 5.1.2 |
| `!=` | `!= 5.1.2` | 5.1.2 제외 |
| `>` | `> 5.0.0` | 5.0.0보다 큰 버전 |
| `>=` | `>= 5.0.0` | 5.0.0 이상 |
| `<` | `< 6.0.0` | 6.0.0 미만 |
| `<=` | `<= 5.9.9` | 5.9.9 이하 |
| `~>` | `~> 5.1` | 5.1.x (5.2.0 불허) |

### Lock File

```hcl
module "vpc" {
  version = "5.1.2"
}
```

**.terraform.lock.hcl:**
```hcl
module "terraform-aws-modules/vpc/aws" {
  version = "5.1.2"
}
```

---

## 7. Module 간 데이터 전달

### Parent → Child (Inputs)

```hcl
module "vpc" {
  source = "./modules/vpc"

  name       = var.vpc_name
  cidr_block = var.vpc_cidr
}
```

### Child → Parent (Outputs)

```hcl
module "vpc" {
  source = "./modules/vpc"
}

resource "aws_instance" "web" {
  subnet_id = module.vpc.public_subnet_ids[0]
}
```

### Module → Module

```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "ecs" {
  source = "./modules/ecs"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}
```

---

## 8. Variable Scope

### Root Module

```hcl
variable "environment" {
  default = "prod"
}

module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
}
```

### Child Module

**modules/vpc/variables.tf:**
```hcl
variable "environment" {
  type = string
}
```

→ **Parent의 변수는 자동으로 전달되지 않음!**

---

## 9. Terraform Registry

### 공식 Registry

**https://registry.terraform.io/**

### Module 검색

```bash
terraform-aws-modules/vpc/aws
terraform-aws-modules/ec2-instance/aws
terraform-aws-modules/rds/aws
```

### Module 사용

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

### Private Registry

```hcl
module "vpc" {
  source = "app.terraform.io/my-org/vpc/aws"
  version = "1.0.0"
}
```

---

## 10. Module 조합 (Composition)

### 예제: 3-Tier 아키텍처

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  name       = "app-vpc"
  cidr_block = "10.0.0.0/16"
}

module "web" {
  source = "./modules/web-tier"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids
}

module "app" {
  source = "./modules/app-tier"
  
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  alb_target_arn = module.web.alb_target_group_arn
}

module "db" {
  source = "./modules/db-tier"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  app_sg_id  = module.app.security_group_id
}
```

---

## 11. Module Best Practices

### 1. 명확한 인터페이스

```hcl
variable "name" {
  description = "Name prefix for all resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where resources will be created"
  type        = string
}
```

### 2. 합리적인 기본값

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = false
}
```

### 3. Input Validation

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}
```

### 4. 유용한 Outputs

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "all_subnet_ids" {
  description = "All subnet IDs"
  value       = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
}
```

### 5. 문서화

**README.md 필수:**
- 사용 예제
- Inputs 표
- Outputs 표
- 요구사항

### 6. 버전 관리

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

### 7. 단일 책임 원칙

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

---

## 12. 실전 예제

### 예제 1: 간단한 Module

```hcl
module "s3_bucket" {
  source = "./modules/s3"

  bucket_name = "my-app-data"
  versioning  = true
  
  tags = {
    Environment = "prod"
  }
}
```

### 예제 2: Registry Module

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Terraform   = "true"
    Environment = "prod"
  }
}
```

### 예제 3: Module 체인

```hcl
module "network" {
  source = "./modules/network"
}

module "compute" {
  source     = "./modules/compute"
  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.subnet_ids
}

module "storage" {
  source = "./modules/storage"
  app_sg = module.compute.security_group_id
}
```

---

## 13. 핵심 요약

### Module 개념
- ✅ 재사용 가능한 Terraform 구성
- ✅ 조직화, 표준화, 추상화
- ✅ Input → Output 인터페이스

### Module Source
- ✅ Local Path
- ✅ Terraform Registry
- ✅ GitHub, Git, HTTP, S3

### Best Practices
- ✅ 명확한 인터페이스
- ✅ Validation 추가
- ✅ 문서화
- ✅ 버전 관리
- ✅ 단일 책임

---

## 참고 자료

- [Modules](https://developer.hashicorp.com/terraform/language/modules)
- [Terraform Registry](https://registry.terraform.io/)
- [Module Sources](https://developer.hashicorp.com/terraform/language/modules/sources)
- [Module Composition](https://developer.hashicorp.com/terraform/language/modules/develop/composition)
