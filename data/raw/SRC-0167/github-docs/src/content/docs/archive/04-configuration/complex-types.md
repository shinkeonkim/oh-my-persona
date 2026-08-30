---
title: "Complex Types (list, map, object, tuple, set) 심화"
description: "Legacy study material imported from 04-configuration/complex-types.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Terraform 의 모든 타입 시스템 이해
- Collection Types (list, set, map) 차이점
- Structural Types (object, tuple) 활용
- Optional attributes (Terraform 1.3+)
- Type Conversion 규칙
- 복잡한 데이터 모델 설계

---

## 1. Terraform Type System 개요

### 타입 분류

```
Terraform Types
├── Primitive Types
│   ├── string
│   ├── number
│   ├── bool
│   └── null
├── Collection Types (동일 element 타입)
│   ├── list(TYPE)
│   ├── set(TYPE)
│   └── map(TYPE)
└── Structural Types (다양한 element 타입)
    ├── object({...})
    └── tuple([...])
```

### `any` 및 dynamic

```hcl
variable "flexible" {
  type = any  # 타입 검증 우회
}
```

---

## 2. Primitive Types 복습

### string

```hcl
variable "name" {
  type    = string
  default = "web-server"
}

# 문자열 보간
locals {
  full_name = "${var.name}-${var.environment}"
}

# Heredoc
locals {
  script = <<-EOT
    #!/bin/bash
    echo "Hello, ${var.name}!"
  EOT
}
```

### number

```hcl
variable "port" {
  type    = number
  default = 8080
}

variable "price" {
  type    = number
  default = 19.99  # float 허용
}
```

### bool

```hcl
variable "enabled" {
  type    = bool
  default = true
}
```

### null

```hcl
locals {
  optional_value = var.provided ? var.value : null
}

# null 은 "값이 없음"을 명시적으로 표현
```

---

## 3. Collection Types

### 3.1 list(TYPE) - 순서있는 컬렉션

**정의:**
```hcl
variable "azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}
```

**특징:**
- 순서 유지
- 인덱스 접근 (`[0]`, `[1]`, ...)
- 중복 허용
- `count` 와 호환

**접근:**
```hcl
var.azs[0]                    # "us-east-1a"
var.azs[length(var.azs) - 1]  # 마지막 요소
element(var.azs, 0)           # "us-east-1a"
element(var.azs, 10)          # 순환 (0으로 wrap)
```

**활용:**
```hcl
resource "aws_subnet" "public" {
  count             = length(var.azs)
  availability_zone = var.azs[count.index]
}
```

### 3.2 set(TYPE) - 순서 없는 유니크 컬렉션

**정의:**
```hcl
variable "unique_ports" {
  type    = set(number)
  default = [80, 443, 8080]
}
```

**특징:**
- 순서 없음 (**인덱스 접근 불가**)
- 자동 중복 제거
- `for_each` 와 호환

**변환:**
```hcl
toset(["a", "b", "b", "a"])   # ["a", "b"] (중복 제거)
tolist(toset(["a", "b"]))     # ["a", "b"] (다시 list로)
```

**활용:**
```hcl
resource "aws_security_group_rule" "ingress" {
  for_each  = var.unique_ports
  from_port = each.value
  to_port   = each.value
  # ...
}
```

### 3.3 map(TYPE) - 키-값 쌍

**정의:**
```hcl
variable "tags" {
  type = map(string)
  default = {
    Environment = "prod"
    Team        = "DevOps"
  }
}
```

**특징:**
- 유니크 키 (문자열)
- 모든 값은 **동일 타입**
- 알파벳 순 자동 정렬

**접근:**
```hcl
var.tags["Environment"]                # "prod"
lookup(var.tags, "Environment", "dev")  # "prod" (기본값 fallback)
keys(var.tags)                          # ["Environment", "Team"]
values(var.tags)                        # ["prod", "DevOps"]
```

**활용:**
```hcl
resource "aws_instance" "example" {
  tags = merge(var.tags, {
    Name = "web-server"
  })
}
```

### 3.4 List vs Set vs Map 비교

| 특성 | list | set | map |
|------|------|-----|-----|
| 순서 | ✅ 유지 | ❌ 없음 | 알파벳 순 |
| 중복 | ✅ 허용 | ❌ 제거 | ❌ 키 유니크 |
| 인덱스 접근 | ✅ `[0]` | ❌ 불가 | ✅ `["key"]` |
| count 사용 | ✅ | ❌ | ❌ |
| for_each 사용 | ❌ (toset 필요) | ✅ | ✅ |
| 반복 안전성 | 낮음 | 높음 | 높음 |

---

## 4. Structural Types

### 4.1 object({...}) - 서로 다른 타입 속성

**정의:**
```hcl
variable "server" {
  type = object({
    name          = string
    instance_type = string
    disk_size     = number
    monitoring    = bool
    tags          = map(string)
  })

  default = {
    name          = "web-01"
    instance_type = "t3.micro"
    disk_size     = 20
    monitoring    = true
    tags = {
      Role = "web"
    }
  }
}
```

