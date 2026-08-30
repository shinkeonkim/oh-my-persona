---
title: "Week 7: Lifecycle & Custom Conditions (004 강화)"
description: "Legacy study material imported from 07-lifecycle/README.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Lifecycle Meta-Arguments 완벽 이해
- depends_on을 통한 명시적 종속성 관리
- create_before_destroy로 무중단 배포
- Custom Conditions (004 신규 기능)
- Ephemeral Values 및 Sensitive Data 관리

---

## 1. Lifecycle Meta-Arguments

### 개요

**Lifecycle 블록**은 리소스의 생명주기 동작을 제어합니다.

```hcl
resource "aws_instance" "example" {
  # ... 리소스 구성 ...

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
    ignore_changes        = []
    replace_triggered_by  = []
  }
}
```

---

## 2. create_before_destroy

### 목적

리소스 재생성 시 **새 리소스를 먼저 생성**한 후 기존 리소스 삭제

### 기본 동작 (create_before_destroy = false)

```
1. 기존 리소스 삭제
2. 새 리소스 생성
```
→ **다운타임 발생!**

### create_before_destroy = true

```
1. 새 리소스 생성
2. 기존 리소스 삭제
```
→ **무중단 배포!**

### 예제

```hcl
resource "aws_launch_template" "example" {
  name_prefix   = "example-"
  image_id      = "ami-12345678"
  instance_type = "t2.micro"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "example" {
  launch_template {
    id      = aws_launch_template.example.id
    version = "$Latest"
  }

  min_size = 1
  max_size = 3

  lifecycle {
    create_before_destroy = true
  }
}
```

**시나리오:**
1. Launch Template의 AMI 변경
2. Terraform이 새 Launch Template 생성
3. ASG가 새 Template 사용
4. 기존 Launch Template 삭제

**결과:** 서비스 중단 없음!

### 제약사항

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "unique-bucket-name"

  lifecycle {
    create_before_destroy = true
  }
}
```
→ **주의:** Bucket 이름이 고유해야 하므로 충돌 가능

---

## 3. prevent_destroy

### 목적

중요한 리소스의 **실수로 인한 삭제 방지**

### 예제

```hcl
resource "aws_db_instance" "production" {
  identifier = "production-database"
  
  engine         = "postgres"
  instance_class = "db.t3.large"

  lifecycle {
    prevent_destroy = true
  }
}
```

**terraform destroy 실행 시:**
```
Error: Instance cannot be destroyed

  on main.tf line 5:
   5: resource "aws_db_instance" "production" {

Resource aws_db_instance.production has lifecycle.prevent_destroy set,
but the plan calls for this resource to be destroyed.
```

### 제거 방법

**1. prevent_destroy 제거:**
```hcl
lifecycle {
  prevent_destroy = false
}
```

**2. State에서 제거 후 수동 삭제:**
```bash
terraform state rm aws_db_instance.production

aws rds delete-db-instance --db-instance-identifier production-database
```

---

## 4. ignore_changes

### 목적

**특정 속성의 변경을 무시**

### 사용 사례

**Case 1: 외부에서 변경되는 속성**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name        = "Example"
    LastUpdated = timestamp()
  }

  lifecycle {
    ignore_changes = [
      tags["LastUpdated"]
    ]
  }
}
```

**Case 2: Auto Scaling으로 관리되는 속성**
```hcl
resource "aws_autoscaling_group" "example" {
  min_size         = 1
  max_size         = 10
  desired_capacity = 2

  lifecycle {
    ignore_changes = [
      desired_capacity
    ]
  }
}
```
→ Auto Scaling이 desired_capacity를 조정해도 Terraform이 되돌리지 않음

**Case 3: 모든 속성 무시**
```hcl
lifecycle {
  ignore_changes = all
}
```

### 예제: User Data

```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  user_data     = file("${path.module}/user-data.sh")

  lifecycle {
    ignore_changes = [
      user_data
    ]
  }
}
```
→ user_data 변경 시 인스턴스 재생성 방지

---

## 5. replace_triggered_by

### 목적 (Terraform 1.2+)

**다른 리소스가 변경될 때 자동으로 재생성**

### 예제

```hcl
resource "aws_ami_copy" "example" {
  name              = "example-ami"
  source_ami_id     = var.source_ami_id
  source_ami_region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = aws_ami_copy.example.id
  instance_type = "t2.micro"

  lifecycle {
    replace_triggered_by = [
      aws_ami_copy.example
    ]
  }
}
```
→ AMI가 변경되면 인스턴스 자동 재생성

---

## 6. depends_on (명시적 종속성)

### 암시적 vs 명시적 종속성

**암시적 (Implicit) - 권장:**
```hcl
resource "aws_subnet" "example" {
  vpc_id = aws_vpc.main.id
}
```
→ Terraform이 자동으로 VPC → Subnet 순서 파악

**명시적 (Explicit) - 필요시만:**
```hcl
resource "aws_iam_role_policy" "example" {
  role   = aws_iam_role.example.id
  policy = jsonencode({...})
}

resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  depends_on = [
    aws_iam_role_policy.example
  ]
}
```
→ IAM Policy가 먼저 생성되어야 하지만 직접 참조 불가

### depends_on 사용 시나리오

**Case 1: 순서가 중요하지만 참조할 속성이 없을 때**
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "example"
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket_policy" "example" {
  bucket = aws_s3_bucket.example.id
  policy = jsonencode({...})

  depends_on = [
    aws_s3_bucket_public_access_block.example
  ]
}
```

**Case 2: 숨겨진 종속성**
```hcl
resource "aws_iam_role" "example" {
  name = "example-role"
}

