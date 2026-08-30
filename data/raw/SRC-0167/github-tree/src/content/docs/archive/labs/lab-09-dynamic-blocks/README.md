---
title: "Lab 09: Dynamic Blocks"
description: "Legacy study material imported from labs/lab-09-dynamic-blocks/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟡 Intermediate
**소요 시간:** 75분
**시험 도메인:** Terraform Configuration (26%)

### 학습 목표

- ✅ Dynamic Blocks 문법 이해
- ✅ Complex Types 와 조합
- ✅ Security Group 규칙 동적 생성
- ✅ 중첩 dynamic blocks

---

## 📖 시나리오 1: Security Group Dynamic Ingress

**variables.tf:**
```hcl
variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
    description = optional(string, "")
  }))

  default = [
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTP"
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "SSH from internal"
    }
  ]
}
```

**main.tf:**
```hcl
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Web server security group"
  vpc_id      = data.aws_vpc.default.id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

---

## 📖 시나리오 2: IAM Policy Statements

**main.tf:**
```hcl
variable "policy_statements" {
  type = list(object({
    effect    = string
    actions   = list(string)
    resources = list(string)
  }))

  default = [
    {
      effect    = "Allow"
      actions   = ["s3:GetObject", "s3:ListBucket"]
      resources = ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"]
    },
    {
      effect    = "Allow"
      actions   = ["dynamodb:GetItem", "dynamodb:PutItem"]
      resources = ["arn:aws:dynamodb:us-east-1:*:table/MyTable"]
    }
  ]
}

data "aws_iam_policy_document" "app" {
  dynamic "statement" {
    for_each = var.policy_statements
    content {
      effect    = statement.value.effect
      actions   = statement.value.actions
      resources = statement.value.resources
    }
  }
}

resource "aws_iam_policy" "app" {
  name   = "app-policy"
  policy = data.aws_iam_policy_document.app.json
}
```

---

## 📖 시나리오 3: ASG Dynamic Tags

**main.tf:**
```hcl
variable "asg_tags" {
  type = map(string)

  default = {
    Environment = "prod"
    Team        = "DevOps"
    CostCenter  = "Engineering"
    ManagedBy   = "Terraform"
  }
}

resource "aws_autoscaling_group" "web" {
  min_size         = 2
  max_size         = 10
  desired_capacity = 3

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  vpc_zone_identifier = data.aws_subnets.default.ids

  dynamic "tag" {
    for_each = var.asg_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}
```

---

## 📖 시나리오 4: 중첩 Dynamic Blocks (S3 Lifecycle)

**main.tf:**
```hcl
variable "lifecycle_rules" {
  type = list(object({
    id      = string
    enabled = bool
    prefix  = optional(string, "")
    transitions = list(object({
      days          = number
      storage_class = string
    }))
    expiration_days = optional(number)
  }))

  default = [
    {
      id      = "logs"
      enabled = true
      prefix  = "logs/"
      transitions = [
        { days = 30, storage_class = "STANDARD_IA" },
        { days = 90, storage_class = "GLACIER" }
      ]
      expiration_days = 365
    }
  ]
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket-example"
}

resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.enabled ? "Enabled" : "Disabled"

      dynamic "filter" {
        for_each = rule.value.prefix != "" ? [1] : []
        content {
          prefix = rule.value.prefix
        }
      }

      dynamic "transition" {
        for_each = rule.value.transitions
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }

      dynamic "expiration" {
        for_each = rule.value.expiration_days != null ? [1] : []
        content {
          days = rule.value.expiration_days
        }
      }
    }
  }
}
```

---

## ✅ 검증

```bash
terraform plan
terraform apply
```

---

## 🎯 핵심 문법

### Dynamic Block

```hcl
resource "..." "..." {
  dynamic "<BLOCK_NAME>" {
    for_each = <LIST_OR_MAP>
    content {
      # 각 반복마다 생성될 block 내용
    }
  }
}
```

### 반복 값 참조

- `<BLOCK_NAME>.key` - 반복 키 (map 인 경우)
- `<BLOCK_NAME>.value` - 반복 값

### 조건부 Block

```hcl
dynamic "encryption" {
  for_each = var.enable_encryption ? [1] : []
  content { ... }
}
```

---

## 📚 시험 관련

- Dynamic block 은 **for_each** 필수
- 중첩 가능 (dynamic 안에 dynamic)
- 조건부 생성: `[1] : []` 패턴
- 코드 반복 제거에 유용

---

## 참고

- [Complex Types](/archive/04-configuration/complex-types/)
- [Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
