---
title: "Lab 11: Module Registry 활용"
description: "Legacy study material imported from labs/lab-11-module-registry/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟡 Intermediate
**소요 시간:** 60분
**시험 도메인:** Terraform Modules (10%)

### 학습 목표

- ✅ Terraform Registry 탐색
- ✅ Public Module 사용
- ✅ Version constraint 활용
- ✅ 여러 Module 조합

---

## 📖 시나리오 1: terraform-aws-modules/vpc/aws

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
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "nat_public_ips" {
  value = module.vpc.nat_public_ips
}
```

```bash
terraform init
terraform plan
terraform apply -auto-approve
```

---

## 📖 시나리오 2: Version 업그레이드

**초기:**
```hcl
version = "5.0.0"
```

```bash
terraform init
terraform apply
```

**업그레이드:**
```hcl
version = "~> 5.1"
```

```bash
terraform init -upgrade
terraform plan  # 새 버전의 변경사항 확인
terraform apply
```

---

## 📖 시나리오 3: 여러 Registry Module 조합

**main.tf:**
```hcl
# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"

  name = "app-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}

# Security Group
module "web_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/web"
  version = "~> 5.1"

  name        = "web-sg"
  description = "Web SG"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}

# EC2 Instance
module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 5.5"

  name = "web-server"

  instance_type          = "t3.micro"
  vpc_security_group_ids = [module.web_sg.security_group_id]
  subnet_id              = module.vpc.public_subnets[0]

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}

output "web_public_ip" {
  value = module.ec2.public_ip
}
```

---

## 📖 시나리오 4: GitHub Source

**main.tf:**
```hcl
module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc?ref=v5.1.2"

  name = "github-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
}
```

⚠️ Registry 방식 권장 (문서화, 버전 관리).

---

## 📖 시나리오 5: Local vs Registry 비교

**Local Module:**
```hcl
module "vpc_local" {
  source = "./modules/vpc"
  # ...
}
```

**Registry Module:**
```hcl
module "vpc_registry" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"
  # ...
}
```

| | Local | Registry |
|-|-------|----------|
| Version | Git 관리 | version 명시 |
| 재사용 | 프로젝트 내 | 조직/전세계 |
| 커스터마이징 | 자유 | Fork 필요 |
| 유지관리 | 자체 | 커뮤니티 |

---

## ✅ 검증

```bash
terraform state list
# module.vpc.aws_vpc.this[0]
# module.vpc.aws_subnet.public[0]
# module.web_sg.aws_security_group.this_name_prefix[0]
# module.ec2.aws_instance.this[0]

terraform output
```

---

## 🎯 Registry Module Source 문법

```
<NAMESPACE>/<NAME>/<PROVIDER>

예:
terraform-aws-modules/vpc/aws
terraform-google-modules/network/google
Azure/network/azurerm
```

**Sub-module:**
```
terraform-aws-modules/security-group/aws//modules/web
```

---

## 📚 시험 관련

- Registry source 문법 (namespace/name/provider)
- version 은 선택 (하지만 권장)
- Verified vs Community modules
- Public Registry: registry.terraform.io
- Private Registry: HCP Terraform / Enterprise

---

## Cleanup

```bash
terraform destroy -auto-approve
```

---

## 참고

- [Module Registry](/archive/05-modules/registry/)
- [Module Versioning](/archive/05-modules/versioning/)
- [terraform-aws-modules](https://github.com/terraform-aws-modules)
