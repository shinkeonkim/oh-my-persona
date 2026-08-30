---
title: "Week 4: Terraform Configuration (HCL)"
description: "Legacy study material imported from 04-configuration/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- HCL 문법 완벽 숙달
- Variables, Outputs 활용
- Data Sources vs Resources 이해
- Built-in Functions 활용
- Complex Types 이해

---

## 1. HCL 기본 문법

### Block 구조

```hcl
<BLOCK_TYPE> "<BLOCK_LABEL>" "<BLOCK_NAME>" {
  <ARGUMENT_NAME> = <ARGUMENT_VALUE>
  
  <NESTED_BLOCK> {
    <ARGUMENT> = <VALUE>
  }
}
```

### 주요 Block 타입

**resource:**
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```

**data:**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
}
```

**variable:**
```hcl
variable "instance_type" {
  type    = string
  default = "t2.micro"
}
```

**output:**
```hcl
output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

**locals:**
```hcl
locals {
  common_tags = {
    Environment = "prod"
    ManagedBy   = "Terraform"
  }
}
```

**module:**
```hcl
module "vpc" {
  source = "./modules/vpc"
  cidr   = "10.0.0.0/16"
}
```

---

## 2. Variables

### 정의

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
  sensitive   = false
  
  validation {
    condition     = can(regex("^t[2-3]\\.", var.instance_type))
    error_message = "Must be t2 or t3 family"
  }
}
```

### Variable Types

**Primitive:**
```hcl
variable "name" {
  type = string
}

variable "count" {
  type = number
}

variable "enabled" {
  type = bool
}
```

**Collection:**
```hcl
variable "azs" {
  type = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "tags" {
  type = map(string)
  default = {
    Environment = "dev"
  }
}

variable "unique_azs" {
  type = set(string)
}
```

**Structural:**
```hcl
variable "server_config" {
  type = object({
    name          = string
    instance_type = string
    disk_size     = number
    monitoring    = bool
  })
}

variable "ports" {
  type = tuple([string, number, bool])
}
```

### Variable 값 제공

**1. CLI:**
```bash
terraform apply -var="instance_type=t3.small"
```

**2. 파일:**
```hcl
instance_type = "t3.small"
```
```bash
terraform apply -var-file="prod.tfvars"
```

**3. 환경 변수:**
```bash
export TF_VAR_instance_type="t3.small"
terraform apply
```

**4. 자동 로드:**
- `terraform.tfvars`
- `*.auto.tfvars`

### Precedence (우선순위)

```
1. -var (최우선)
2. -var-file
3. terraform.tfvars
4. *.auto.tfvars
5. TF_VAR_*
6. default 값 (최하위)
```

---

## 3. Outputs

### 정의

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
  sensitive   = false
}

output "instance_ips" {
  value = {
    public  = aws_instance.web.public_ip
    private = aws_instance.web.private_ip
  }
}
```

### 조회

```bash
terraform output

terraform output instance_id

terraform output -json

terraform output -raw instance_id
```

### Module Outputs

```hcl
module "vpc" {
  source = "./modules/vpc"
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

---

## 4. Data Sources

### Resource vs Data Source

| Resource | Data Source |
|----------|-------------|
| `resource "type" "name"` | `data "type" "name"` |
| 생성/관리 | 조회 |
| State 저장 | State 저장 안 됨 |
| 변경 가능 | 읽기 전용 |

### 예시

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

---

## 5. Built-in Functions

### 숫자 함수

```hcl
length([1, 2, 3])

max(12, 54, 3)

min(12, 54, 3)

ceil(5.1)

floor(5.9)
```

### 문자열 함수

```hcl
lower("HELLO")

upper("hello")

title("hello world")

split("-", "foo-bar-baz")

join("-", ["foo", "bar"])

replace("hello", "l", "L")

substr("hello", 0, 2)

format("Hello, %s!", "World")
```

### 컬렉션 함수

```hcl
concat([1, 2], [3, 4])

merge({a = 1}, {b = 2})

lookup({a = 1, b = 2}, "a", 0)

keys({a = 1, b = 2})

values({a = 1, b = 2})

contains(["a", "b"], "a")

flatten([[1, 2], [3, 4]])
```

### 타입 변환

```hcl
tostring(42)

tonumber("42")

tobool("true")

tolist(toset([1, 2, 2]))

toset([1, 2, 2])

tomap({a = "1", b = "2"})
```

### 파일 함수

```hcl
file("${path.module}/userdata.sh")

filebase64("image.png")

templatefile("config.tpl", { name = "example" })
```

---

## 6. Expressions

### 조건식

```hcl
condition ? true_val : false_val

var.environment == "prod" ? "t3.large" : "t2.micro"
```

### For Expressions

```hcl
[for s in var.list : upper(s)]

{for k, v in var.map : k => upper(v)}

[for s in var.list : upper(s) if s != ""]
```

### Splat Expressions

```hcl
aws_instance.example[*].id

aws_instance.example[*].public_ip
```

---

더 많은 내용은 다음 파일 참고:
- [Variables 상세](/archive/04-configuration/variables-outputs/)
- [Functions 상세](/archive/04-configuration/functions/)
- [Complex Types](/archive/04-configuration/complex-types/)

---

## 참고 자료

- [Configuration Language](https://developer.hashicorp.com/terraform/language)
- [Variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Functions](https://developer.hashicorp.com/terraform/language/functions)
