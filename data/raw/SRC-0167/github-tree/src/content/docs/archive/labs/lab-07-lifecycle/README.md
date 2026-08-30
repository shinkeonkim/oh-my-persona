---
title: "Lab 07: Lifecycle Meta-Arguments"
description: "Legacy study material imported from labs/lab-07-lifecycle/README.md"
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

- ✅ create_before_destroy 로 무중단 배포
- ✅ prevent_destroy 로 리소스 보호
- ✅ ignore_changes 로 외부 변경 무시
- ✅ replace_triggered_by 활용
- ✅ depends_on 명시적 종속성

---

## 📖 시나리오 1: create_before_destroy

### 목적: EC2 재생성 시 무중단

**main.tf:**
```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "web-server"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}
```

**변경 트리거:**
```bash
terraform apply

# AMI 변경 (새 AMI 발견 시)
terraform apply
# + 새 인스턴스 먼저 생성
# - 기존 인스턴스 나중 삭제
```

---

## 📖 시나리오 2: prevent_destroy

### 목적: 프로덕션 DB 삭제 방지

**main.tf:**
```hcl
resource "aws_db_instance" "prod" {
  identifier     = "prod-database"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  db_name        = "myapp"
  username       = "admin"
  password       = "TempPassword123!"
  skip_final_snapshot = true

  lifecycle {
    prevent_destroy = true
  }
}
```

**Destroy 시도:**
```bash
terraform destroy
# Error: Instance cannot be destroyed
# Resource aws_db_instance.prod has lifecycle.prevent_destroy set,
# but the plan calls for this resource to be destroyed.
```

**해결 (실제 삭제 시):**
```hcl
lifecycle {
  prevent_destroy = false
}
```

---

## 📖 시나리오 3: ignore_changes

### 목적: Auto Scaling desired_capacity 무시

**main.tf:**
```hcl
resource "aws_launch_template" "web" {
  name_prefix   = "web-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true
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

  lifecycle {
    ignore_changes = [
      desired_capacity  # Auto Scaling 이 조정 → Terraform 무시
    ]
  }
}
```

**검증:**
```bash
terraform apply
# desired_capacity = 3

# AWS 에서 스케일 아웃 (desired = 6)
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name web \
  --desired-capacity 6

terraform plan
# No changes  ← desired_capacity 무시!
```

---

## 📖 시나리오 4: replace_triggered_by

### 목적: AMI 변경 시 인스턴스 재생성

**main.tf:**
```hcl
resource "aws_ami_copy" "custom" {
  name              = "custom-ami-${formatdate("YYYYMMDD", timestamp())}"
  source_ami_id     = "ami-0abcdef1234567890"
  source_ami_region = "us-east-1"
}

resource "aws_instance" "app" {
  ami           = aws_ami_copy.custom.id
  instance_type = "t3.micro"

  lifecycle {
    replace_triggered_by = [
      aws_ami_copy.custom
    ]
  }
}
```

**AMI 변경 시:**
```
aws_ami_copy.custom 재생성
   ↓
aws_instance.app 자동 재생성
```

---

## 📖 시나리오 5: depends_on

### 목적: IAM Role Policy 순서 강제

**main.tf:**
```hcl
resource "aws_iam_role" "app" {
  name = "app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "app_s3" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_instance_profile" "app" {
  name = "app-profile"
  role = aws_iam_role.app.name
}

resource "aws_instance" "app" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.app.name

  depends_on = [
    aws_iam_role_policy_attachment.app_s3
  ]

  user_data = <<-EOF
    #!/bin/bash
    aws s3 ls  # Policy 필요
  EOF
}
```

**동작:**
- Policy 첨부 → Instance 생성 순서 보장

---

## ✅ 검증

각 시나리오마다:
```bash
terraform apply
terraform state show <resource>
```

---

## 🎯 핵심 개념 요약

| Meta-Argument | 사용 사례 |
|---------------|-----------|
| `create_before_destroy` | 무중단 배포 (ASG, LT) |
| `prevent_destroy` | 프로덕션 DB, S3 |
| `ignore_changes` | Auto Scaling, 외부 변경 |
| `replace_triggered_by` | 종속 리소스 재생성 |
| `depends_on` | 숨겨진 종속성 |

---

## 📚 시험 관련

- Lifecycle block 은 `resource` 블록 내부
- `ignore_changes = all` 은 위험 (거의 안 씀)
- `depends_on` 은 마지막 수단 (implicit 우선)
- `prevent_destroy = true` 시 config 수정 필요

---

## Cleanup

```bash
# prevent_destroy 를 false 로 변경 후
terraform destroy -auto-approve
```

---

## 참고

- [Lifecycle](/archive/07-lifecycle/readme/)
- [Custom Conditions](/archive/07-lifecycle/custom-conditions/)
