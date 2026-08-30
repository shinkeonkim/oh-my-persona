---
title: "Week 1-2: Infrastructure as Code 개념 및 Terraform 기초"
description: "Legacy study material imported from 01-iac-concepts/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Infrastructure as Code (IaC) 개념 완벽 이해
- Terraform의 목적과 장점 파악
- 기본 워크플로우 익히기
- Terraform 설치 및 초기 환경 구성

---

## 1. Infrastructure as Code (IaC)란?

### 정의

**Infrastructure as Code (IaC)** 는 인프라를 코드로 정의하고 관리하는 방법론입니다.

### 전통적 방식 vs IaC

| 전통적 방식 | Infrastructure as Code |
|------------|------------------------|
| GUI 클릭 또는 수동 명령 | 코드로 인프라 정의 |
| 문서로만 기록 | 코드 자체가 문서 |
| 재현성 낮음 | 완벽한 재현 가능 |
| 변경 이력 추적 어려움 | Git으로 버전 관리 |
| 협업 어려움 | 코드 리뷰, PR 가능 |
| 수동 작업, 실수 가능성 | 자동화, 일관성 보장 |

### IaC의 장점

**1. 재현성 (Reproducibility)**
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```
→ 언제 어디서나 동일한 인프라 생성

**2. 버전 관리 (Version Control)**
```bash
git log infrastructure.tf
git diff v1.0..v2.0
```
→ 모든 변경사항 추적 가능

**3. 자동화 (Automation)**
```bash
terraform apply -auto-approve
```
→ CI/CD 파이프라인 통합

**4. 문서화 (Documentation)**
- 코드 = 실제 인프라 상태
- 주석으로 의도 명확히 전달
- README로 사용법 설명

**5. 협업 (Collaboration)**
```bash
git checkout -b feature/add-load-balancer
terraform plan
# PR 생성 및 리뷰
```

**6. 비용 절감**
- 인프라 복제 시간 단축
- 실수로 인한 비용 감소
- 표준화로 효율성 증가

---

## 2. Declarative vs Imperative

### Declarative (선언적) - Terraform

**"무엇을" 원하는지 정의**

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  count         = 3
}
```

**특징:**
- 최종 상태 명시
- Terraform이 현재→원하는 상태로 자동 변환
- 멱등성 (Idempotent) - 여러 번 실행해도 결과 동일
- 순서 신경 쓸 필요 없음

### Imperative (명령적) - Shell Scripts

**"어떻게" 만들지 단계별 명령**

```bash
#!/bin/bash
for i in {1..3}; do
  aws ec2 run-instances \
    --image-id ami-12345678 \
    --instance-type t2.micro \
    --count 1
done
```

**특징:**
- 단계별 명령 실행
- 순서 중요
- 중간 실패 시 복구 어려움
- 멱등성 보장 안 됨

### 비교 예시

**시나리오: EC2 인스턴스 3개 → 5개로 증가**

**Declarative (Terraform):**
```hcl
resource "aws_instance" "web" {
  count = 5
}
```
→ Terraform이 "2개 추가 필요"를 자동 계산

**Imperative (Shell):**
```bash
for i in {4..5}; do
  aws ec2 run-instances ...
done
```
→ 직접 "2개 추가"를 계산하고 명령

---

## 3. Terraform이란?

### 정의

**Terraform**은 HashiCorp에서 만든 **오픈소스 IaC 도구**입니다.

### 주요 특징

**1. Provider 기반 아키텍처**
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

**지원 Provider:**
- **Public Cloud**: AWS, Azure, GCP, Oracle Cloud
- **Private Cloud**: VMware vSphere, OpenStack
- **SaaS**: GitHub, Datadog, PagerDuty, Cloudflare
- **Database**: PostgreSQL, MySQL, MongoDB
- **Networking**: Palo Alto, Cisco, F5

**2. State 관리**
- 현재 인프라 상태를 `terraform.tfstate` 파일에 저장
- 변경 전후 비교 가능
- 원격 State로 팀 협업 지원

**3. 계획 및 적용 분리**
```bash
terraform plan
terraform apply
```
→ 변경 전 미리 확인 가능

**4. 그래프 기반 종속성 관리**
```hcl
resource "aws_vpc" "main" { }

resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
}
```
→ VPC 먼저, Subnet 나중에 자동 생성

---

## 4. Terraform vs 다른 도구

### Terraform vs CloudFormation

| Terraform | AWS CloudFormation |
|-----------|---------------------|
| 멀티 클라우드 | AWS 전용 |
| HCL (읽기 쉬움) | YAML/JSON |
| 계획 미리보기 강력 | Change Set 제공 |
| 커뮤니티 Provider 풍부 | AWS 리소스만 |

