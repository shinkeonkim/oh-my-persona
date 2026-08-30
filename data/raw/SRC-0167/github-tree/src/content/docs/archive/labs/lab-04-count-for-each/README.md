---
title: "Lab 04: count와 for_each"
description: "Legacy study material imported from labs/lab-04-count-for-each/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📋 개요

**난이도:** 🟡 Intermediate  
**소요 시간:** 60분  
**시험 도메인:** Terraform Configuration (26%)

### 학습 목표
- ✅ count 메타-인수 활용
- ✅ for_each로 안전한 리소스 관리
- ✅ 두 방식의 차이점 실전 이해
- ✅ 리소스 제거 시 동작 비교

### 실습 시나리오
count와 for_each를 각각 사용하여 여러 S3 Bucket을 생성하고, 중간 리소스 제거 시 동작 차이를 확인합니다.

---

## 📖 Part 1: count 사용

### count로 여러 Bucket 생성

**파일: `count-example.tf`**
```hcl
variable "bucket_names_count" {
  type    = list(string)
  default = ["bucket-a", "bucket-b", "bucket-c"]
}

resource "aws_s3_bucket" "count_example" {
  count  = length(var.bucket_names_count)
  bucket = "${var.bucket_names_count[count.index]}-count-${random_id.suffix.hex}"

  tags = {
    Name  = var.bucket_names_count[count.index]
    Index = count.index
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}
```

### count 참조 방법
```hcl
output "count_bucket_names" {
  value = aws_s3_bucket.count_example[*].id
}

output "count_first_bucket" {
  value = aws_s3_bucket.count_example[0].id
}

output "count_second_bucket" {
  value = aws_s3_bucket.count_example[1].id
}
```

### 실습 1: count로 배포
```bash
terraform init
terraform apply -auto-approve

terraform output count_bucket_names
```

**예상 출력:**
```
count_bucket_names = [
  "bucket-a-count-12ab34cd",
  "bucket-b-count-12ab34cd",
  "bucket-c-count-12ab34cd",
]
```

### 실습 2: 중간 항목 제거 (count의 문제점)

**count-example.tf 수정:**
```hcl
variable "bucket_names_count" {
  type    = list(string)
  default = ["bucket-a", "bucket-c"]
}
```

```bash
terraform plan
```

**예상 결과:**
```
aws_s3_bucket.count_example[1]: Destruction complete
aws_s3_bucket.count_example[2]: Forces replacement

Plan: 0 to add, 1 to change, 2 to destroy.
```

**⚠️ 문제점:**
- `bucket-b`를 제거했지만
- `bucket-c`가 **index 2 → index 1**로 변경
- Terraform이 `bucket-c`를 삭제하고 재생성!

---

## 📖 Part 2: for_each 사용

### for_each로 여러 Bucket 생성

**파일: `for-each-example.tf`**
```hcl
variable "bucket_names_foreach" {
  type = set(string)
  default = ["bucket-a", "bucket-b", "bucket-c"]
}

resource "aws_s3_bucket" "foreach_example" {
  for_each = var.bucket_names_foreach
  bucket   = "${each.key}-foreach-${random_id.suffix.hex}"

  tags = {
    Name = each.key
  }
}
```

### for_each 참조 방법
```hcl
output "foreach_bucket_names" {
  value = [for bucket in aws_s3_bucket.foreach_example : bucket.id]
}

output "foreach_bucket_a" {
  value = aws_s3_bucket.foreach_example["bucket-a"].id
}
```

### 실습 3: for_each로 배포
```bash
terraform apply -auto-approve

terraform output foreach_bucket_names
```

### 실습 4: 중간 항목 제거 (for_each의 안전성)

**for-each-example.tf 수정:**
```hcl
variable "bucket_names_foreach" {
  type = set(string)
  default = ["bucket-a", "bucket-c"]
}
```

```bash
terraform plan
```

**예상 결과:**
```
aws_s3_bucket.foreach_example["bucket-b"]: Destruction complete

Plan: 0 to add, 0 to change, 1 to destroy.
```

**✅ 장점:**
- `bucket-b`만 정확히 삭제
- `bucket-a`와 `bucket-c`는 **영향 없음**
- 안전한 리소스 관리!

---

## 📊 count vs for_each 비교

### 참조 방식

```hcl
aws_s3_bucket.count_example[0]
aws_s3_bucket.count_example[1]
aws_s3_bucket.count_example[2]

aws_s3_bucket.foreach_example["bucket-a"]
aws_s3_bucket.foreach_example["bucket-b"]
aws_s3_bucket.foreach_example["bucket-c"]
```

### 사용 시나리오

**count 사용 권장:**
- 동일한 리소스를 **정확한 개수**만큼 생성
- 항목 추가만 하고 제거/재배열 없음
- 순서가 중요하지 않음

```hcl
variable "instance_count" {
  default = 3
}

resource "aws_instance" "web" {
  count         = var.instance_count
  instance_type = "t2.micro"
}
```

**for_each 사용 권장:**
- 항목을 **이름으로 관리**
- 중간 항목 제거 가능성
- 각 인스턴스가 고유한 특성

```hcl
variable "instances" {
  type = map(object({
    instance_type = string
  }))
  default = {
    web = { instance_type = "t2.micro" }
    api = { instance_type = "t3.small" }
    db  = { instance_type = "t3.medium" }
  }
}

resource "aws_instance" "app" {
  for_each      = var.instances
  instance_type = each.value.instance_type
}
```

---

## 🎯 실전 예제

### for_each with map

```hcl
variable "environments" {
  type = map(object({
    instance_type = string
    disk_size     = number
  }))
  default = {
    dev = {
      instance_type = "t2.micro"
      disk_size     = 20
    }
    staging = {
      instance_type = "t3.small"
      disk_size     = 50
    }
    prod = {
      instance_type = "t3.large"
      disk_size     = 100
    }
  }
}

resource "aws_instance" "env" {
  for_each      = var.environments
  instance_type = each.value.instance_type

  root_block_device {
    volume_size = each.value.disk_size
  }

  tags = {
    Name        = "Server-${each.key}"
    Environment = each.key
  }
}
```

---

## ✅ 정리 및 Cleanup

```bash
terraform destroy -auto-approve
```

---

## 🎯 핵심 포인트

| 특성 | count | for_each |
|------|-------|----------|
| **입력 타입** | number | map or set |
| **참조** | `[index]` | `["key"]` |
| **중간 제거** | ⚠️ 재생성 위험 | ✅ 안전 |
| **용도** | 동일 리소스 N개 | 키 기반 관리 |
| **프로덕션** | 주의 필요 | 권장 |

**시험 팁:**
- count는 인덱스, for_each는 키
- 중간 제거 시나리오 → for_each 선택
- "안전한 관리" → for_each

---

**완성된 솔루션은 `solution/` 폴더를 참고하세요.**
