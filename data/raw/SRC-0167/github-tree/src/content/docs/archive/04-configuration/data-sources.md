---
title: "Data Sources vs Resources 상세"
description: "Legacy study material imported from 04-configuration/data-sources.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Data Source 개념 완벽 이해
- Resource vs Data Source 차이점
- 주요 AWS Data Sources 활용
- terraform_remote_state 활용
- External data sources 사용법
- Data Source 의 lifecycle 및 종속성 관리

---

## 1. Data Source 란?

### 정의

**Data Source** 는 Terraform 외부에서 정의된 정보를 **읽기 전용**으로 조회하는 방법입니다.

- 기존 인프라 정보 조회
- 다른 Terraform 프로젝트 결과 참조
- 외부 API 호출

### 기본 문법

```hcl
data "<PROVIDER>_<TYPE>" "<NAME>" {
  # 조회 조건 (arguments)
}

# 참조: data.<PROVIDER>_<TYPE>.<NAME>.<ATTRIBUTE>
```

---

## 2. Resource vs Data Source

### 비교표

| 특성 | Resource | Data Source |
|------|----------|-------------|
| 문법 | `resource "type" "name"` | `data "type" "name"` |
| 목적 | 인프라 생성/관리 | 정보 조회 |
| State 저장 | ✅ | ✅ (read-only) |
| 변경 가능 | ✅ | ❌ (읽기 전용) |
| 생성 | ✅ Terraform 이 생성 | ❌ 이미 존재해야 함 |
| 삭제 | ✅ destroy 로 제거 | ❌ destroy 영향 없음 |
| Plan 기호 | `+`, `~`, `-`, `-/+` | `<=` (read) |
| API 호출 | Plan/Apply 시 | Plan 시 (refresh) |

### 예제 비교

**Resource (생성):**
```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "my-logs-bucket"
}
```

**Data Source (조회):**
```hcl
data "aws_s3_bucket" "existing_logs" {
  bucket = "existing-logs-bucket"
}
```

---

## 3. 자주 사용하는 AWS Data Sources

### 3.1 aws_ami - AMI 조회

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}
```

### 3.2 aws_availability_zones - AZ 목록

```hcl
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "public" {
  count             = length(data.aws_availability_zones.available.names)
  vpc_id            = aws_vpc.main.id
  availability_zone = data.aws_availability_zones.available.names[count.index]
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
}
```

### 3.3 aws_caller_identity - 현재 계정 정보

```hcl
data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "user_arn" {
  value = data.aws_caller_identity.current.arn
}
```

### 3.4 aws_region - 현재 리전

```hcl
data "aws_region" "current" {}

locals {
  region_name = data.aws_region.current.name
  region_desc = data.aws_region.current.description
}
```

### 3.5 aws_vpc - 기존 VPC 조회

```hcl
data "aws_vpc" "default" {
  default = true
}

data "aws_vpc" "by_tag" {
  tags = {
    Name = "production-vpc"
  }
}

resource "aws_subnet" "extra" {
  vpc_id     = data.aws_vpc.default.id
  cidr_block = "172.31.100.0/24"
}
```

### 3.6 aws_subnets - Subnets 조회

```hcl
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  tags = {
    Tier = "private"
  }
}

resource "aws_instance" "app" {
  count     = 3
  subnet_id = data.aws_subnets.private.ids[count.index]
}
```

### 3.7 aws_iam_policy_document - IAM Policy 작성

```hcl
data "aws_iam_policy_document" "s3_read" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.data.arn,
      "${aws_s3_bucket.data.arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "s3_read" {
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.s3_read.json
}
```

### 3.8 aws_secretsmanager_secret_version - 시크릿 조회

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "example" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```

### 3.9 aws_ssm_parameter - SSM 파라미터

```hcl
data "aws_ssm_parameter" "database_url" {
  name = "/prod/app/database_url"
}

resource "aws_lambda_function" "app" {
  environment {
    variables = {
      DATABASE_URL = data.aws_ssm_parameter.database_url.value
    }
  }
}
```

---

## 4. terraform_remote_state - 원격 State 참조

### 목적

다른 Terraform 프로젝트의 output 을 참조합니다.

