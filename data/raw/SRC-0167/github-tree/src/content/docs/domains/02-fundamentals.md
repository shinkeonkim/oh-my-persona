---
title: 02. Terraform 기초 / Fundamentals
description: "Objectives 2a-2d: providers, versions, multiple providers, and state."
---

## 세 구성 요소 / Three cooperating parts

1. **Terraform Core** parses configuration, builds the dependency graph, creates plans, and coordinates apply.
2. **Providers** expose resource/data-source schemas and call remote APIs.
3. **State** binds Terraform addresses such as `aws_instance.web` to remote object identities and metadata.

Core가 “무엇이 필요한가”를 계산하고, provider가 “API로 어떻게 수행하는가”를 구현하며, state가 “어떤 실제 객체를 이미 관리하는가”를 기억합니다.

## 2a-2b. Provider source and version

```hcl
terraform {
  required_version = "~> 1.12.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"
}
```

- `required_providers` declares source addresses and acceptable versions.
- `provider` blocks configure a selected provider instance.
- `terraform init` installs providers and updates `.terraform.lock.hcl` selections.
- Commit the dependency lock file for reproducible provider installation.

## 2c. Multiple providers and aliases

```hcl
provider "aws" {
  region = "ap-northeast-2"
}

provider "aws" {
  alias  = "dr"
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "replica" {
  provider = aws.dr
  bucket   = "example-replica-bucket"
}
```

Alias는 다른 region/account 구성을 명시적으로 선택합니다. Child module은 provider configuration을 자체 정의하기보다 호출자로부터 전달받는 설계를 우선합니다.

## 2d. State is a mapping, not configuration

State는 HCL의 복사본이 아닙니다. 주소, remote ID, 속성 snapshot, dependency metadata를 저장합니다. State 손상이나 유출은 인프라 관리와 비밀 보호에 직접 영향을 주므로 직접 편집하지 말고 backend와 CLI를 사용합니다.

State is not a copy of HCL. It stores bindings, remote identifiers, snapshots, and metadata. Use supported backends and CLI operations rather than manual editing.

## Provider requirement, selection, configuration

Provider 관련 시험 문제는 세 계층을 분리하면 대부분 해결됩니다.

| 계층 | 위치 | 책임 |
|---|---|---|
| Requirement | `terraform.required_providers` | source address와 허용 version constraint 선언 |
| Selection | `.terraform.lock.hcl` | `init`이 선택한 정확한 provider version과 checksum 기록 |
| Configuration | `provider` block | region, endpoint, alias 등 provider instance 설정 |

`version = "~> 5.0"`은 5.x 범위 안에서 허용 가능한 release를 뜻하지만 실제로 어떤 version을 설치할지는 기존 lock selection, registry에서 사용 가능한 release, `terraform init -upgrade` 사용 여부가 함께 결정합니다. Lock file은 사람이 provider constraint를 대신 작성하는 파일이 아니며, team이 같은 selection과 checksum을 사용하도록 version control에 commit하는 것이 일반적입니다.

`terraform init`은 configuration을 읽어 provider package를 설치하고 checksum을 검증합니다. `-upgrade`는 configuration의 constraint 안에서 기존 selection을 다시 고려합니다. `-lockfile=readonly`는 lock file 수정을 막고 기록된 selection/checksum을 검증하므로 `-upgrade`와 목적이 충돌합니다.

## Alias와 module 전달 / Aliased providers

Default provider configuration은 alias가 없는 instance입니다. 같은 provider를 여러 region, account 또는 endpoint로 사용하려면 alias를 추가하고 resource나 module이 어느 instance를 사용할지 명시합니다.

```hcl
provider "aws" {
  region = "ap-northeast-2"
}

provider "aws" {
  alias  = "singapore"
  region = "ap-southeast-1"
}

module "replica" {
  source = "./modules/storage"
  providers = {
    aws = aws.singapore
  }
}
```