**접근:**
```hcl
var.server.name
var.server.tags["Role"]
var.server.instance_type
```

**활용:**
```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.server.instance_type
  monitoring    = var.server.monitoring

  root_block_device {
    volume_size = var.server.disk_size
  }

  tags = merge(var.server.tags, {
    Name = var.server.name
  })
}
```

### 4.2 tuple([...]) - 순서와 타입 고정 리스트

**정의:**
```hcl
variable "record" {
  type    = tuple([string, number, bool])
  default = ["web-01", 100, true]
}
```

**접근:**
```hcl
var.record[0]  # string
var.record[1]  # number
var.record[2]  # bool
```

**특징:**
- 각 인덱스마다 **다른 타입** 가능
- 길이 고정
- list 와 다름: `list([string, number])` 는 유효하지 않음

**활용 (드문 경우):**
```hcl
variable "cache_config" {
  type    = tuple([string, number])  # [type, size]
  default = ["redis", 4096]
}

# 대신 object 권장
variable "cache_config" {
  type = object({
    type = string
    size = number
  })
}
```

---

## 5. Optional Attributes (Terraform 1.3+)

### 기본 사용

```hcl
variable "server" {
  type = object({
    name          = string
    instance_type = optional(string, "t3.micro")
    monitoring    = optional(bool, false)
    tags          = optional(map(string), {})
  })
}
```

**default 없는 optional:**
```hcl
type = object({
  name        = string
  description = optional(string)  # null 이 default
})
```

### 실전 예제: 유연한 Module Input

```hcl
variable "instances" {
  type = list(object({
    name          = string
    ami           = optional(string, "ami-default")
    instance_type = optional(string, "t3.micro")
    subnet_id     = string
    tags          = optional(map(string), {})
  }))
}
```

**사용:**
```hcl
instances = [
  {
    name      = "web-01"
    subnet_id = "subnet-1234"
    # ami, instance_type, tags 는 default 사용
  },
  {
    name          = "app-01"
    ami           = "ami-custom"
    instance_type = "t3.large"
    subnet_id     = "subnet-5678"
    tags = {
      Role = "app"
    }
  }
]
```

---

## 6. 중첩 (Nested) 타입

### 6.1 List of Objects

```hcl
variable "users" {
  type = list(object({
    name  = string
    email = string
    roles = list(string)
  }))

  default = [
    {
      name  = "alice"
      email = "alice@example.com"
      roles = ["admin", "developer"]
    },
    {
      name  = "bob"
      email = "bob@example.com"
      roles = ["viewer"]
    }
  ]
}
```

**활용:**
```hcl
resource "aws_iam_user" "users" {
  for_each = { for u in var.users : u.name => u }
  name     = each.value.name
}
```

### 6.2 Map of Objects

```hcl
variable "vpc_config" {
  type = map(object({
    cidr = string
    azs  = list(string)
  }))

  default = {
    prod = {
      cidr = "10.0.0.0/16"
      azs  = ["us-east-1a", "us-east-1b"]
    }
    dev = {
      cidr = "10.1.0.0/16"
      azs  = ["us-east-1a"]
    }
  }
}
```

**활용:**
```hcl
resource "aws_vpc" "environments" {
  for_each   = var.vpc_config
  cidr_block = each.value.cidr

  tags = {
    Name = each.key
  }
}
```

### 6.3 복잡한 중첩

```hcl
variable "network_config" {
  type = object({
    vpc_cidr = string
    subnets = map(object({
      cidr              = string
      availability_zone = string
      is_public         = bool
      routing_rules = list(object({
        cidr_block     = string
        gateway_id     = optional(string)
        nat_gateway_id = optional(string)
      }))
    }))
  })
}
```

---

## 7. Type Constraints

### 명시적 vs 암묵적

```hcl
# 명시적 (권장)
variable "count" {
  type    = number
  default = 3
}

# 암묵적 (default 로부터 추론)
variable "count" {
  default = 3  # 자동으로 number 로 추론
}
```

### 왜 명시해야 하나?

1. **에러 조기 발견** - 잘못된 타입 즉시 검출
2. **문서화** - 사용자에게 예상 타입 안내
3. **자동 변환 회피** - 예상치 못한 변환 방지

### 여러 타입 허용

```hcl
variable "flexible" {
  type = any  # 모든 타입 (지양)
}
```

---

## 8. Type Conversion

### 8.1 자동 변환

Terraform 은 필요 시 **자동 변환**을 시도합니다:

```hcl
tostring(42)          # "42"
tonumber("42")        # 42
tobool("true")        # true
tobool("1")           # 에러 (오직 "true"/"false")
```

### 8.2 명시적 변환

```hcl
tolist(toset(["a", "b", "b"]))    # ["a", "b"] (set → list)
tomap({a=1, b=2})                 # map(number)
toset(["a", "b", "a"])            # ["a", "b"]
tostring(number_value)
tonumber(string_value)
tobool(string_value)
```

