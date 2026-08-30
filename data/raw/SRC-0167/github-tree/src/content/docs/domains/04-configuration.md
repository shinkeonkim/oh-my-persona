---
title: 04. Terraform 구성 / Configuration
description: "Objectives 4a-4h: blocks, references, values, types, expressions, dependencies, validation, and sensitive data."
---

## Configuration is a typed dependency graph

HCL을 단순 텍스트 템플릿으로 보지 마세요. Block은 객체를 선언하고, expression은 값을 계산하며, reference는 dependency를 만들고, type constraint와 condition은 입력과 결과의 계약을 강화합니다.

Do not treat HCL as text templating. Blocks declare constructs, expressions compute values, references create dependencies, and types and conditions enforce contracts.

## 4a-4b. Resource, data, and references

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
}
```

`resource`는 lifecycle을 관리하고 `data`는 정보를 읽습니다. `data.aws_ami.ubuntu.id` 참조는 값 전달과 dependency edge를 동시에 만듭니다.

### Data source lifecycle을 정확히 구분

Data source가 “state와 무관한 조회”라는 설명은 틀립니다. Terraform은 provider가 읽은 data source attribute를 plan 계산과 state snapshot에 사용할 수 있지만, 해당 remote object의 create, update, delete lifecycle을 소유하지 않습니다.

| Question | Managed resource | Data source |
|---|---|---|
| Remote object를 만드는가? | Provider `Create` operation을 실행할 수 있음 | 기존 object/API를 읽음 |
| Configuration에서 제거하면 remote object를 삭제하는가? | Plan이 destroy를 제안할 수 있음 | Terraform이 remote object를 삭제하지 않음 |
| Attribute가 state에 나타날 수 있는가? | 예 | 예, provider read result가 기록될 수 있음 |
| 다른 block이 reference할 수 있는가? | 예 | 예 |
| Reference가 dependency edge를 만드는가? | 예 | 예 |

Data source는 보통 plan 중 provider read가 가능할 때 평가됩니다. 그러나 argument가 apply 뒤에만 알려지는 managed resource attribute에 의존하면 read가 apply까지 deferred될 수 있습니다. 따라서 “모든 data source는 plan 전에 항상 읽힌다”도 정확하지 않습니다. Plan의 `(known after apply)` 표시와 dependency graph를 함께 읽으세요.

## 4c-4e. Values, types, expressions

```hcl
variable "services" {
  type = map(object({
    port    = number
    enabled = optional(bool, true)
  }))
}

locals {
  enabled_services = {
    for name, service in var.services : name => service
    if service.enabled
  }
}