### Terraform vs Ansible

| Terraform | Ansible |
|-----------|---------|
| 인프라 프로비저닝 | 구성 관리 (Configuration) |
| Declarative | Imperative (Playbook) |
| State 관리 | Stateless |
| 인프라 생성/변경/삭제 | 소프트웨어 설치/설정 |

**함께 사용:**
```
Terraform: EC2 인스턴스 생성
   ↓
Ansible: 인스턴스 내부 소프트웨어 설치/설정
```

---

## 5. Terraform 사용 사례

### Use Case 1: 멀티 클라우드 인프라

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "azurerm" {
  features {}
}

resource "aws_s3_bucket" "data" { }

resource "azurerm_storage_account" "backup" { }
```

### Use Case 2: 환경별 인프라 복제

```bash
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

terraform workspace select prod
terraform apply
```

### Use Case 3: 재해 복구 (DR)

```hcl
module "primary" {
  source = "./infrastructure"
  region = "us-east-1"
}

module "dr" {
  source = "./infrastructure"
  region = "us-west-2"
}
```

### Use Case 4: 일시적 환경

```bash
terraform apply

terraform destroy
```
→ 테스트 환경을 즉시 생성/삭제

---

## 6. Terraform 핵심 개념

### 6.1 Provider

**외부 API와 통신하는 플러그인**

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
  region     = "us-east-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}
```

### 6.2 Resource

**관리할 인프라 구성 요소**

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
  }
}
```

### 6.3 Data Source

**기존 인프라 정보 조회**

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/*"]
  }
}

resource "aws_instance" "web" {
  ami = data.aws_ami.ubuntu.id
}
```

### 6.4 State

**현재 인프라 상태 저장**

```json
{
  "version": 4,
  "resources": [
    {
      "type": "aws_instance",
      "name": "web",
      "instances": [{
        "attributes": {
          "id": "i-1234567890abcdef0",
          "public_ip": "54.123.45.67"
        }
      }]
    }
  ]
}
```

### 6.5 Module

**재사용 가능한 Terraform 코드 묶음**

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
}
```

---

## 7. Terraform 워크플로우

### 기본 워크플로우

```
1. Write → 2. Init → 3. Plan → 4. Apply → 5. Destroy
```

**1. Write**
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
}
```

**2. Init**
```bash
terraform init
```
- Provider 다운로드
- Backend 초기화
- Module 다운로드

**3. Plan**
```bash
terraform plan
```
- 변경 사항 미리보기
- State와 구성 비교

**4. Apply**
```bash
terraform apply
```
- 인프라 변경 실행
- State 업데이트

**5. Destroy**
```bash
terraform destroy
```
- 모든 관리 리소스 삭제

---

## 8. 실습 준비

### 8.1 Terraform 설치

**macOS:**
```bash
brew install terraform

terraform version
```

**Linux:**
```bash
wget https://releases.hashicorp.com/terraform/1.12.0/terraform_1.12.0_linux_amd64.zip
unzip terraform_1.12.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

terraform version
```

**Windows:**
```powershell
choco install terraform

terraform version
```

### 8.2 AWS CLI 설정

```bash
aws configure

# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json

aws sts get-caller-identity
```

### 8.3 첫 번째 프로젝트

**디렉토리 생성:**
```bash
mkdir terraform-hello-world
cd terraform-hello-world
```

**main.tf 작성:**
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
  region = "ap-northeast-2"
}

resource "aws_s3_bucket" "example" {
  bucket = "terraform-hello-world-YOUR_NAME"

  tags = {
    Name        = "Hello World"
    Environment = "Learning"
  }
}
```

**실행:**
```bash
terraform init

terraform plan

terraform apply

terraform destroy
```

---

## 9. 핵심 요약

### IaC 핵심 개념
- ✅ 인프라를 코드로 관리
- ✅ 재현 가능, 버전 관리, 자동화
- ✅ Declarative (선언적) 접근

### Terraform 특징
- ✅ 멀티 클라우드 지원
- ✅ Provider 기반 확장
- ✅ State 관리
- ✅ 계획 → 적용 분리

### 기본 워크플로우
```
Write → Init → Plan → Apply → Destroy
```

---

## 10. 다음 단계

- [Terraform 설치 가이드](/archive/01-iac-concepts/installation/)
- [첫 번째 프로젝트 실습](/archive/01-iac-concepts/first-project/)
- [Week 3: Core Terraform Workflow](/archive/03-core-workflow/readme/)

---

## 참고 자료

- [HashiCorp Learn: IaC](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004#learn-about-infrastructure-as-code-iac)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [What is Terraform?](https://developer.hashicorp.com/terraform/intro)
