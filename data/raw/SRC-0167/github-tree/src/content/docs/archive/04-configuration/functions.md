---
title: "Terraform Built-in Functions 완전 가이드"
description: "Legacy study material imported from 04-configuration/functions.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- 모든 카테고리의 Built-in Functions 이해
- 실전에서 자주 사용하는 함수 활용
- 함수 조합 패턴 익히기
- 시험 자주 나오는 함수 마스터
- terraform console 로 함수 테스트

---

## 1. Functions 개요

Terraform 은 다양한 **Built-in Functions** 를 제공하지만 **사용자 정의 함수는 지원하지 않습니다**.

### 함수 호출 문법

```hcl
<FUNCTION_NAME>(<ARG1>, <ARG2>, ...)
```

### terraform console 로 테스트

```bash
terraform console
> length(["a", "b", "c"])
3

> upper("hello")
"HELLO"

> merge({a=1}, {b=2})
{
  "a" = 1
  "b" = 2
}
```

---

## 2. Numeric Functions (숫자)

| 함수 | 목적 | 예제 |
|------|------|------|
| `abs()` | 절대값 | `abs(-42) → 42` |
| `ceil()` | 올림 | `ceil(5.1) → 6` |
| `floor()` | 내림 | `floor(5.9) → 5` |
| `max()` | 최대값 | `max(12, 54, 3) → 54` |
| `min()` | 최소값 | `min(12, 54, 3) → 3` |
| `pow()` | 거듭제곱 | `pow(2, 8) → 256` |
| `log()` | 로그 | `log(100, 10) → 2` |
| `signum()` | 부호 (-1, 0, 1) | `signum(-3) → -1` |
| `parseint()` | 문자열 → 정수 | `parseint("100", 10) → 100` |

### 예제

```hcl
locals {
  instance_count = max(var.min_count, ceil(var.load / 100))
  # 최소 min_count, load 100당 1대씩 올림
}
```

---

## 3. String Functions (문자열)

### 3.1 대소문자 변환

```hcl
lower("HELLO WORLD")    # "hello world"
upper("hello world")    # "HELLO WORLD"
title("hello world")    # "Hello World"
```

### 3.2 트리밍

```hcl
chomp("hello\n")             # "hello" (마지막 줄바꿈만 제거)
trim(" hello ", " ")         # "hello"
trimspace("  hello  ")       # "hello"
trimprefix("app-server", "app-")   # "server"
trimsuffix("server.log", ".log")   # "server"
```

### 3.3 분할/결합

```hcl
split("-", "a-b-c-d")             # ["a", "b", "c", "d"]
join("-", ["a", "b", "c"])        # "a-b-c"
join(",", ["10.0.1.0/24", "10.0.2.0/24"])   # "10.0.1.0/24,10.0.2.0/24"
```

### 3.4 검색/치환

```hcl
replace("hello world", "world", "terraform")   # "hello terraform"
substr("hello world", 6, 5)                    # "world"
strrev("hello")                                # "olleh"
```

### 3.5 정규식

```hcl
regex("[a-z]+", "hello 123")                   # "hello"
regexall("[0-9]+", "a1 b2 c3")                 # ["1", "2", "3"]
```

### 3.6 포맷팅

```hcl
format("Hello, %s!", "World")                     # "Hello, World!"
format("%03d", 5)                                 # "005"
formatlist("Server-%02d", [1, 2, 3])              # ["Server-01", "Server-02", "Server-03"]

# 여러 값
format("%s is %d years old", "Alice", 30)   # "Alice is 30 years old"
```

### 3.7 들여쓰기

```hcl
indent(2, "line1\nline2")  # 첫 줄 제외, 2 space 들여쓰기
```

---

## 4. Collection Functions (컬렉션)

### 4.1 길이/개수

```hcl
length(["a", "b", "c"])              # 3
length("hello")                       # 5
length({a=1, b=2})                    # 2
```

### 4.2 검색

```hcl
contains(["a", "b", "c"], "b")       # true
element(["a", "b", "c"], 1)          # "b"
index(["a", "b", "c"], "b")          # 1
lookup({a=1, b=2}, "a", 0)           # 1 (default: 0)
lookup({a=1, b=2}, "z", 0)           # 0
```

### 4.3 병합/결합

