---
title: 05. Terraform 모듈 / Modules
description: "Objectives 5a-5d: module sources, scope, use, and version management."
---

## Module as a contract

모든 Terraform configuration은 module입니다. 명령을 실행하는 디렉터리는 **root module**, `module` block으로 호출되는 구성은 **child module**입니다. 좋은 module은 input, managed resources, output의 경계를 분명히 합니다.

Every Terraform configuration is a module. The working directory is the root module; configuration called by a `module` block is a child module.

## 5a. Sources

```hcl
module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"
}
```

Sources include local paths, public/private registry addresses, Git, and other supported package sources. Registry modules support the `version` argument; non-registry sources typically pin a revision in the source URL.

## 5b. Scope

- Child module은 parent의 local value나 resource를 자동으로 볼 수 없습니다.
- Inputs enter through variables; results leave through outputs.
- Resource names are scoped to their module address.
- Provider configurations should normally be passed from the root module.

## 5c. Composition

```hcl
module "network" {
  source = "./modules/network"
  cidr   = var.network_cidr
}

module "app" {
  source    = "./modules/app"
  subnet_id = module.network.private_subnet_id
}
```

`module.network.private_subnet_id`는 데이터 전달과 module 간 dependency를 함께 만듭니다. Prefer small composable modules over a single module that owns unrelated lifecycle boundaries.

## 5d. Versions

Module version constraints control acceptable registry releases. Pin deliberately, test upgrades through plan, and avoid unconstrained production dependencies. `terraform init -upgrade` asks Terraform to reconsider selections within configured constraints.

## Module call이 만드는 주소와 graph

Module call은 source code를 복사해 붙이는 기능이 아니라 별도 namespace와 contract를 가진 graph node를 만듭니다. `module "network"` 안의 `aws_vpc.main`은 state에서 `module.network.aws_vpc.main` 주소를 갖습니다. Module call에 `for_each`를 사용하면 `module.network["prod"]...`처럼 module instance key도 주소에 포함됩니다.

Parent가 `module.network.vpc_id`를 참조하면 child output에서 parent consumer로 value flow와 dependency edge가 생깁니다. Child 내부 resource를 `module.network.aws_vpc.main.id`처럼 직접 참조할 수는 없습니다. Output으로 의도적으로 노출한 값만 public interface입니다.

## Source 유형과 version 선택

| Source | 예 | Version control 방식 |
|---|---|---|
| Local path | `./modules/network` | 같은 repository commit |
| Registry | `hashicorp/consul/aws` | module call의 `version` constraint |
| Git | `git::https://...git?ref=v1.2.0` | branch, tag, commit SHA `ref` |
| Object storage/package | 문서화된 source URL | source별 immutable version/key |

Registry module의 `version` argument는 semantic version constraint를 사용합니다. Git/local source에 같은 argument를 붙이지 않습니다. Remote source가 바뀌면 `terraform init`을 다시 실행해 module package를 설치해야 하며 `terraform get`은 module update에 초점을 둔 명령입니다.

`.terraform/modules/modules.json`은 working directory의 generated metadata입니다. Provider selection/checksum을 기록하는 `.terraform.lock.hcl`과 달리 remote module selection 전체를 dependency lock file에 고정하지 않습니다. 그래서 source와 version constraint, Git ref를 configuration에서 명확히 관리해야 합니다.

## 좋은 module contract의 기준

1. **Cohesion:** 함께 생성·변경·삭제되는 resource를 하나의 lifecycle boundary로 묶습니다.
2. **Small interface:** caller가 결정해야 하는 input만 받고 구현 세부 값을 요구하지 않습니다.
3. **Useful outputs:** 다른 module이 실제로 참조할 identity와 endpoint만 노출합니다.
4. **Typed inputs:** object type, validation, nullable/default 의미를 문서화합니다.
5. **Provider neutrality:** credential과 root 실행 환경을 module 내부에 하드코딩하지 않습니다.
6. **Upgrade path:** breaking change는 version과 `moved` block 등 migration guidance로 관리합니다.

