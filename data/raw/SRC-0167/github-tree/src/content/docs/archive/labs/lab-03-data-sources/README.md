---
title: "Lab 03: Data Sources 활용"
description: "Legacy study material imported from labs/lab-03-data-sources/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟢 Beginner  
**소요 시간:** 45분  
**시험 도메인:** Terraform Configuration (26%)

### 학습 목표
- ✅ Resource vs Data Source 차이 이해
- ✅ 기존 인프라 참조
- ✅ 최신 AMI 동적 조회
- ✅ Cross-resource references

### 실습 시나리오
Data Source를 사용하여 최신 Ubuntu AMI를 조회하고, 기존 VPC를 참조하여 EC2 인스턴스를 생성합니다.

---

## 📖 단계별 실습

### Step 1: Data Source로 최신 AMI 조회

**파일: `data.tf`**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
```

### Step 2: Data Source 참조

**파일: `main.tf`**
```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"

  tags = {
    Name = "Web Server"
    AMI  = data.aws_ami.ubuntu.name
  }
}
```

### Step 3: Outputs

**파일: `outputs.tf`**
```hcl
output "ami_id" {
  value = data.aws_ami.ubuntu.id
}

output "ami_name" {
  value = data.aws_ami.ubuntu.name
}

output "instance_id" {
  value = aws_instance.web.id
}
```

---

## ✅ 검증

```bash
terraform init
terraform plan
terraform apply -auto-approve

terraform output ami_id
terraform output ami_name

aws ec2 describe-instances \
  --instance-ids $(terraform output -raw instance_id)

terraform destroy -auto-approve
```

---

## 🎯 핵심 개념

### Resource vs Data Source

| Resource | Data Source |
|----------|-------------|
| `resource "type" "name"` | `data "type" "name"` |
| 인프라 **생성/관리** | 기존 인프라 **조회** |
| State에 저장됨 | State에 저장 안 됨 |
| Apply 시 변경 가능 | 읽기 전용 |

### 자주 사용하는 Data Sources

```hcl
data "aws_availability_zones" "available" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "selected" {
  vpc_id = data.aws_vpc.default.id
  filter {
    name   = "availability-zone"
    values = ["us-east-1a"]
  }
}
```

---

**완성된 솔루션은 `solution/` 폴더를 참고하세요.**