```hcl
concat([1, 2], [3, 4], [5])          # [1, 2, 3, 4, 5]
merge({a=1}, {b=2}, {a=3})           # {a=3, b=2}
```

### 4.4 변환

```hcl
keys({a=1, b=2, c=3})                # ["a", "b", "c"]
values({a=1, b=2, c=3})              # [1, 2, 3]
zipmap(["a", "b"], [1, 2])           # {a=1, b=2}
```

### 4.5 필터링

```hcl
compact(["a", "", "b", ""])          # ["a", "b"] (빈 문자열 제거)
distinct(["a", "b", "a", "c"])       # ["a", "b", "c"]
coalesce("", "b", "c")               # "b" (첫 non-null/empty)
coalescelist([], [1, 2], [3])        # [1, 2]
```

### 4.6 슬라이싱

```hcl
slice(["a", "b", "c", "d"], 1, 3)    # ["b", "c"] (start inclusive, end exclusive)
chunklist(["a", "b", "c", "d", "e"], 2)   # [["a", "b"], ["c", "d"], ["e"]]
```

### 4.7 정렬/역순

```hcl
sort(["c", "a", "b"])                # ["a", "b", "c"]
reverse([1, 2, 3])                   # [3, 2, 1]
```

### 4.8 집합 연산

```hcl
setintersection(["a", "b"], ["b", "c"])    # ["b"]
setunion(["a"], ["b", "c"])                # ["a", "b", "c"]
setsubtract(["a", "b", "c"], ["b"])        # ["a", "c"]
setproduct(["a", "b"], [1, 2])             # [["a", 1], ["a", 2], ["b", 1], ["b", 2]]
```

### 4.9 평탄화

```hcl
flatten([[1, 2], [3, 4], [5]])       # [1, 2, 3, 4, 5]
flatten([[[1], [2]], [3]])           # [1, 2, 3]
```

### 4.10 범위

```hcl
range(3)               # [0, 1, 2]
range(1, 4)            # [1, 2, 3]
range(1, 10, 2)        # [1, 3, 5, 7, 9]
```

### 4.11 논리 함수

```hcl
alltrue([true, true, true])       # true
alltrue([true, false, true])      # false
anytrue([false, false, true])     # true
```

### 4.12 sum

```hcl
sum([1, 2, 3, 4])    # 10
```

### 4.13 transpose

```hcl
transpose({"a"=["1","2"], "b"=["3","4"]})
# {"1"=["a"], "2"=["a"], "3"=["b"], "4"=["b"]}
```

### 4.14 one()

```hcl
one([])                # null
one(["a"])             # "a"
one(["a", "b"])        # 에러
```

---

## 5. Encoding Functions (인코딩)

### 5.1 Base64

```hcl
base64encode("hello")                          # "aGVsbG8="
base64decode("aGVsbG8=")                       # "hello"
base64gzip("large string...")                  # gzip + base64
```

### 5.2 JSON

```hcl
jsonencode({name="app", port=80})              # '{"name":"app","port":80}'
jsondecode("{\"name\":\"app\"}")               # {name="app"}
```

### 5.3 YAML

```hcl
yamlencode({name="app"})                       # "name: app\n"
yamldecode("name: app")                        # {name="app"}
```

### 5.4 URL

```hcl
urlencode("hello world")                       # "hello+world"
```

### 5.5 CSV

```hcl
csvdecode("a,b\n1,2\n3,4")
# [{"a"="1","b"="2"}, {"a"="3","b"="4"}]
```

---

## 6. Filesystem Functions (파일 시스템)

### 6.1 파일 읽기

```hcl
file("${path.module}/user-data.sh")            # 파일 내용 문자열
filebase64("logo.png")                         # base64 인코딩
```

### 6.2 파일 존재 확인

```hcl
fileexists("${path.module}/config.json")       # true / false
```

### 6.3 여러 파일

```hcl
fileset("${path.module}", "*.tf")              # 매칭 파일 목록
fileset(".", "modules/*/*.tf")                 # 재귀 패턴
```

### 6.4 경로 함수

```hcl
abspath(path.root)                             # 절대 경로
dirname("/foo/bar/baz.txt")                    # "/foo/bar"
basename("/foo/bar/baz.txt")                   # "baz.txt"
pathexpand("~/config")                         # "/home/user/config"
```

### 6.5 Template 파일