### 8.3 List ↔ Set

```hcl
locals {
  raw_list = ["a", "b", "a", "c"]
  unique_set = toset(local.raw_list)   # {"a", "b", "c"}
  back_to_list = tolist(local.unique_set)  # ["a", "b", "c"] (정렬됨)
}
```

### 8.4 Object ↔ Map

```hcl
# object → map (동일 타입 값이어야)
variable "config" {
  type = object({
    a = string
    b = string
  })
}

locals {
  as_map = tomap(var.config)  # map(string)
}
```

---

## 9. for expressions

### 9.1 List Comprehension

```hcl
locals {
  upper_names = [for name in var.names : upper(name)]
}
```

### 9.2 Map Comprehension

```hcl
locals {
  name_to_id = { for user in var.users : user.name => user.id }
}
```

### 9.3 Filtering

```hcl
locals {
  active_users = [for u in var.users : u.name if u.active]
  admins = { for u in var.users : u.name => u if contains(u.roles, "admin") }
}
```

### 9.4 실전 패턴

**Object list → Map (for_each 준비):**
```hcl
locals {
  instances_by_name = { for i in var.instances : i.name => i }
}

resource "aws_instance" "example" {
  for_each      = local.instances_by_name
  ami           = each.value.ami
  instance_type = each.value.instance_type
}
```

**Flatten nested:**
```hcl
locals {
  all_rules = flatten([
    for sg_name, sg in var.security_groups : [
      for rule in sg.ingress_rules : {
        sg_name = sg_name
        port    = rule.port
        cidr    = rule.cidr
      }
    ]
  ])
}
```

---

## 10. Dynamic Blocks with Complex Types

```hcl
variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
    description = optional(string)
  }))

  default = [
    { from_port = 80, to_port = 80, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] },
    { from_port = 443, to_port = 443, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
  ]
}

resource "aws_security_group" "web" {
  name = "web-sg"

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
}
```

---

## 11. Validation with Complex Types

```hcl
variable "database_config" {
  type = object({
    engine         = string
    engine_version = string
    instance_class = string
    allocated_storage = number
    multi_az       = bool
  })

  validation {
    condition = contains(["mysql", "postgres", "mariadb"], var.database_config.engine)
    error_message = "Engine must be mysql, postgres, or mariadb."
  }

  validation {
    condition = var.database_config.allocated_storage >= 20
    error_message = "Storage must be at least 20 GB."
  }

  validation {
    condition = var.database_config.multi_az == true || !startswith(var.database_config.instance_class, "db.r")
    error_message = "R-family instances require multi_az = true."
  }
}
```

---

## 12. Best Practices

### ✅ DO

- **명시적 타입 사용** (any 지양)
- **object 로 관련 속성 그룹화**
- **for_each 는 set/map 사용** (list 대신 toset)
- **Optional attributes 활용** (Terraform 1.3+)
- **복잡한 구조 위에는 주석** 추가
- **Validation 으로 데이터 무결성 보장**

### ❌ DON'T

- `type = any` 남용
- 너무 깊은 중첩 (3단계 이상)
- tuple 을 object 대신 사용 (가독성 저해)
- list 를 for_each 에 직접 사용 (안전하지 않음)

---

## 13. 시험 자주 나오는 함정

### 함정 1: for_each vs count

```
Q: for_each 에 list 를 직접 넘길 수 있나요?
A: ❌ NO. set 또는 map 만 허용. toset() 필요.

for_each = toset(var.list_of_strings)  # OK
for_each = var.map_of_objects           # OK
for_each = var.list_of_strings          # ERROR
```

### 함정 2: List 접근 순서

```
Q: set 에 인덱스 접근 가능한가요?
A: ❌ NO. set 은 순서 없음. tolist() 로 변환 필요.

set = toset(["a", "b", "c"])
set[0]                # ERROR
tolist(set)[0]        # "a"
```

### 함정 3: object 는 immutable

```
Q: object 의 특정 속성만 변경 가능한가요?
A: ❌ NO. 전체 object 를 새로 만들거나 merge() 사용.

merge(var.config, { new_field = "value" })
```

### 함정 4: null 처리

```
Q: null 은 어떻게 처리해야 하나요?
A: coalesce() 또는 try() 사용.

coalesce(var.optional, "default")
try(var.might_not_exist, "default")
```

---

## 참고 자료

- [Type Constraints](https://developer.hashicorp.com/terraform/language/expressions/type-constraints)
- [Collection Types](https://developer.hashicorp.com/terraform/language/expressions/types#collection-types)
- [Structural Types](https://developer.hashicorp.com/terraform/language/expressions/type-constraints#structural-types)
- [Optional Object Attributes](https://developer.hashicorp.com/terraform/language/expressions/type-constraints#optional-object-type-attributes)
- 관련 문서: [Variables 상세](/archive/04-configuration/variables-outputs/), [Functions 상세](/archive/04-configuration/functions/)