### S3 Backend

```hcl
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "my-terraform-state"
    key    = "networking/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.network.outputs.private_subnet_id
  vpc_security_group_ids = [
    data.terraform_remote_state.network.outputs.app_sg_id
  ]
}
```

### HCP Terraform (cloud block)

```hcl
data "terraform_remote_state" "network" {
  backend = "remote"

  config = {
    organization = "my-org"

    workspaces = {
      name = "network-prod"
    }
  }
}
```

### Local

```hcl
data "terraform_remote_state" "shared" {
  backend = "local"

  config = {
    path = "../shared/terraform.tfstate"
  }
}
```

⚠️ **주의:** State 파일의 **outputs 만** 접근 가능. Resource 속성 직접 접근 불가.

---

## 5. External Data Source

### 목적

외부 스크립트/명령어의 결과를 Terraform 으로 가져오기.

### 기본 사용

**data.tf:**
```hcl
data "external" "app_version" {
  program = ["bash", "${path.module}/scripts/get_version.sh"]

  query = {
    environment = "prod"
    service     = "webapp"
  }
}
```

**scripts/get_version.sh:**
```bash
#!/bin/bash

# stdin 으로 query 를 JSON 으로 받음
eval "$(jq -r '@sh "ENVIRONMENT=\(.environment) SERVICE=\(.service)"')"

# 처리
VERSION=$(curl -s "https://api.example.com/versions/${SERVICE}/${ENVIRONMENT}")

# stdout 으로 JSON 반환
jq -n --arg v "$VERSION" '{"version": $v}'
```

**활용:**
```hcl
resource "aws_lambda_function" "app" {
  environment {
    variables = {
      APP_VERSION = data.external.app_version.result.version
    }
  }
}
```

### 제약사항

- 결과는 반드시 **map(string)** 형식 JSON
- 외부 스크립트에 의존 → 이식성 저하
- **최후 수단**으로 사용

---

## 6. HTTP Data Source

### 목적

HTTP 요청으로 데이터 가져오기.

```hcl
data "http" "my_ip" {
  url = "https://ipinfo.io/ip"

  request_headers = {
    Accept = "text/plain"
  }
}

resource "aws_security_group_rule" "office_access" {
  cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  type        = "ingress"
}
```

---

## 7. Data Source 종속성

### 암시적 종속성

```hcl
data "aws_ami" "ubuntu" {
  # ...
}

resource "aws_instance" "web" {
  ami = data.aws_ami.ubuntu.id   # 자동 종속성
}
```

### 명시적 depends_on

```hcl
data "aws_iam_role" "app_role" {
  name = aws_iam_role.app.name

  depends_on = [
    aws_iam_role_policy_attachment.app_policy
  ]
}
```

⚠️ Data Source 의 `depends_on` 은 Terraform 이 refresh 를 지연시키게 만듭니다.

---

## 8. Data Source with count / for_each

### count

```hcl
data "aws_instance" "app_servers" {
  count = length(var.instance_names)

  filter {
    name   = "tag:Name"
    values = [var.instance_names[count.index]]
  }
}

output "instance_ips" {
  value = data.aws_instance.app_servers[*].public_ip
}
```

### for_each

```hcl
data "aws_ami" "distros" {
  for_each = toset(["ubuntu", "amazon-linux", "debian"])

  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["*${each.key}*"]
  }
}
```

---

## 9. Data Source Lifecycle

### 언제 실행되나?

- **Plan 시:** 항상 refresh (최신 데이터 조회)
- **Apply 시:** 이미 refresh 됨, 다시 조회 안 함
- **Refresh 시:** 최신 데이터로 업데이트

### -refresh=false

```bash
terraform plan -refresh=false   # Data source refresh 건너뜀
```

⚠️ Data source 결과가 이미 있으면 그것을 사용. 없으면 에러.

---

## 10. 실전 시나리오

### 시나리오 1: 기존 인프라 통합

**상황:** 이미 존재하는 VPC 에 새 EC2 배포

```hcl
data "aws_vpc" "existing" {
  tags = {
    Name = "shared-vpc"
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }

  filter {
    name   = "tag:Type"
    values = ["public"]
  }
}

resource "aws_instance" "new_web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = data.aws_subnets.public.ids[0]
}
```