```hcl
templatefile("${path.module}/user-data.tpl", {
  region = var.region
  hostname = var.hostname
})
```

**user-data.tpl:**
```
#!/bin/bash
HOSTNAME=${hostname}
REGION=${region}
```

### 6.6 Path References

| 참조 | 의미 |
|------|------|
| `path.module` | 현재 모듈 디렉토리 |
| `path.root` | Root 모듈 디렉토리 |
| `path.cwd` | 현재 작업 디렉토리 |
| `terraform.workspace` | 현재 workspace 이름 |

---

## 7. Date & Time Functions (날짜/시간)

```hcl
timestamp()                                    # "2026-07-21T10:00:00Z"
formatdate("YYYY-MM-DD", timestamp())          # "2026-07-21"
timeadd(timestamp(), "24h")                    # 24시간 후
timeadd("2026-01-01T00:00:00Z", "168h")        # 1주일 후
```

### 예제: 만료 시간

```hcl
resource "aws_iam_role" "example" {
  tags = {
    CreatedAt = timestamp()
    ExpiresAt = timeadd(timestamp(), "720h")   # 30일 후
  }
}
```

---

## 8. Hash & Crypto Functions

### 8.1 Hash

```hcl
md5("hello")               # "5d41402abc4b2a76b9719d911017c592"
sha1("hello")              # "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
sha256("hello")            # 64자 hex
sha512("hello")            # 128자 hex

base64sha256("hello")      # base64 인코딩된 sha256
```

### 8.2 File Hash

```hcl
filemd5("script.sh")
filesha256("archive.zip")
filebase64sha256("archive.zip")
```

### 8.3 UUID

```hcl
uuid()                              # "b4d1e15c-..." (매번 다름)
uuidv5("dns", "example.com")        # 결정적 UUID
```

### 8.4 Password/Encryption

```hcl
bcrypt("password", 10)              # bcrypt 해시
rsadecrypt(ciphertext, private_key) # RSA 복호화
```

⚠️ `bcrypt()`, `uuid()` 는 매번 다른 값 반환 → apply 마다 리소스 재생성 위험. `ignore_changes` 활용.

---

## 9. IP Network Functions

```hcl
cidrhost("10.0.0.0/24", 5)          # "10.0.0.5"
cidrhost("10.0.0.0/16", 256)        # "10.0.1.0"
cidrnetmask("10.0.0.0/24")          # "255.255.255.0"
cidrsubnet("10.0.0.0/16", 8, 2)     # "10.0.2.0/24" (8-bit 확장, index 2)
cidrsubnets("10.0.0.0/16", 8, 8, 8) # ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
```

### 실전: VPC Subnets

```hcl
locals {
  vpc_cidr = "10.0.0.0/16"
  subnets = cidrsubnets(local.vpc_cidr, 8, 8, 8, 8)
  # ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

resource "aws_subnet" "public" {
  count      = 4
  vpc_id     = aws_vpc.main.id
  cidr_block = local.subnets[count.index]
}
```

---

## 10. Type Conversion Functions

### 10.1 기본 변환

```hcl
tostring(42)                        # "42"
tonumber("42")                      # 42
tobool("true")                      # true
```

### 10.2 컬렉션 변환

```hcl
tolist(["a", "b", "b"])             # ["a", "b", "b"]
toset(["a", "b", "b"])              # ["a", "b"] (중복 제거)
tomap({a=1, b=2})                   # 명시적 map
```

### 10.3 안전한 실행

```hcl
try(var.might_fail, "default")      # 에러 시 default
can(regex("[a-z]+", "hello"))       # true (에러 없이 실행 가능)
can(tonumber("not a number"))       # false
```

### 10.4 Sensitive 조작

```hcl
sensitive(var.something)            # 강제 sensitive
nonsensitive(var.sensitive_value)   # sensitive 해제 (주의!)
```

### 10.5 type() 함수 (디버깅용)

```hcl
type(var.something)                 # 타입 문자열 반환
```

### 10.6 defaults()

```hcl
defaults(var.input, {
  name = "default-name"
  tags = {}
})
```

### 10.7 ephemeralasnull() (Terraform 1.10+)

```hcl
ephemeralasnull(var.ephemeral_value)   # ephemeral 값을 null 처리
```

---

## 11. 함수 조합 실전 패턴

