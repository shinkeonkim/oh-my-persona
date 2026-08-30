---
title: "Terraform Registry 활용"
description: "Legacy study material imported from 05-modules/registry.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Public Terraform Registry 이해
- Module 검색 및 평가 방법
- Registry Module 사용법
- HashiCorp Verified Modules
- Private Registry (HCP Terraform)
- Module 게시 방법

---

## 1. Terraform Registry 란?

### 정의

**Terraform Registry** 는 Terraform Modules 와 Providers 를 공유하는 공식 저장소입니다.

- **Public Registry:** https://registry.terraform.io/
- **Private Registry:** HCP Terraform / Enterprise 자체

---

## 2. Registry Module 유형

### 2.1 HashiCorp Official

HashiCorp 가 직접 관리하는 Module.

### 2.2 Verified

HashiCorp 파트너 (AWS, Azure, GCP 등)가 유지관리하는 신뢰할 수 있는 Module.

**표시:** 🔵 파란색 체크마크

**예시:**
- `terraform-aws-modules/vpc/aws`
- `terraform-google-modules/network/google`
- `Azure/network/azurerm`

### 2.3 Community

커뮤니티가 제작하고 관리.

**주의:** 품질 편차 있음. 검증 필요.

### 2.4 Partner

HashiCorp 파트너 프로그램 참여 벤더.

---

## 3. Module 검색 및 평가

### 3.1 검색 방법

Registry 웹사이트에서:
- **Provider 필터:** aws, azurerm, google, kubernetes
- **정렬:** Popular, Recently updated
- **키워드:** vpc, ec2, database

### 3.2 평가 기준

Module 선택 시 확인:

| 항목 | 확인 방법 |
|------|-----------|
| **Downloads** | 많을수록 검증됨 |
| **Stars** | GitHub 스타 |
| **Verified 뱃지** | HashiCorp 검증 여부 |
| **Last Updated** | 최근 6개월 이내 |
| **Provider Version** | 최신 Provider 지원 |
| **Documentation** | 완전한 README + Inputs/Outputs |
| **Examples** | examples/ 디렉토리 |
| **Issues** | 활발한 유지관리 |

### 3.3 좋은 Module 지표

✅ **Good:**
- Verified 뱃지
- 최근 6개월 내 업데이트
- 명확한 문서화
- Examples 다수
- Semantic versioning 사용
- Provider 최신 버전 지원

❌ **Warning:**
- 1년 이상 미업데이트
- Issue 응답 없음
- 문서 부족
- 예제 없음
- Breaking changes 미공지

---

## 4. Module Source 문법

### Registry 형식

```
<NAMESPACE>/<NAME>/<PROVIDER>
```

**예시:**
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}
```

- `terraform-aws-modules` : Namespace (조직)
- `vpc` : Module 이름
- `aws` : Provider

### Sub-module (드문 경우)

```
<NAMESPACE>/<NAME>/<PROVIDER>//<SUBMODULE_PATH>
```

```hcl
module "vpc_endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  version = "5.1.2"
}
```

---

## 5. Verified Module 사용 예제

### 5.1 AWS VPC Module

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

# Outputs 참조
resource "aws_instance" "web" {
  subnet_id = module.vpc.public_subnets[0]
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  # ...
}
```

### 5.2 AWS EC2 Module

```hcl
module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.5.0"

  name = "single-instance"

  instance_type          = "t2.micro"
  key_name               = "user1"
  monitoring             = true
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-12345678"

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

### 5.3 AWS RDS Module

```hcl
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.1.1"

  identifier = "prod-postgres"

  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.large"
  allocated_storage = 100

  db_name  = "myapp"
  username = "admin"
  port     = 5432

  vpc_security_group_ids = [module.vpc.default_security_group_id]

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  subnet_ids = module.vpc.private_subnets

  family = "postgres15"

  major_engine_version = "15"

  deletion_protection = true

  tags = {
    Terraform   = "true"
    Environment = "prod"
  }
}
```

### 5.4 AWS Security Group Module

```hcl
module "web_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/web"
  version = "5.1.2"

  name        = "web-sg"
  description = "Security group for web-server"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}
```

### 5.5 여러 Module 조합

```hcl
# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "app-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
}

# Security Group
module "sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.2"

  name        = "app-sg"
  description = "Application security group"
  vpc_id      = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

# EC2
module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.5.0"

  name = "app-server"

  instance_type          = "t3.small"
  subnet_id              = module.vpc.private_subnets[0]
  vpc_security_group_ids = [module.sg.security_group_id]
}
```

---

## 6. Version Constraints

### 기본 사용

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}
```

### Constraint 연산자

| 연산자 | 예제 | 의미 |
|--------|------|------|
| `=` | `= 5.1.2` | 정확히 5.1.2 |
| `!=` | `!= 5.1.2` | 5.1.2 제외 |
| `>` | `> 5.0.0` | 5.0.0 초과 |
| `>=` | `>= 5.0.0` | 5.0.0 이상 |
| `<` | `< 6.0.0` | 6.0.0 미만 |
| `<=` | `<= 5.9.9` | 5.9.9 이하 |
| `~>` | `~> 5.1` | 5.x, 6.0 불허 |
| `~>` | `~> 5.1.0` | 5.1.x, 5.2.0 불허 |

### 실전 예제

