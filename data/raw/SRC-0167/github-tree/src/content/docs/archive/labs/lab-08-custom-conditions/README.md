---
title: "Lab 08: Custom Conditions (004 신규)"
description: "Legacy study material imported from labs/lab-08-custom-conditions/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🔴 Advanced
**소요 시간:** 90분
**시험 도메인:** Terraform Configuration (26%)

### 학습 목표

- ✅ Variable Validation 작성
- ✅ Preconditions (생성 전 검증)
- ✅ Postconditions (생성 후 검증)
- ✅ Check Blocks (지속적 헬스체크)
- ✅ Cross-Variable Validation (Terraform 1.9+)

---

## 📖 시나리오 1: Variable Validation

**variables.tf:**
```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  type = string

  validation {
    condition     = can(regex("^t[2-3]\\.", var.instance_type))
    error_message = "Must be t2 or t3 family."
  }

  validation {
    condition     = !(var.environment == "prod" && endswith(var.instance_type, ".micro"))
    error_message = "Prod cannot use micro instances."
  }
}

variable "cidr_block" {
  type = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be valid CIDR."
  }
}
```

**테스트:**
```bash
terraform plan -var="environment=invalid"
# Error: Environment must be dev, staging, or prod.

terraform plan -var="environment=prod" -var="instance_type=t3.micro"
# Error: Prod cannot use micro instances.
```

---

## 📖 시나리오 2: Precondition

**main.tf:**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/*"]
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  lifecycle {
    precondition {
      condition     = data.aws_ami.ubuntu.architecture == "x86_64"
      error_message = "AMI must be x86_64."
    }

    precondition {
      condition     = data.aws_ami.ubuntu.root_device_type == "ebs"
      error_message = "AMI must use EBS root."
    }

    precondition {
      condition     = var.environment != "prod" || var.multi_az
      error_message = "Prod requires multi_az = true."
    }
  }
}
```

---

## 📖 시나리오 3: Postcondition

**main.tf:**
```hcl
resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  associate_public_ip_address = true

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

resource "aws_lb" "web" {
  # ...

  lifecycle {
    postcondition {
      condition     = self.dns_name != ""
      error_message = "LB must have DNS name."
    }
  }
}
```

---

## 📖 시나리오 4: Check Block

**main.tf:**
```hcl
resource "aws_lb" "web" {
  name               = "web-lb"
  internal           = false
  load_balancer_type = "application"
  # ...
}

check "web_health" {
  data "http" "web_check" {
    url = "http://${aws_lb.web.dns_name}/health"

    request_headers = {
      Accept = "application/json"
    }
  }

  assert {
    condition     = data.http.web_check.status_code == 200
    error_message = "Web health check failed. Status: ${data.http.web_check.status_code}"
  }
}

check "s3_encryption" {
  assert {
    condition = aws_s3_bucket_server_side_encryption_configuration.data.rule[0].apply_server_side_encryption_by_default[0].sse_algorithm == "AES256"
    error_message = "S3 bucket must use AES256 encryption."
  }
}
```

**실행:**
```bash
terraform apply

# Check 실패 시:
# Warning: Check block assertion failed
# 
# on main.tf line 45:
#   45:   assert {
# 
# Web health check failed. Status: 503
# 
# (Apply 는 계속 진행됨)
```

---

## 📖 시나리오 5: Cross-Variable Validation (1.9+)

**variables.tf:**
```hcl
variable "min_size" {
  type = number

  validation {
    condition     = var.min_size >= 1
    error_message = "min_size must be >= 1."
  }
}

variable "max_size" {
  type = number

  validation {
    condition     = var.max_size >= var.min_size
    error_message = "max_size must be >= min_size."
  }
}

variable "desired_capacity" {
  type = number

  validation {
    condition     = var.desired_capacity >= var.min_size && var.desired_capacity <= var.max_size
    error_message = "desired must be between min and max."
  }
}
```

---

## ✅ 검증

```bash
terraform validate
terraform plan
terraform apply
```

---

## 🎯 핵심 요약

| 종류 | 도입 | 실패 시 |
|------|------|---------|
| Variable Validation | 0.13+ | Apply 중단 |
| Precondition | 1.2+ | Apply 중단 |
| Postcondition | 1.2+ | Apply 중단 |
| Check Block | 1.5+ | 경고만 |

---

## 📚 시험 관련

- Check block 은 **non-blocking** (경고만)
- Precondition/Postcondition 은 **blocking** (apply 중단)
- `self` 는 postcondition 만
- Cross-variable validation 은 1.9+

---

## 참고

- [Custom Conditions](/archive/07-lifecycle/custom-conditions/)
- [Sensitive Data](/archive/07-lifecycle/sensitive-data/)