### 11.1 병합된 태그

```hcl
locals {
  common_tags = {
    ManagedBy   = "Terraform"
    Environment = var.environment
  }
}

resource "aws_instance" "web" {
  tags = merge(local.common_tags, {
    Name = "web-server"
    Role = "frontend"
  })
}
```

### 11.2 조건부 리소트 리스트

```hcl
locals {
  all_subnets = concat(
    aws_subnet.public[*].id,
    aws_subnet.private[*].id
  )
}
```

### 11.3 파일에서 리스트 로드

```hcl
locals {
  ip_list = split("\n", trimspace(file("${path.module}/allowed-ips.txt")))
}

resource "aws_security_group" "example" {
  dynamic "ingress" {
    for_each = toset(local.ip_list)
    content {
      cidr_blocks = ["${ingress.value}/32"]
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
    }
  }
}
```

### 11.4 JSON 설정 파싱

```hcl
locals {
  config = jsondecode(file("${path.module}/config.json"))
}

resource "aws_instance" "web" {
  instance_type = local.config.instance_type
  ami           = local.config.ami_id
}
```

### 11.5 User Data Template

```hcl
resource "aws_instance" "web" {
  user_data = templatefile("${path.module}/init.sh.tpl", {
    hostname   = "web-${count.index}"
    packages   = ["nginx", "certbot"]
    env        = var.environment
  })
}
```

### 11.6 CIDR 자동 계산

```hcl
locals {
  az_count = length(data.aws_availability_zones.available.names)
  public_subnets = [for i in range(local.az_count) : cidrsubnet(var.vpc_cidr, 8, i)]
  private_subnets = [for i in range(local.az_count) : cidrsubnet(var.vpc_cidr, 8, i + 100)]
}
```

---

## 12. terraform console 활용

```bash
terraform console

# 함수 테스트
> length(var.availability_zones)
3

> merge({a=1}, {b=2})
{
  "a" = 1
  "b" = 2
}

> [for s in ["Alice", "Bob"] : upper(s)]
tolist([
  "ALICE",
  "BOB",
])

# 리소스 attribute 확인
> aws_instance.web.public_ip
"54.123.45.67"

# 종료: exit 또는 Ctrl+D
```

---

## 13. 시험 자주 나오는 함수 TOP 20

1. `length()` - 리스트/맵/문자열 길이
2. `contains()` - 포함 여부
3. `lookup()` - map 조회 with default
4. `merge()` - map 병합
5. `concat()` - list 결합
6. `flatten()` - 중첩 list 평탄화
7. `element()` - list index 접근
8. `keys()`, `values()` - map 조작
9. `toset()`, `tolist()`, `tomap()` - 타입 변환
10. `can()` - validation 에서 활용
11. `regex()` - 정규식 매칭
12. `format()` - 문자열 포맷팅
13. `file()` - 파일 읽기
14. `templatefile()` - 템플릿 처리
15. `jsonencode()`, `jsondecode()` - JSON 변환
16. `cidrsubnet()` - CIDR 계산
17. `try()` - 에러 처리
18. `coalesce()` - null 처리
19. `split()`, `join()` - 문자열/리스트 변환
20. `distinct()` - 중복 제거

---

## 14. Best Practices

### ✅ DO

- `terraform console` 로 함수 테스트
- 복잡한 로직은 `locals` 에 저장
- Type 변환은 명시적으로
- `try()` 로 안전하게 처리

### ❌ DON'T

- `uuid()`, `timestamp()` 를 리소스에 직접 사용 (ignore_changes 필요)
- 과도한 함수 중첩 (가독성 저해)
- 사용자 정의 함수 시도 (지원 안 됨)

---

## 참고 자료

- [Functions Overview](https://developer.hashicorp.com/terraform/language/functions)
- [Numeric Functions](https://developer.hashicorp.com/terraform/language/functions#numeric-functions)
- [String Functions](https://developer.hashicorp.com/terraform/language/functions#string-functions)
- [Collection Functions](https://developer.hashicorp.com/terraform/language/functions#collection-functions)
- [Terraform Console](https://developer.hashicorp.com/terraform/cli/commands/console)
- 관련 문서: [Variables 상세](/archive/04-configuration/variables-outputs/), [Complex Types](/archive/04-configuration/complex-types/)
