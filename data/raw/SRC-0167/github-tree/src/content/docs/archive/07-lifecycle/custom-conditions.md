---
title: "Custom Conditions 완전 정복 (004 신규)"
description: "Legacy study material imported from 07-lifecycle/custom-conditions.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Variable Validation 작성
- Preconditions/Postconditions 활용 (Terraform 1.2+)
- Check Blocks 사용 (Terraform 1.5+)
- Cross-Variable Validation (Terraform 1.9+)

---

## 1. Custom Conditions 개요

**Custom Conditions** 는 인프라 무결성을 코드로 검증하는 방법.

### 종류

| 종류 | Terraform 버전 | 목적 |
|------|---------------|------|
| Variable Validation | 0.13+ | 입력 검증 |
| Preconditions | 1.2+ | 리소스 생성 전 검증 |
| Postconditions | 1.2+ | 리소스 생성 후 검증 |
| Check Blocks | 1.5+ | 지속적 인프라 검증 |

---

## 2. Variable Validation

### 기본 사용

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}
```

### Regex 활용

```hcl
variable "ami_id" {
  type = string

  validation {
    condition     = can(regex("^ami-[a-f0-9]{8,17}$", var.ami_id))
    error_message = "Invalid AMI ID format."
  }
}
```

### 여러 Validation

```hcl
variable "instance_type" {
  type = string

  validation {
    condition     = can(regex("^t[2-3]\\.", var.instance_type))
    error_message = "Must be t2 or t3 family."
  }

  validation {
    condition     = !endswith(var.instance_type, ".nano")
    error_message = "Nano instances not allowed."
  }
}
```

### Cross-Variable Validation (Terraform 1.9+)

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

## 3. Preconditions

### 리소스 생성 전 검증

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/*"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  lifecycle {
    precondition {
      condition     = data.aws_ami.ubuntu.architecture == "x86_64"
      error_message = "AMI must be x86_64."
    }

    precondition {
      condition     = data.aws_ami.ubuntu.root_device_type == "ebs"
      error_message = "AMI must use EBS."
    }
  }
}
```

### 실전 예제

```hcl
resource "aws_db_instance" "main" {
  # ...

  lifecycle {
    precondition {
      condition     = var.environment == "prod" ? var.multi_az : true
      error_message = "Multi-AZ required for prod."
    }

    precondition {
      condition     = var.backup_retention >= 7
      error_message = "Backup retention must be >= 7 days."
    }
  }
}
```

---

## 4. Postconditions

### 리소스 생성 후 검증

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  lifecycle {
    postcondition {
      condition     = self.instance_state == "running"
      error_message = "Instance must be running."
    }

    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have public IP."
    }
  }
}
```

**`self` 참조:** 현재 리소스의 속성 참조.

### Data Source 에도 적용

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  lifecycle {
    postcondition {
      condition     = self.tags["Verified"] == "true"
      error_message = "AMI must have Verified tag."
    }
  }
}
```

---

## 5. Check Blocks (Terraform 1.5+)

### 목적

**Non-blocking** 인프라 검증 (경고만, apply 는 진행).

### 기본 구조

```hcl
check "health_check" {
  data "http" "example" {
    url = "https://${aws_instance.web.public_ip}/health"
  }

  assert {
    condition     = data.http.example.status_code == 200
    error_message = "Health check failed: ${data.http.example.status_code}"
  }
}
```

### 여러 assert

```hcl
check "database_health" {
  data "external" "db_check" {
    program = ["python3", "${path.module}/check_db.py"]
  }

  assert {
    condition     = data.external.db_check.result.status == "ok"
    error_message = "Database not healthy."
  }

  assert {
    condition     = tonumber(data.external.db_check.result.latency_ms) < 100
    error_message = "Database latency too high."
  }
}
```

### 리소스 참조

```hcl
check "s3_bucket_public_access" {
  assert {
    condition = aws_s3_bucket_public_access_block.example.block_public_acls
    error_message = "S3 bucket must block public ACLs."
  }
}
```

---

## 6. Precondition vs Postcondition vs Check

| | Precondition | Postcondition | Check |
|-|--------------|---------------|-------|
| 위치 | lifecycle 블록 | lifecycle 블록 | 최상위 block |
| 실행 시점 | 리소스 생성 전 | 리소스 생성 후 | 매 refresh 시 |
| 실패 시 | Apply 중단 | Apply 중단 | 경고만 |
| Terraform 버전 | 1.2+ | 1.2+ | 1.5+ |
| self 참조 | ❌ | ✅ | 옵션 |

### 언제 어떤 것?

- **Variable Validation** → 사용자 입력 검증
- **Precondition** → 데이터 소스, 종속성 검증
- **Postcondition** → 리소스 결과 검증
- **Check Block** → 지속적 헬스체크 (배포 후에도)

---

## 7. 실전 시나리오

### 시나리오 1: Prod 안전 장치

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Invalid environment."
  }
}

variable "instance_type" {
  type = string

  validation {
    condition     = !(var.environment == "prod" && var.instance_type == "t3.micro")
    error_message = "Prod cannot use t3.micro."
  }
}

resource "aws_db_instance" "main" {
  # ...

  lifecycle {
    precondition {
      condition     = var.environment != "prod" || var.multi_az
      error_message = "Prod requires multi_az."
    }

    postcondition {
      condition     = self.backup_retention_period >= 7
      error_message = "Backup retention < 7 days."
    }
  }
}
```

### 시나리오 2: 지속적 헬스체크

```hcl
resource "aws_lb" "web" { ... }

check "web_health" {
  data "http" "web" {
    url = "https://${aws_lb.web.dns_name}/health"
  }

  assert {
    condition     = data.http.web.status_code == 200
    error_message = "Web health check failed."
  }

  assert {
    condition     = can(jsondecode(data.http.web.response_body).status == "ok")
    error_message = "Web response invalid."
  }
}
```

### 시나리오 3: 종속성 검증

```hcl
data "aws_vpc" "main" {
  tags = { Name = var.vpc_name }
}

resource "aws_instance" "app" {
  subnet_id = var.subnet_id

  lifecycle {
    precondition {
      condition     = contains(data.aws_subnets.vpc.ids, var.subnet_id)
      error_message = "Subnet must be in VPC ${var.vpc_name}."
    }
  }
}
```

---

## 8. Best Practices

### ✅ DO

- **Variable validation** 으로 사용자 입력 조기 검증
- **Precondition** 으로 종속성 확인
- **Postcondition** 으로 결과 검증
- **Check** 으로 지속적 모니터링
- Error message 는 명확히

### ❌ DON'T

- 너무 많은 validation (성능 저하)
- Runtime 에만 알 수 있는 것을 precondition 에
- Check block 에 apply 를 막는 로직

---

## 9. 시험 자주 나오는 함정

### 함정 1: Precondition 은 apply 중단?

```
Q: Precondition 실패 시 어떻게 되나요?
A: Apply 중단. Error 발생.
```

### 함정 2: Check Block 실패는?

```
Q: Check Block 실패 시 apply 진행?
A: ✅ YES. 경고만 표시. Non-blocking.
```

### 함정 3: self 참조

```
Q: self 는 precondition 에도 쓸 수 있나요?
A: ❌ NO. Postcondition 만.
```

---

## 참고 자료

- [Custom Conditions](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)
- [Checks](https://developer.hashicorp.com/terraform/language/checks)
- 관련 문서: [Variables 상세](/archive/04-configuration/variables-outputs/), [Sensitive Data](/archive/07-lifecycle/sensitive-data/)
- 실습: [Lab 08: Custom Conditions](/archive/labs/lab-08-custom-conditions/readme/)
