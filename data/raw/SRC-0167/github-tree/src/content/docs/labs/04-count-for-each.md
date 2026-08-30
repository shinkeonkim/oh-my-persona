---
title: Lab 04. count와 for_each
description: Compare index-based and key-based resource addresses and predict changes when collection membership changes.
---

| Level | Time | Objectives |
|---|---:|---|
| Intermediate | 45-60 min | 4d-4f |

**Read first:** [Types, expressions, dependencies](/domains/04-configuration/#4c-4e-values-types-expressions)

## Outcome

같은 세 항목을 `count`와 `for_each`로 선언하고 중간 항목을 제거합니다. 핵심 관찰 대상은 remote 이름이 아니라 state의 **instance address 안정성**입니다.

## Complete no-cost configuration

```text
lab-04/
├── versions.tf
├── variables.tf
├── main.tf
└── outputs.tf
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="variables.tf"
variable "service_list" {
  type    = list(string)
  default = ["web", "api", "worker"]
}

variable "service_map" {
  type = map(object({
    port    = number
    enabled = bool
  }))
  default = {
    web    = { port = 80, enabled = true }
    api    = { port = 8080, enabled = true }
    worker = { port = 9000, enabled = true }
  }
}
```

```hcl title="main.tf"
resource "terraform_data" "by_count" {
  count = length(var.service_list)

  input = {
    position = count.index
    name     = var.service_list[count.index]
  }
}

resource "terraform_data" "by_key" {
  for_each = {
    for name, service in var.service_map : name => service
    if service.enabled
  }

  input = {
    name = each.key
    port = each.value.port
  }
}
```

```hcl title="outputs.tf"
output "count_addresses" {
  value = [for item in terraform_data.by_count : item.input]
}

output "keyed_services" {
  value = { for key, item in terraform_data.by_key : key => item.output }
}
```

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=initial.tfplan
terraform apply initial.tfplan
terraform state list
```

초기 state에는 `by_count[0..2]`와 `by_key["api"|"web"|"worker"]`가 있어야 합니다. Set/map key의 출력 순서는 작성 순서와 같다고 가정하지 않습니다.

## Experiment

1. Historical guide의 count와 for_each configuration을 별도 directory에서 준비합니다.
2. Apply 전 plan에서 address를 적습니다.

```text
example.item[0]
example.item[1]
example.item[2]

example.item["api"]
example.item["db"]
example.item["web"]
```

3. `terraform state list` 결과를 저장합니다.
4. List 중간 값과 map/set의 같은 key를 각각 제거합니다.
5. 새 plan의 address와 action을 이전 결과와 비교합니다.

## Membership change experiment

`service_list`에서 중간 `"api"`를 제거하고 `service_map`에서도 `api` key를 제거합니다.

```hcl
service_list = ["web", "worker"]

service_map = {
  web    = { port = 80, enabled = true }
  worker = { port = 9000, enabled = true }
}
```

```bash
terraform plan -out=remove-api.tfplan
terraform show remove-api.tfplan
```

Count에서는 old index 1이 `api`였지만 새 index 1은 `worker`입니다. `terraform_data`는 input change를 update로 처리할 수 있지만 다른 provider resource는 schema에 따라 replacement가 될 수 있습니다. 핵심은 “두 개가 무조건 재생성된다”가 아니라 **address가 position에 결합돼 input association이 이동했다**는 사실입니다.

For_each에서는 `terraform_data.by_key["api"]`만 collection에서 사라지고 `web`, `worker` key는 유지됩니다. Stable business identity가 있다면 key 기반 address가 refactoring과 membership change를 더 명확하게 표현합니다.

## Unknown and sensitive key experiment

다음 잘못된 패턴을 읽고 plan 전에 왜 instance set을 정할 수 없는지 설명합니다.

```hcl
# 잘못된 예: apply 뒤 생성되는 id를 key로 사용
resource "terraform_data" "invalid" {
  for_each = toset([terraform_data.by_count[0].id])
  input    = each.key
}
```

`for_each` key는 plan에서 resource address를 만들기 위해 known이어야 합니다. Sensitive value도 address에 key가 노출되므로 사용할 수 없습니다. List를 `toset()`하면 중복과 순서가 제거되므로 key identity가 정말 원하는 의미인지 먼저 확인합니다.

## Checkpoints

- `count.index`는 numeric position이고 `each.key`는 collection identity입니다.
- `each.value`는 map value 또는 set에서는 key와 같은 string입니다.
- `for_each`와 `count`를 같은 block에 함께 사용할 수 없습니다.
- Resource-level `for_each`는 instances를 만들고 `for` expression은 value를 만듭니다.
- Address 변경이 remote action으로 어떻게 나타나는지는 provider schema와 moved mapping에 달려 있습니다.

## Troubleshooting

| 오류 | 원인 | 수정 |
|---|---|---|
| unsuitable `for_each` value | list를 직접 전달 | map 또는 set of strings로 명시 변환 |
| keys derived from unknown values | apply-time value가 key | configuration-known business key 사용 |
| duplicate object key | `for` expression key 충돌 | grouping `...` 또는 unique key 설계 |
| invalid index | membership 변경 뒤 old index 참조 | collection과 consumer address를 함께 수정 |

Index 기반 resource를 이미 운영 중이고 key 기반으로 전환한다면 단순 syntax 변경만으로 destroy/create가 생길 수 있습니다. `moved` block에서 old indexed address와 new keyed address를 명시하고 plan을 검토합니다.

Provider resource의 replace/update 결과는 schema에 따라 달라질 수 있습니다. “count는 항상 N개를 재생성한다”를 외우지 말고 index가 이동해 어떤 instance가 어떤 input을 받게 됐는지 설명하세요.

## Verification

- `count.index`는 numeric position과 결합됩니다.
- `each.key`는 stable key와 결합됩니다.
- `for_each`는 map 또는 set of strings를 직접 받으며 list는 명시적 conversion이 필요합니다.
- Unknown collection keys는 plan 전에 instance address를 정할 수 없으므로 사용할 수 없습니다.

Apply했다면 원래 collection을 복원하지 말고 `terraform destroy`로 Lab object를 정리합니다.

```bash
terraform apply remove-api.tfplan
terraform state list
terraform destroy -auto-approve
rm -f initial.tfplan remove-api.tfplan
```

완료 기준은 initial/removal 두 plan의 address 표를 직접 작성하고, count와 for_each가 “몇 개를 만든다” 이상의 identity model이라는 점을 설명하는 것입니다.

**Detailed walkthrough:** [Historical Lab 04](/archive/labs/lab-04-count-for-each/readme/)  
**Related:** [Configuration concepts](/domains/04-configuration/) · [Configuration questions](/archive/practice-exams/domain-4-configuration/)  
**Next:** [Lab 05 Modules](/labs/05-modules/)