output "service_names" {
  value = keys(local.enabled_services)
}
```

- Primitive: `string`, `number`, `bool`
- Collection: `list(T)`, `set(T)`, `map(T)`
- Structural: `object({...})`, `tuple([...])`
- `for`, splat, conditional, and built-in functions transform values; they do not generate arbitrary HCL text.

### Variable, local, output scope

| Value kind | 누가 값을 정하는가? | Caller가 override하는가? | Module 밖으로 전달되는가? |
|---|---|---|---|
| Input variable | Caller, tfvars, environment, CLI 등 | 예 | Child module input으로 명시적으로 전달 가능 |
| Local value | 현재 module expression | 아니요 | 직접 노출되지 않음 |
| Output value | 현재 module expression | 아니요 | Module의 공개 result contract가 됨 |

Local value는 반복 expression에 이름을 붙이고 transformation을 한곳에 모으는 도구입니다. Variable의 default 대체물이 아니고 parent/child module 사이에 자동 상속되지 않습니다. Child가 값이 필요하면 input variable로 전달하고, caller가 결과를 사용해야 하면 output으로 공개합니다.

```hcl
locals {
  normalized_name = lower(trimspace(var.service_name))
  common_tags = merge(var.tags, {
    Service = local.normalized_name
  })
}
```

Local끼리 reference할 수 있지만 dependency cycle은 허용되지 않습니다. 많은 local을 단계별 imperative assignment처럼 연결하기보다 의미 있는 derived value의 이름과 contract를 표현하세요.

## 4f. Dependencies

암시적 dependency가 우선입니다. `depends_on`은 참조할 값은 없지만 behavior상 선행되어야 하는 경우에만 추가합니다. 과도한 명시적 dependency는 unknown values와 보수적인 plan을 늘릴 수 있습니다.

## 4g. Validation layers

| Mechanism | Best fit |
|---|---|
| Variable `validation` | 입력 자체의 유효성 |
| `precondition` | resource/data/output 동작 전 가정 |
| `postcondition` | 적용 또는 읽기 후 보장 |
| `check` block | 지속적 assertion; failure is generally a warning, not apply blocking |

## 4h. Sensitive data

`sensitive = true`는 표시를 가리지만 state 저장을 자동 방지하지 않습니다. Secure the backend, limit access, avoid hard-coded credentials, prefer dynamic credentials, and use ephemeral/write-only capabilities only in supported contexts.

Vault와 같은 secrets manager를 사용하면 Terraform configuration에 장기 비밀을 하드코딩하지 않고 필요한 시점에 값을 조회할 수 있습니다. 그러나 provider가 읽은 secret은 사용 방식에 따라 state나 plan에 남을 수 있으므로, Vault 사용 자체를 비저장의 보장으로 오해하지 말고 schema의 ephemeral/write-only 지원과 state 접근 통제를 함께 확인해야 합니다.

Vault and other secrets managers avoid hard-coding long-lived secrets in configuration. They do not automatically guarantee that a consumed value is absent from plan or state; verify provider schema behavior, use ephemeral or write-only paths where supported, and secure state access.

## Block, argument, expression의 관계

HCL에서 block은 `resource "TYPE" "NAME" { ... }`처럼 body를 가진 구조이고 argument는 `name = expression` 형태로 값을 할당합니다. Expression은 literal, reference, operator, function call, conditional, `for`, splat 등으로 값을 계산합니다. Dynamic block은 repeatable nested block을 생성하지만 top-level resource 자체를 생성하는 문법은 아닙니다.

```hcl
resource "aws_instance" "web" {       # block
  instance_type = var.instance_type    # argument = expression

  tags = merge(local.common_tags, {    # function and object expression
    Name = "${var.environment}-web"    # string template
  })
}
```

Reference `aws_instance.web.id`는 attribute value를 읽는 동시에 consumer가 producer 뒤에 평가되도록 implicit dependency를 만듭니다. 단순 문자열 `"aws_instance.web.id"`는 reference가 아니라 문자 데이터이므로 dependency를 만들지 않습니다.

## Value, type, null, unknown

Terraform type system은 primitive와 collection, structural type을 조합합니다. `list(string)`은 순서와 중복을 유지하고, `set(string)`은 uniqueness를 제공하지만 의미 있는 index를 갖지 않으며, `map(T)`는 string key로 값을 찾습니다. `tuple`과 `object`는 각 위치/속성별 type이 다른 구조를 표현합니다.

- **null:** 값의 의도적 부재이며 argument 생략과 유사하게 처리될 수 있습니다.
- **unknown:** plan 시점에 아직 계산할 수 없고 apply 뒤 알려질 값입니다.
- **sensitive:** UI redaction 표시이며 persistence와 별개입니다.
- **ephemeral:** 지원되는 context에서 plan/state persistence를 피하는 값입니다.

Automatic conversion이 가능한 경우도 있지만 module contract에는 명시적 type constraint를 작성해 caller의 실수를 이른 단계에서 차단합니다. `any`는 모든 값을 아무 제약 없이 허용하는 단순 escape가 아니라 Terraform이 하나의 일관된 type을 추론하도록 하는 placeholder이므로 신중히 사용합니다.

## Collection 변환과 instance identity

```hcl
resource "terraform_data" "service" {
  for_each = var.services
  input    = each.value
}
```

`count` instance는 `[0]`, `[1]` 같은 numeric index로 식별되고 `for_each` instance는 `["]key["]` 형태의 stable key로 식별됩니다. 중간 list item 제거가 뒤 index의 input을 이동시킬 수 있는 반면 map key 제거는 해당 key instance에 집중됩니다. 실제 update 또는 replacement 여부는 resource schema가 결정합니다.

`for_each` key와 `count` 값은 graph가 resource instance address를 만들 때 알려져 있어야 합니다. Apply 뒤에만 알 수 있는 remote ID를 key로 사용하면 plan 단계에서 instance set을 결정할 수 없어 오류가 발생합니다. Sensitive value도 key로 사용하면 key가 UI와 state address에 노출되므로 허용되지 않습니다.

## `for` expression과 dynamic block

Ordinary value를 만들 때는 `for` expression을 사용합니다.

```hcl
locals {
  enabled_ports = {
    for name, service in var.services : name => service.port
    if service.enabled
  }
}
```

Provider schema가 반복 가능한 nested block을 요구할 때만 `dynamic`을 사용합니다. `dynamic "ingress"`의 `for_each`와 iterator는 nested `ingress { ... }` block을 생성합니다. 읽기 어려운 abstraction이 되면 explicit block 또는 module input 재설계를 선택합니다.

```hcl
resource "aws_security_group" "service" {
  name   = "service"
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    iterator = rule

    content {
      description = rule.key
      from_port   = rule.value.port
      to_port     = rule.value.port
      protocol    = "tcp"
      cidr_blocks = rule.value.cidrs
    }
  }
}
```

이 block은 여러 `aws_security_group` instance를 만들지 않습니다. 하나의 resource instance 안에 provider schema가 정의한 여러 `ingress` nested block을 만듭니다. Top-level resource 반복은 resource-level `for_each`/`count`, list/map 값 생성은 `for` expression, nested block 생성은 `dynamic`이라는 경계를 유지합니다. `dynamic`은 `lifecycle`, `provider`, `depends_on` 같은 meta-argument를 생성할 수 없습니다.

## Meta-arguments를 목적별로 구분

| Meta-argument | 핵심 질문 |
|---|---|
| `count` | 동일 block의 instance 수는 몇 개인가? |
| `for_each` | 어떤 stable key별 instance가 필요한가? |
| `depends_on` | 표현식에 드러나지 않는 hidden dependency가 있는가? |
| `provider` | 어떤 provider configuration instance를 사용할 것인가? |
| `lifecycle` | replacement, destroy protection, attribute ownership을 어떻게 조정할 것인가? |

`create_before_destroy`는 replacement order를 바꾸지만 old/new 동시 존재가 가능한 이름과 quota가 필요합니다. `prevent_destroy`는 block이 configuration에 있는 동안 destroy/replacement plan을 거부하지만 backup이나 policy를 대신하지 않습니다. `ignore_changes`는 external controller와 attribute ownership을 나눌 때 사용하며 drift 전체를 숨기는 도구가 아닙니다. `replace_triggered_by`는 managed resource/attribute 변화에 replacement를 연결합니다.

## Condition을 가장 이른 올바른 위치에 배치

- Variable `validation`: input 자체가 contract를 만족하는가?
- `precondition`: resource/data/output operation 전에 조합된 가정이 맞는가?
- `postcondition`: provider가 읽거나 만든 결과가 보장을 만족하는가?
- `check`: 배포 뒤 지속적으로 확인할 assertion인가?

`check` failure는 일반적으로 warning을 보고하며 precondition이나 postcondition과 같은 blocking enforcement가 아닙니다. Security policy와 혼동하지 않습니다. Error message에는 기대 조건과 사용자가 고칠 방법을 포함합니다.

## Secret lifecycle

Credential을 `.tf`에 literal로 작성하거나 committed tfvars, CLI history에 남기지 않습니다. Environment, workload identity, dynamic provider credentials 등 provider가 지원하는 standard chain을 우선합니다. State와 saved plan은 sensitive material일 수 있으므로 encryption, least privilege, versioning, audit를 적용합니다. Terraform 1.12의 ephemeral value와 provider write-only argument는 지원되는 schema/context에서만 비저장 경계를 제공합니다.

## 시험 함정과 self-check

- Output은 child/root module 밖으로 값을 노출하지만 root input을 공급하지 않습니다.
- Local value는 input이 아니며 caller가 override할 수 없습니다.
- Data source도 provider read 결과가 state에 기록될 수 있지만 remote lifecycle은 관리하지 않습니다.
- `depends_on`은 모든 block에 필요한 boilerplate가 아닙니다.
- `sensitive`와 encryption, ephemeral은 서로 다른 문제를 해결합니다.

다음 질문에 답할 수 있어야 합니다.

1. `list`, `set`, `map` 중 instance key 안정성이 필요한 `for_each` input에 무엇을 선택할 것인가?
2. `for` expression, resource `for_each`, `dynamic` block은 각각 무엇을 반복하는가?
3. Unknown value가 variable validation보다 postcondition에서 더 적합할 수 있는 이유는 무엇인가?
4. `ignore_changes`를 전체 attribute에 무분별하게 적용하면 어떤 drift가 가려지는가?
5. Sensitive value가 CLI에 가려져도 state 보호가 필요한 이유는 무엇인가?

## 다음 연결 / Why next

구성의 input/output 계약을 재사용 가능한 경계로 묶으면 [module](/domains/05-modules/)이 됩니다.

**Official sources:** [Resources](https://developer.hashicorp.com/terraform/language/v1.12.x/resources), [Values](https://developer.hashicorp.com/terraform/language/v1.12.x/values), [Functions](https://developer.hashicorp.com/terraform/language/v1.12.x/functions), [Validate](https://developer.hashicorp.com/terraform/language/v1.12.x/validate), [Sensitive data](https://developer.hashicorp.com/terraform/language/v1.12.x/manage-sensitive-data)<br />
**Labs:** [02 Variables/outputs](/labs/02-variables-outputs/), [03 Data sources](/labs/03-data-sources/), [04 count/for_each](/labs/04-count-for-each/), [07 Lifecycle](/labs/07-lifecycle/), [08 Conditions](/labs/08-custom-conditions/), [09 Dynamic blocks](/labs/09-dynamic-blocks/)<br />
**Questions:** [Domain 4 bank](/archive/practice-exams/domain-4-configuration/)