Child module은 provider configuration을 상속받을 수 있지만 재사용 가능한 module 내부에 credential이나 특정 region을 고정하면 caller가 실행 환경을 통제하기 어렵습니다. Child module은 `required_providers`로 requirement를 선언하고 root module이 configuration을 소유하는 구조가 기본입니다. Alias를 받는 child module은 `configuration_aliases`도 선언해야 합니다.

## State가 해결하는 네 가지 문제

1. **Binding:** `aws_instance.web` 같은 resource instance address가 어떤 remote ID와 연결됐는지 기억합니다.
2. **Metadata:** dependency와 provider association 등 다음 operation에 필요한 정보를 보관합니다.
3. **Performance:** 매 operation마다 모든 remote object를 전역 검색하지 않고 관리 범위를 좁힙니다.
4. **Collaboration boundary:** backend와 locking을 통해 어느 snapshot을 기준으로 누가 write하는지 조정합니다.

State에는 provider가 반환한 attribute와 output이 들어갈 수 있으므로 secret으로 취급해야 합니다. `sensitive = true`는 CLI 표시를 가리는 기능이지 state encryption이나 비저장을 자동 제공하지 않습니다. Backend access control, encryption, versioning, audit가 함께 필요합니다.

State를 직접 JSON 편집하면 serial, lineage, schema와 binding을 손상할 수 있습니다. 조회는 `terraform state list`, `terraform state show`, `terraform show`; 이동과 제거는 `moved`, `removed` block이나 문서화된 state command를 사용합니다. State command는 remote object 자체가 아니라 binding을 바꿀 수 있으므로 다음 plan의 의미까지 확인해야 합니다.

## Initialization에서 실제로 일어나는 일

```text
Read configuration
  -> initialize backend
  -> download child modules
  -> resolve and install providers
  -> write/update dependency lock selections
  -> prepare working directory metadata
```

`init`은 resource를 생성하지 않습니다. Backend 설정이 바뀌면 `-migrate-state`로 snapshot을 이동할지 `-reconfigure`로 기존 backend metadata를 무시할지 의도를 선택해야 합니다. 둘을 “오류를 없애는 옵션”으로 무작정 사용하면 안 됩니다.

## 시험 함정 / Common traps

- Backend는 cloud resource type을 구현하지 않고 provider는 state storage 방식 자체를 결정하지 않습니다.
- Version constraint와 selected version은 같은 값이 아닙니다.
- Lock file은 provider dependency를 잠그지만 remote module version 전체를 기록하는 파일은 아닙니다.
- Provider alias는 별도 provider binary가 아니라 별도 configuration instance입니다.
- State는 HCL의 backup이 아니며 remote object 그 자체도 아닙니다.
- CLI workspace와 HCP Terraform workspace는 이름만 비슷하고 책임 범위가 다릅니다.

## 스스로 설명하기 / Recall checks

- `required_providers`, `provider`, `.terraform.lock.hcl`을 각각 누가 읽고 무엇을 결정하는지 설명할 수 있는가?
- `init`과 `init -upgrade`의 차이를 version constraint와 연결해 설명할 수 있는가?
- Alias provider를 child module에 전달하는 이유를 account 또는 region 예제로 설명할 수 있는가?
- State file이 없을 때 Terraform이 address와 existing remote object를 자동 연결할 수 없는 이유는 무엇인가?
- `sensitive` 표시와 secure backend가 해결하는 문제가 어떻게 다른가?

## 다음 연결 / Why next

Provider와 state가 준비되는 과정을 실제 명령 순서로 이해하려면 [Core workflow](/domains/03-workflow/)로 이동합니다.

**Official sources:** [Providers](https://developer.hashicorp.com/terraform/language/v1.12.x/providers), [Provider requirements](https://developer.hashicorp.com/terraform/language/v1.12.x/providers/requirements), [Lock file](https://developer.hashicorp.com/terraform/language/v1.12.x/files/dependency-lock), [State purpose](https://developer.hashicorp.com/terraform/language/v1.12.x/state/purpose)<br />
**Lab:** [Lab 01 First project](/labs/01-first-project/)<br />
**Questions:** [Domain 2 bank](/archive/practice-exams/domain-2-terraform-fundamentals/)