### 시나리오 2: Cross-account 참조

```hcl
provider "aws" {
  alias  = "shared_services"
  region = "us-east-1"

  assume_role {
    role_arn = "arn:aws:iam::999999999999:role/CrossAccountRead"
  }
}

data "aws_ami" "shared_ami" {
  provider = aws.shared_services

  most_recent = true
  filter {
    name   = "name"
    values = ["golden-image-*"]
  }
}

resource "aws_instance" "app" {
  ami = data.aws_ami.shared_ami.id
}
```

### 시나리오 3: Multi-Region

```hcl
provider "aws" {
  alias  = "primary"
  region = "us-east-1"
}

provider "aws" {
  alias  = "dr"
  region = "us-west-2"
}

data "aws_availability_zones" "primary_azs" {
  provider = aws.primary
  state    = "available"
}

data "aws_availability_zones" "dr_azs" {
  provider = aws.dr
  state    = "available"
}

output "region_azs" {
  value = {
    primary = data.aws_availability_zones.primary_azs.names
    dr      = data.aws_availability_zones.dr_azs.names
  }
}
```

### 시나리오 4: Multi-Project State 통합

```hcl
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "my-tfstate"
    key    = "network/prod.tfstate"
    region = "us-east-1"
  }
}

data "terraform_remote_state" "database" {
  backend = "s3"
  config = {
    bucket = "my-tfstate"
    key    = "database/prod.tfstate"
    region = "us-east-1"
  }
}

resource "aws_ecs_service" "app" {
  cluster = data.terraform_remote_state.network.outputs.ecs_cluster_id
  
  network_configuration {
    subnets = data.terraform_remote_state.network.outputs.private_subnet_ids
  }
}

resource "aws_ecs_task_definition" "app" {
  container_definitions = jsonencode([{
    environment = [
      {
        name  = "DB_ENDPOINT"
        value = data.terraform_remote_state.database.outputs.db_endpoint
      }
    ]
  }])
}
```

---

## 11. Best Practices

### ✅ DO

- **Data Source 로 기존 인프라 참조** (하드코딩 대신)
- **filter/tags 로 명확히 조회** (여러 매칭 방지)
- **most_recent = true** 로 최신 AMI 조회
- **terraform_remote_state** 는 outputs 만 사용
- **Sensitive data 는 Secrets Manager/SSM 활용**

### ❌ DON'T

- Data Source 로 자기 프로젝트의 리소스 조회 (직접 참조하세요)
- `most_recent = false` 없이 여러 결과 매칭
- external data source 남용 (스크립트 의존성 증가)
- HTTP data source 로 매번 다른 데이터 (drift 유발)

---

## 12. 시험 자주 나오는 함정

### 함정 1: Data Source 는 destroy 되지 않음

```
Q: terraform destroy 시 data source 도 삭제되나요?
A: ❌ NO. Data source 는 외부 리소스를 조회만. destroy 영향 없음.
```

### 함정 2: State 저장 여부

```
Q: Data source 의 결과는 State 에 저장되나요?
A: ✅ YES. Refresh 시 최신화되지만 State 에 저장됨.
```

### 함정 3: terraform_remote_state 는 무엇 접근?

```
Q: terraform_remote_state 로 resource 속성 직접 접근 가능?
A: ❌ NO. outputs 만 접근 가능. Resource 는 원본 state 에서 output 으로 노출 필요.
```

### 함정 4: Data Source refresh 시점

```
Q: Data source 는 언제 refresh 되나요?
A: terraform plan 실행 시 매번 (unless -refresh=false).
```

---

## 참고 자료

- [Data Sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [terraform_remote_state](https://developer.hashicorp.com/terraform/language/state/remote-state-data)
- [external Provider](https://registry.terraform.io/providers/hashicorp/external/latest/docs)
- [AWS Provider Data Sources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- 관련 문서: [Variables 상세](/archive/04-configuration/variables-outputs/), [Functions 상세](/archive/04-configuration/functions/)
- 실습: [Lab 03: Data Sources](/archive/labs/lab-03-data-sources/readme/)
