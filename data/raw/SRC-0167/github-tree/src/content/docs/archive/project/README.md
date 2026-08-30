---
title: "HashiCorp Terraform Associate (004) 완벽 학습 가이드"
description: "Legacy study material imported from README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

> 이 자료는 이제 Astro Starlight 정적 웹 사이트로 제공됩니다. 기존 Markdown은 원본 자료로 보존되며, 빌드 시 검색 가능한 웹 페이지로 자동 변환됩니다.  
> This guide is now delivered as an Astro Starlight static site. Existing Markdown remains the source material and is imported into searchable web pages during each build.

## 웹 사이트 실행 / Run the website

```bash
bun install --frozen-lockfile
bun run dev
```

Production 정적 파일은 `bun run build` 후 `dist/`에 생성됩니다. 검색은 production build에서 Pagefind로 동작하므로 `bun run build` 후 `bun run preview`로 확인하세요.

The default deployment origin is `https://terraform-study.shinkeonkim.com`. Override `SITE_URL` only for another environment.

```bash
SITE_URL="https://preview.example.com" bun run build
```

공식 `web-unified-docs` v1.12 소스 인덱스는 `bun run sources:update`로 갱신합니다.

## 📋 목차

1. [자격증 개요](#자격증-개요)
2. [학습 커리큘럼](#학습-커리큘럼)
3. [시험 준비 전략](#시험-준비-전략)
4. [다음 단계](#다음-단계)
5. [공식 참고 자료](#공식-참고-자료)

---

## 자격증 개요

### HashiCorp Terraform Associate (004) 란?

HashiCorp Terraform Associate 자격증은 **Infrastructure as Code (IaC)** 의 기본 개념과 Terraform의 핵심 기능을 검증하는 공인 자격증입니다.

### 시험 정보

| 항목 | 내용 |
|------|------|
| **시험 코드** | Terraform Associate 004 |
| **시험 형식** | 온라인 감독 (Online Proctored) |
| **문제 수** | 약 57문항 |
| **시험 시간** | 60분 (1시간) |
| **문제 유형** | 단일 선택, 다중 선택, 참/거짓 |
| **합격 점수** | 약 70% (공식 미공개) |
| **응시 비용** | $70.50 USD |
| **유효 기간** | 2년 |
| **테스트 버전** | Terraform 1.12 |
| **언어** | 영어 |

### 003 vs 004 주요 변경사항

| 영역 | 003 버전 | 004 버전 |
|------|----------|----------|
| **Terraform 버전** | 1.3 이전 | 1.12 (최신 기능 포함) |
| **Lifecycle 안전성** | 기본 create/update/destroy | `depends_on`, `create_before_destroy` 심화 |
| **검증** | 최소한의 입력 검증 | Custom conditions (preconditions, postconditions, check blocks) |
| **시크릿 관리** | `sensitive = true` 플래그 | Ephemeral values, write-only arguments |
| **협업** | 제한적인 HCP 커버리지 | HCP Terraform workspaces & projects 핵심 내용 |
| **거버넌스** | 주로 개념적 | 실무 시나리오 기반 거버넌스 및 확장성 |

---

## 학습 커리큘럼

### 8주 완성 학습 플랜

이 커리큘럼은 **주당 8-10시간** 학습을 기준으로 설계되었습니다.

#### Week 1-2: Terraform 기초 및 IaC 개념

**학습 목표:**
- Infrastructure as Code (IaC) 개념 이해
- Terraform의 목적과 장점 파악
- 기본 워크플로우 익히기

**학습 내용:**
1. [IaC 개념 및 Terraform 소개](/archive/01-iac-concepts/readme/)
2. [Terraform 설치 및 초기 설정](/archive/01-iac-concepts/installation/)
3. [첫 번째 Terraform 프로젝트](/archive/01-iac-concepts/first-project/)

**실습:**
- Terraform 설치 및 버전 확인
- AWS/Azure/GCP 중 하나 선택하여 간단한 리소스 생성
- `init → plan → apply → destroy` 워크플로우 실습

**학습 자료:**
- [HashiCorp Learn: Get Started with Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
- [What is Infrastructure as Code?](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004#learn-about-infrastructure-as-code-iac)

---

#### Week 3: Core Terraform Workflow (핵심 워크플로우)

**학습 목표:**
- Terraform CLI 명령어 완벽 이해
- 워크플로우 각 단계의 역할 파악
- 포맷팅 및 검증 도구 활용

**학습 내용:**
1. [Terraform Core Workflow](/archive/03-core-workflow/readme/)
2. [CLI 명령어 상세 가이드](/archive/03-core-workflow/cli-commands/)
3. [State 파일 이해하기](/archive/03-core-workflow/state-basics/)

**핵심 명령어:**
```bash
terraform init      # 작업 디렉토리 초기화, 프로바이더 다운로드
terraform fmt       # 코드 포맷팅
terraform validate  # 구성 검증 (구문 오류 확인)
terraform plan      # 실행 계획 생성 (변경사항 미리보기)
terraform apply     # 인프라 변경 적용
terraform destroy   # 관리 중인 인프라 삭제
```

**실습:**
- 각 명령어를 순차적으로 실행하며 동작 확인
- `terraform plan`의 출력 분석
- State 파일 내용 확인 및 이해

**학습 자료:**
- [The Core Terraform Workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
- [Terraform CLI Documentation](https://developer.hashicorp.com/terraform/cli)

---

#### Week 4: Terraform Configuration (HCL 언어)

**학습 목표:**
- HCL(HashiCorp Configuration Language) 문법 숙달
- Variables, Outputs, Data Sources 활용
- 복잡한 타입 및 표현식 이해

**학습 내용:**
1. [HCL 기본 문법](/archive/04-configuration/readme/)
2. [Variables 및 Outputs](/archive/04-configuration/variables-outputs/)
3. [Data Sources vs Resources](/archive/04-configuration/data-sources/)
4. [Functions 및 Expressions](/archive/04-configuration/functions/)
5. [Complex Types (list, map, object, tuple)](/archive/04-configuration/complex-types/)

**핵심 개념:**

**Variables 정의:**
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
  
  validation {
    condition     = can(regex("^t2\\.", var.instance_type))
    error_message = "Instance type must be in t2 family"
  }
}
```

**Outputs 정의:**
```hcl
output "instance_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.example.public_ip
  sensitive   = false
}
```

**Data Source 사용:**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}
```

**실습:**
- Variables를 사용한 재사용 가능한 구성 작성
- Outputs를 통한 정보 출력
- Data Sources를 활용한 기존 리소스 참조
- Built-in Functions 활용 (`length()`, `lookup()`, `merge()` 등)

**학습 자료:**
- [Terraform Configuration Language](https://developer.hashicorp.com/terraform/language)
- [Variables and Outputs](https://developer.hashicorp.com/terraform/language/values)

---

#### Week 5: Terraform Modules (모듈 시스템)

**학습 목표:**
- Module의 개념과 구조 이해
- Module 작성 및 재사용
- Module 버전 관리

**학습 내용:**
1. [Module 기초](/archive/05-modules/readme/)
2. [Module 작성 가이드](/archive/05-modules/creating-modules/)
3. [Module Registry 활용](/archive/05-modules/registry/)
4. [Module 버전 관리](/archive/05-modules/versioning/)

**Module 구조:**
```
my-module/
├── main.tf          # 주요 리소스 정의
├── variables.tf     # 입력 변수
├── outputs.tf       # 출력 값
├── README.md        # 문서화
└── examples/        # 사용 예제
    └── basic/
        └── main.tf
```

**Module 호출 예제:**
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

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

**실습:**
- 간단한 Module 작성 (예: VPC 모듈)
- Terraform Registry에서 공개 Module 사용
- Module 간 종속성 관리
- Module Output을 다른 Module에서 참조

**학습 자료:**
- [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules)
- [Terraform Registry](https://registry.terraform.io/)

---

#### Week 6: State Management (상태 관리)

**학습 목표:**
- Terraform State의 역할과 중요성 이해
- Remote State 및 State Locking
- State 조작 및 관리 기법

**학습 내용:**
1. [State 파일의 역할](/archive/06-state/readme/)
2. [Remote Backend 설정](/archive/06-state/remote-backend/)
3. [State Locking](/archive/06-state/state-locking/)
4. [State 조작 명령어](/archive/06-state/state-commands/)
5. [Drift Detection 및 해결](/archive/06-state/drift-detection/)

**State Backend 설정 (S3 + DynamoDB):**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

**State 명령어:**
```bash
terraform state list                          # State의 모든 리소스 목록
terraform state show aws_instance.example     # 특정 리소스 상세 정보
terraform state mv SOURCE DESTINATION         # 리소스 이동 또는 이름 변경
terraform state rm ADDRESS                    # State에서 리소스 제거
terraform state pull                          # Remote state 다운로드
terraform import ADDRESS ID                   # 기존 리소스를 State에 임포트
```

**실습:**
- S3 Backend 설정 및 State 마이그레이션
- State Locking 테스트
- `terraform import`를 통한 기존 리소스 가져오기
- Drift 감지 및 해결 시나리오

**학습 자료:**
- [Terraform State](https://developer.hashicorp.com/terraform/language/state)
- [Backend Configuration](https://developer.hashicorp.com/terraform/language/settings/backends/configuration)

---

#### Week 7: Lifecycle & Custom Conditions (004 신규 강화)

**학습 목표:**
- Lifecycle Meta-Arguments 활용
- Custom Conditions을 통한 검증
- Ephemeral Values 및 Write-Only Arguments

**학습 내용:**
1. [Lifecycle Meta-Arguments](/archive/07-lifecycle/readme/)
2. [Custom Conditions](/archive/07-lifecycle/custom-conditions/)
3. [Sensitive Data 관리](/archive/07-lifecycle/sensitive-data/)

**Lifecycle 예제:**
```hcl
resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true  # 재생성 시 새 리소스 먼저 생성
    prevent_destroy       = false # 삭제 방지
    ignore_changes        = [     # 변경 무시
      tags["LastModified"],
    ]
  }

  depends_on = [
    aws_security_group.example  # 명시적 종속성
  ]
}
```

**Custom Conditions (Preconditions/Postconditions):**
```hcl
variable "ami_id" {
  type = string
  
  validation {
    condition     = can(regex("^ami-", var.ami_id))
    error_message = "AMI ID must start with 'ami-'"
  }
}

resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = "t2.micro"

  lifecycle {
    precondition {
      condition     = data.aws_ami.example.architecture == "x86_64"
      error_message = "AMI must be x86_64 architecture"
    }

    postcondition {
      condition     = self.instance_state == "running"
      error_message = "Instance must be in running state"
    }
  }
}
```

**Check Blocks (Terraform 1.5+):**
```hcl
check "health_check" {
  data "http" "app_health" {
    url = "https://${aws_instance.app.public_ip}/health"
  }

  assert {
    condition     = data.http.app_health.status_code == 200
    error_message = "Application health check failed"
  }
}
```

**실습:**
- `create_before_destroy`를 사용한 무중단 배포
- Variable Validation 작성
- Preconditions/Postconditions 활용
- Check Blocks를 통한 인프라 검증

**학습 자료:**
- [Lifecycle Meta-Arguments](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [Custom Conditions](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)

---

#### Week 8: HCP Terraform & 최종 복습

**학습 목표:**
- HCP Terraform (구 Terraform Cloud) 이해
- Workspaces 및 Projects 조직화
- 협업 및 거버넌스 기능
- 최종 모의고사 및 복습

**학습 내용:**
1. [HCP Terraform 개요](/archive/08-hcp-terraform/readme/)
2. [Workspaces vs Projects](/archive/08-hcp-terraform/workspaces-projects/)
3. [Variable Sets 및 Run Triggers](/archive/08-hcp-terraform/variables-triggers/)
4. [Policy as Code (Sentinel/OPA)](/archive/08-hcp-terraform/policy/)
5. [협업 워크플로우](/archive/08-hcp-terraform/collaboration/)

**HCP Terraform 핵심 개념:**

| 기능 | 설명 |
|------|------|
| **Workspaces** | 독립적인 Terraform 실행 환경 (State 분리) |
| **Projects** | 관련 Workspaces를 논리적으로 그룹화 |
| **Variable Sets** | 여러 Workspace에 공유되는 변수 집합 |
| **Run Triggers** | Workspace 간 의존성 및 자동 실행 트리거 |
| **VCS Integration** | GitHub/GitLab 등과 연동한 자동 실행 |
| **Policy Sets** | Sentinel/OPA를 통한 정책 검증 |
| **Drift Detection** | 인프라 Drift 자동 감지 |

**Workspace 설정 예제:**
```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "production-app"
    }
  }
}
```

**실습:**
- HCP Terraform 무료 계정 생성
- VCS 연동 Workspace 생성
- CLI-driven Workflow 실습
- Variable Sets 구성
- Run Triggers 설정

**최종 복습:**
- 모든 도메인 복습
- 예상 문제 풀이 (3세트)
- 취약 영역 집중 학습

**학습 자료:**
- [HCP Terraform Documentation](https://developer.hashicorp.com/terraform/cloud-docs)
- [Workspaces Overview](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)
- [Projects](https://developer.hashicorp.com/terraform/cloud-docs/projects)

---

## 시험 준비 전략

### 시험 도메인 가중치

| 도메인 | 가중치 | 중요도 |
|--------|--------|--------|
| 1. Infrastructure as Code 개념 | 6% | ⭐⭐ |
| 2. Terraform 기초 | 10% | ⭐⭐⭐ |
| 3. Core Terraform Workflow | 16% | ⭐⭐⭐⭐ |
| 4. Terraform Configuration | 26% | ⭐⭐⭐⭐⭐ |
| 5. Terraform Modules | 10% | ⭐⭐⭐ |
| 6. State Management | 16% | ⭐⭐⭐⭐⭐ |
| 7. Maintain Infrastructure | 10% | ⭐⭐⭐ |
| 8. HCP Terraform | 6% | ⭐⭐⭐ |

### 학습 우선순위

**High Priority (60분 중 약 35분):**
1. **Terraform Configuration (26%)** - HCL 문법, Variables, Outputs, Functions
2. **State Management (16%)** - State 파일, Remote Backend, Locking, Drift
3. **Core Workflow (16%)** - CLI 명령어, 워크플로우 순서

**Medium Priority (약 20분):**
4. **Terraform Modules (10%)** - Module 구조, 소싱, 버전 관리
5. **Terraform 기초 (10%)** - Providers, Plugin 아키텍처
6. **Maintain Infrastructure (10%)** - Import, State 조작

**Lower Priority (약 5분):**
7. **HCP Terraform (6%)** - Workspaces, Projects, 협업 기능
8. **IaC 개념 (6%)** - IaC 정의, 장점

### 시험 당일 전략

1. **시간 관리:**
   - 60분 / 57문제 = 문제당 약 1분
   - 확실한 문제는 30초 안에 해결
   - 어려운 문제는 플래그 후 나중에 재검토

2. **문제 읽기:**
   - 키워드에 집중 (always, never, best practice, etc.)
   - 다중 선택 문제는 몇 개를 선택해야 하는지 확인

3. **함정 회피:**
   - `terraform taint` (deprecated) → `-replace` 사용
   - `terraform refresh` (deprecated) → `apply -refresh-only` 사용
   - `sensitive = true`는 CLI 출력만 숨김 (State 파일에는 평문)

4. **검토 시간 확보:**
   - 마지막 10분은 플래그된 문제 재검토

---

## 다음 단계

각 주차별 상세 학습 내용은 다음 문서를 참고하세요:

- [Week 1-2: IaC 개념 및 Terraform 기초](/archive/01-iac-concepts/readme/)
- [Week 3: Core Terraform Workflow](/archive/03-core-workflow/readme/)
- [Week 4: Terraform Configuration](/archive/04-configuration/readme/)
- [Week 5: Terraform Modules](/archive/05-modules/readme/)
- [Week 6: State Management](/archive/06-state/readme/)
- [Week 7: Lifecycle & Custom Conditions](/archive/07-lifecycle/readme/)
- [Week 8: HCP Terraform](/archive/08-hcp-terraform/readme/)
- [실습 가이드](/archive/labs/readme/)
- [예상 문제 풀이](/archive/practice-exams/readme/)

---

## 공식 참고 자료

### HashiCorp 공식 자료
- [Terraform Associate 004 Learning Path](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004)
- [Exam Content List (004)](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004)
- [Sample Questions (004)](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-questions-004)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Certification Page](https://www.hashicorp.com/certification/terraform-associate)

### 커뮤니티 자료
- [Terraform Registry](https://registry.terraform.io/)
- [HashiCorp Discuss Forum](https://discuss.hashicorp.com/)
- [Terraform GitHub](https://github.com/hashicorp/terraform)

---

**Good luck with your certification journey! 🚀**