resource "aws_iam_role_policy_attachment" "example" {
  role       = aws_iam_role.example.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

resource "aws_instance" "example" {
  iam_instance_profile = aws_iam_role.example.name

  depends_on = [
    aws_iam_role_policy_attachment.example
  ]
}
```

**Case 3: Module 간 종속성**
```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "database" {
  source = "./modules/rds"
  
  vpc_id = module.vpc.vpc_id

  depends_on = [
    module.vpc
  ]
}
```

---

## 7. Custom Conditions (004 신규 강화)

### Variable Validation

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string

  validation {
    condition     = can(regex("^t[2-3]\\.(nano|micro|small|medium|large)$", var.instance_type))
    error_message = "Instance type must be t2 or t3 family (nano to large)."
  }
}

variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "cidr_block" {
  type = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid IPv4 CIDR block."
  }
}

variable "ami_id" {
  type = string

  validation {
    condition     = can(regex("^ami-[a-f0-9]{8,17}$", var.ami_id))
    error_message = "AMI ID must start with 'ami-' followed by 8-17 hexadecimal characters."
  }
}
```

### Preconditions (Terraform 1.2+)

**리소스 생성 전 조건 검증**

```hcl
resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = var.instance_type

  lifecycle {
    precondition {
      condition     = data.aws_ami.example.architecture == "x86_64"
      error_message = "AMI must be x86_64 architecture."
    }

    precondition {
      condition     = data.aws_ami.example.root_device_type == "ebs"
      error_message = "AMI must use EBS root device."
    }
  }
}

data "aws_ami" "example" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "image-id"
    values = [var.ami_id]
  }
}
```

### Postconditions (Terraform 1.2+)

**리소스 생성 후 조건 검증**

```hcl
resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"

  lifecycle {
    postcondition {
      condition     = self.instance_state == "running"
      error_message = "Instance must be in running state."
    }

    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have a public IP."
    }
  }
}
```

### Check Blocks (Terraform 1.5+)

**인프라 헬스체크**

```hcl
check "health_check" {
  data "http" "example" {
    url = "https://${aws_instance.web.public_ip}/health"
  }

  assert {
    condition     = data.http.example.status_code == 200
    error_message = "Health check failed."
  }
}

check "database_connection" {
  data "external" "db_check" {
    program = ["python3", "${path.module}/scripts/check_db.py"]
    
    query = {
      host = aws_db_instance.example.endpoint
    }
  }

  assert {
    condition     = data.external.db_check.result.status == "ok"
    error_message = "Database connection check failed."
  }
}
```

---

## 8. Ephemeral Values (004 신규)

### sensitive 플래그

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "example" {
  password = var.db_password
}

output "db_endpoint" {
  value     = aws_db_instance.example.endpoint
  sensitive = false
}

output "db_password" {
  value     = var.db_password
  sensitive = true
}
```

**CLI 출력:**
```
db_endpoint = "mydb.abc123.us-east-1.rds.amazonaws.com:5432"
db_password = <sensitive>
```

**주의:**
- `sensitive = true`는 **CLI 출력만** 숨김
- State 파일에는 **평문 저장**
- Remote Backend + 암호화 필수!

### Write-Only Arguments (004)

```hcl
resource "aws_db_instance" "example" {
  identifier = "mydb"
  
  password = var.db_password
}
```
→ `password`는 State에 저장 안 됨 (API 제한)

---

## 9. 실전 시나리오

### 시나리오 1: 무중단 배포

```hcl
resource "aws_launch_template" "web" {
  name_prefix   = "web-"
  image_id      = var.ami_id
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "web" {
  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  min_size         = 2
  max_size         = 10
  desired_capacity = 2

  lifecycle {
    create_before_destroy = true
  }
}
```

### 시나리오 2: 프로덕션 DB 보호

```hcl
resource "aws_db_instance" "prod" {
  identifier     = "production-db"
  engine         = "postgres"
  instance_class = "db.t3.large"

  lifecycle {
    prevent_destroy = true
    
    ignore_changes = [
      password
    ]
  }
}
```

### 시나리오 3: Validation

```hcl
variable "environment" {
  type = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Invalid environment."
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.environment == "prod" ? "t3.large" : "t2.micro"

  lifecycle {
    precondition {
      condition     = data.aws_ami.ubuntu.architecture == "x86_64"
      error_message = "AMI must be x86_64."
    }

    postcondition {
      condition     = self.instance_state == "running"
      error_message = "Instance not running."
    }
  }

  tags = {
    Environment = var.environment
  }
}
```

---

## 10. 핵심 요약

### Lifecycle Meta-Arguments

| Meta-Argument | 목적 | 사용 사례 |
|---------------|------|-----------|
| `create_before_destroy` | 무중단 배포 | ASG, Launch Template |
| `prevent_destroy` | 삭제 방지 | 프로덕션 DB, S3 |
| `ignore_changes` | 변경 무시 | Auto Scaling, 외부 변경 |
| `replace_triggered_by` | 트리거 재생성 | AMI 변경 시 |
| `depends_on` | 명시적 종속성 | 숨겨진 의존성 |

### Custom Conditions (004)

- ✅ **Variable Validation**: 입력 검증
- ✅ **Preconditions**: 생성 전 검증
- ✅ **Postconditions**: 생성 후 검증
- ✅ **Check Blocks**: 헬스체크

### Best Practices

- ✅ 암시적 종속성 우선
- ✅ create_before_destroy로 무중단 배포
- ✅ prevent_destroy로 중요 리소스 보호
- ✅ Validation으로 에러 조기 발견
- ✅ sensitive 플래그 + Remote Backend 암호화

---

## 참고 자료

- [Lifecycle Meta-Arguments](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [depends_on](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
- [Custom Conditions](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)
- [Checks](https://developer.hashicorp.com/terraform/language/checks)