단일 resource를 무조건 module로 감싸거나 network, database, application처럼 lifecycle이 다른 모든 것을 하나의 거대 module에 넣는 것은 재사용성을 높이지 않습니다. Module은 directory 구조가 아니라 변경 책임의 경계입니다.

```hcl
variable "service" {
  type = object({
    name = string
    port = number
  })

  validation {
    condition     = var.service.port >= 1 && var.service.port <= 65535
    error_message = "service.port must be between 1 and 65535."
  }
}

output "service_id" {
  description = "Stable identifier consumed by sibling modules."
  value       = terraform_data.service.id
}
```

## Provider requirement와 configuration

Reusable child module은 필요한 provider source와 최소 version을 `required_providers`에 선언합니다. Root module은 조직이 검증한 version upper bound와 실제 provider configuration을 소유합니다. Default provider는 자동 전달될 수 있지만 alias가 필요하면 child의 `configuration_aliases`와 parent module call의 `providers` map을 명시합니다.

Module 내부에 `provider` block을 두면 module instance에 `for_each`, `count`, `depends_on` 적용과 제거 과정에서 제약이 생길 수 있습니다. 현대 module은 provider configuration을 caller에서 받는 방식을 우선합니다.

## Composition과 flat dependency

HashiCorp guidance는 child module끼리 직접 깊게 결합하기보다 root module이 outputs를 inputs로 연결하는 **flat composition**을 권장합니다. Root가 전체 graph를 조립하면 module을 독립적으로 교체하고 test하기 쉽습니다.

```hcl
module "network" {
  source = "./modules/network"
  cidr   = var.network_cidr
}

module "application" {
  source     = "./modules/application"
  subnet_ids = module.network.private_subnet_ids
}
```

## Registry module 평가 절차

Verified badge만 보고 채택하지 않습니다. Source repository, 최근 release와 maintenance, required Terraform/provider versions, created resource, input defaults, output, upgrade guide, license를 확인합니다. Example은 학습 출발점이지 production baseline이 아닙니다. 특히 network module은 default만으로 많은 유료 resource를 만들 수 있으므로 plan에서 전체 resource count와 naming, public exposure를 검토합니다.

## 시험 함정 / Exam traps

- 모든 configuration은 module이며 현재 working directory가 root module입니다.
- Child module은 parent의 variable/local/resource를 이름만 같다고 자동 참조하지 않습니다.
- Module output은 state에 기록될 수 있고 `sensitive` output도 비저장을 보장하지 않습니다.
- Registry `version`과 provider `.terraform.lock.hcl` selection은 다른 dependency mechanism입니다.
- `init -upgrade`는 configured constraint를 무시해 임의 major version으로 올리지 않습니다.
- Module source 변경은 resource address 이동과 별개입니다. Resource가 새 module address로 이동하면 `moved` block이 필요할 수 있습니다.

## 스스로 설명하기 / Recall checks

- Root/child module과 module call의 차이를 state address 예제로 설명할 수 있는가?
- Local, registry, Git source가 version을 고정하는 방식을 각각 말할 수 있는가?
- Provider requirement를 child에 두고 configuration을 root에 두는 이유는 무엇인가?
- Module output reference가 data flow와 dependency를 동시에 만드는 과정을 설명할 수 있는가?
- Module을 upgrade하기 전에 source, changelog, plan에서 무엇을 확인해야 하는가?

## 다음 연결 / Why next

Module 경계를 바꾸면 resource address도 바뀔 수 있습니다. 안전한 리팩터링을 위해 [state와 moved/removed block](/domains/06-state/)을 이해해야 합니다.

**Official sources:** [Modules overview](https://developer.hashicorp.com/terraform/language/v1.12.x/modules), [Module configuration](https://developer.hashicorp.com/terraform/language/v1.12.x/modules/configuration), [Composition](https://developer.hashicorp.com/terraform/language/v1.12.x/modules/develop/composition)<br />
**Labs:** [05 Build a module](/labs/05-modules/), [11 Registry modules](/labs/11-registry-modules/)<br />
**Questions:** [Domain 5 bank](/archive/practice-exams/domain-5-modules/)
