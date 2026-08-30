---
title: "Lab 05: 첫 번째 Module 만들기"
description: "Legacy study material imported from labs/lab-05-first-module/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟡 Intermediate
**소요 시간:** 90분
**시험 도메인:** Terraform Modules (10%)

### 학습 목표

- ✅ Module 표준 구조 이해
- ✅ Variables, Outputs, Versions 파일 작성
- ✅ Root Module 에서 Child Module 호출
- ✅ Module Output 참조
- ✅ Module 재사용 (여러 인스턴스)

### 실습 시나리오

간단한 VPC Module 을 작성하고 여러 환경에서 재사용합니다.

---

## 📖 단계별 실습

### Step 1: 프로젝트 구조 생성

```bash
mkdir -p ~/terraform-lab-05/modules/vpc
cd ~/terraform-lab-05
```

**최종 구조:**
```
terraform-lab-05/
├── main.tf              # Root module
├── outputs.tf
└── modules/
    └── vpc/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── versions.tf
```

### Step 2: VPC Module 작성

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

**modules/vpc/variables.tf:**
```hcl
variable "name" {
  description = "Name prefix"
  type        = string
}

variable "cidr_block" {
  description = "VPC CIDR"
  type        = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be valid CIDR."
  }
}

variable "azs" {
  description = "Availability zones"
  type        = list(string)
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

**modules/vpc/main.tf:**
```hcl
locals {
  common_tags = merge(var.tags, {
    Module = "vpc"
    Name   = var.name
  })
}

resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true

  tags = local.common_tags
}

resource "aws_subnet" "public" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone = var.azs[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.name}-public-${count.index + 1}"
    Type = "public"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.common_tags, { Name = "${var.name}-igw" })
}
```

**modules/vpc/outputs.tf:**
```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.main.id
}
```

### Step 3: Root Module 작성

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

module "vpc_dev" {
  source = "./modules/vpc"

  name       = "dev-vpc"
  cidr_block = "10.0.0.0/16"
  azs        = ["us-east-1a", "us-east-1b"]

  tags = {
    Environment = "dev"
  }
}

module "vpc_prod" {
  source = "./modules/vpc"

  name       = "prod-vpc"
  cidr_block = "10.1.0.0/16"
  azs        = ["us-east-1a", "us-east-1b", "us-east-1c"]

  tags = {
    Environment = "prod"
  }
}
```

**outputs.tf:**
```hcl
output "dev_vpc_id" {
  value = module.vpc_dev.vpc_id
}

output "prod_vpc_id" {
  value = module.vpc_prod.vpc_id
}

output "dev_public_subnets" {
  value = module.vpc_dev.public_subnet_ids
}
```

### Step 4: 초기화 및 실행

```bash
terraform init
# Initializing modules...
# - vpc_dev in modules/vpc
# - vpc_prod in modules/vpc

terraform plan
# Plan: 8 to add, 0 to change, 0 to destroy

terraform apply -auto-approve
```

### Step 5: State 확인

```bash
terraform state list
# module.vpc_dev.aws_vpc.main
# module.vpc_dev.aws_subnet.public[0]
# module.vpc_dev.aws_subnet.public[1]
# module.vpc_dev.aws_internet_gateway.main
# module.vpc_prod.aws_vpc.main
# ...
```

---

## ✅ 검증

```bash
terraform output
# dev_vpc_id = "vpc-..."
# prod_vpc_id = "vpc-..."

aws ec2 describe-vpcs \
  --filters "Name=tag:Module,Values=vpc" \
  --query 'Vpcs[].[VpcId,CidrBlock,Tags[?Key==`Environment`].Value]'
```

---

## 🐛 문제 해결

### Module 변경 후 적용 안 됨

```bash
terraform get -update
terraform init -upgrade
```

### Module Path 오류

```
Error: Module not found

# 해결: source 경로 확인
source = "./modules/vpc"    # 상대 경로
```

---

## 🎯 핵심 개념

### Module 참조 형식

```
module.<MODULE_NAME>.<OUTPUT_NAME>
```

### Module 재사용

```hcl
module "vpc_dev" { source = "./modules/vpc" }
module "vpc_prod" { source = "./modules/vpc" }
```

각각 독립된 리소스로 생성.

---

## 📚 시험 관련 포인트

- Module Structure (main.tf, variables.tf, outputs.tf, versions.tf)
- Module Output 참조 형식
- Local vs Registry source
- Module 재사용 및 독립성

---

## Cleanup

```bash
terraform destroy -auto-approve
```

---

## 참고

- [Module 작성 가이드](/archive/05-modules/creating-modules/)
- [Module Registry](/archive/05-modules/registry/)
- [Lab 11: Module Registry 활용](/archive/labs/lab-11-module-registry/readme/)