```hcl
# 정확한 버전 (안전, 업데이트 수동)
version = "5.1.2"

# Pessimistic (권장, 마이너 업데이트 허용)
version = "~> 5.1"    # 5.1.x, 5.2.x, ..., 5.9.x

# Range
version = ">= 5.0, < 6.0"

# 최신 (위험!)
# version 생략 → 항상 최신
```

자세한 내용은 [Module Versioning](/archive/05-modules/versioning/) 참고.

---

## 7. 다른 Source Type

Registry 외에도 다양한 소스 지원.

### Local Path

```hcl
module "vpc" {
  source = "./modules/vpc"
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
```

### Generic Git

```hcl
module "vpc" {
  source = "git::https://example.com/vpc.git?ref=v1.2.0"
}

module "vpc" {
  source = "git::ssh://git@github.com/user/repo.git"
}
```

### S3 / GCS

```hcl
module "vpc" {
  source = "s3::https://s3.amazonaws.com/my-bucket/vpc.zip"
}

module "vpc" {
  source = "gcs::https://www.googleapis.com/storage/v1/my-bucket/vpc.zip"
}
```

### HTTP

```hcl
module "vpc" {
  source = "https://example.com/vpc-module.zip"
}
```

---

## 8. Private Registry (HCP Terraform)

### 8.1 Private Registry 목적

- 조직 내 Module 공유
- 접근 제어
- 버전 관리
- 문서화 자동화

### 8.2 Private Module 게시

**1. Module Repository 준비:**

- GitHub/GitLab/Bitbucket 저장소
- 이름 형식: `terraform-<PROVIDER>-<NAME>` (예: `terraform-aws-mymodule`)
- Semantic version tag (예: `v1.0.0`)

**2. HCP Terraform 에 게시:**

- Registry → Modules → Publish
- VCS Provider 선택
- Repository 선택
- 자동 감지된 tags → 버전 생성

**3. 사용:**

```hcl
module "mymodule" {
  source  = "app.terraform.io/my-org/mymodule/aws"
  version = "1.0.0"
}
```

### 8.3 Private Module 접근

```bash
terraform login
```

Token 이 `~/.terraform.d/credentials.tfrc.json` 에 저장됨.

---

## 9. Private Provider Registry

### 자체 Provider 게시

```hcl
terraform {
  required_providers {
    custom = {
      source  = "app.terraform.io/my-org/custom"
      version = "~> 1.0"
    }
  }
}
```

---

## 10. Fork & Customization

### 시나리오

공개 Module 이 요구사항을 90% 만족하지만 커스터마이징 필요.

### 옵션 1: Wrapper Module

```hcl
# my-vpc/main.tf
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  # 조직 표준값
  enable_nat_gateway = true
  enable_flow_log    = true
  # ...
}

# 추가 리소스
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.us-east-1.s3"
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

### 옵션 2: Fork

```hcl
module "vpc" {
  source = "github.com/my-org/terraform-aws-vpc?ref=v5.1.2-custom"
}
```

### 옵션 3: Contribute Upstream

가능하면 원본에 PR 로 기여.

---

## 11. Registry API

### Public Registry API

```bash
# Module 정보 조회
curl https://registry.terraform.io/v1/modules/terraform-aws-modules/vpc/aws

# 특정 버전
curl https://registry.terraform.io/v1/modules/terraform-aws-modules/vpc/aws/5.1.2

# 다운로드
curl https://registry.terraform.io/v1/modules/terraform-aws-modules/vpc/aws/5.1.2/download
```

### HCP Terraform API

```bash
curl \
  --header "Authorization: Bearer $TF_TOKEN" \
  https://app.terraform.io/api/v2/organizations/my-org/registry-modules
```

---

## 12. Best Practices

### ✅ DO

- **Verified Module 우선 사용**
- **Version constraint 명시** (`~> X.Y` 최소)
- **README 및 examples 확인**
- **Provider 버전 호환성 확인**
- **Wrapper module 로 조직 표준 적용**

### ❌ DON'T

- Version 생략 (매번 최신 다운로드)
- 검증되지 않은 Community module 무작위 사용
- Module 내부 수정 (fork 하세요)
- 프로덕션에 개발 중인 module 사용

---

## 13. 시험 자주 나오는 함정

### 함정 1: Registry Source 문법

```
Q: "hashicorp/vpc/aws" 는 올바른 source?
A: ❌ NO. namespace 는 "terraform-aws-modules" 등.
   확인: registry.terraform.io 검색.
```

### 함정 2: Version 필수 여부

```
Q: Registry module 에 version 은 필수?
A: ❌ 선택 (하지만 권장). 없으면 최신 다운로드.
```

### 함정 3: HCP Private Module URL

```
Q: HCP Private Module 은 어떻게 참조?
A: app.terraform.io/<ORG>/<NAME>/<PROVIDER>
```

### 함정 4: Local vs Registry

```
Q: source = "./modules/vpc" 는 어떤 방식?
A: Local path (Registry 아님).
```

---

## 참고 자료

- [Terraform Registry](https://registry.terraform.io/)
- [Publishing Modules](https://developer.hashicorp.com/terraform/registry/modules/publish)
- [Module Sources](https://developer.hashicorp.com/terraform/language/modules/sources)
- [HCP Terraform Private Registry](https://developer.hashicorp.com/terraform/cloud-docs/registry)
- 관련 문서: [Module 작성](/archive/05-modules/creating-modules/), [Module Versioning](/archive/05-modules/versioning/)
- 실습: [Lab 11: Module Registry](/archive/labs/lab-11-module-registry/readme/)
