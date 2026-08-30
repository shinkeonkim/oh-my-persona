---
title: Lab 11. Registry Module과 Version
description: Evaluate a registry module contract, constrain its version, and distinguish module selection from provider locking.
---

| Level | Time | Objectives |
|---|---:|---|
| Advanced | 40-60 min | 5a, 5d |

**Read first:** [Modules](/domains/05-modules/), [Terraform 1.12 dependency locks](/reference/terraform-1-12-deep-dive/#provider-constraints-and-the-lock-file)

## Outcome

Terraform Registry module 하나를 선택해 source, version, input, output, provider requirement를 검토합니다. Apply보다 contract review와 dependency selection이 핵심입니다.

## Safe utility module

Cloud resource를 만들지 않는 HashiCorp subnet calculation module을 사용해 registry source와 version selection을 관찰합니다. Registry availability와 current release는 실행 전에 module page에서 확인하고, current stable version이 다르면 해당 release 범위로 constraint를 조정합니다.

```text
lab-11/
├── versions.tf
├── main.tf
└── outputs.tf
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="main.tf"
module "subnet_addrs" {
  source  = "hashicorp/subnets/cidr"
  version = "~> 1.0"

  base_cidr_block = "10.42.0.0/16"
  networks = [
    { name = "web", new_bits = 8 },
    { name = "application", new_bits = 8 },
    { name = "data", new_bits = 8 }
  ]
}
```

```hcl title="outputs.tf"
output "network_cidr_blocks" {
  value = module.subnet_addrs.network_cidr_blocks
}
```

이 module은 계산 결과를 output으로 제공하므로 provider credential이나 cloud cost가 없습니다. Source page의 input/output names가 selected version과 일치하는지 먼저 확인합니다.

## Evaluate before use

1. Verified publisher 여부와 source repository를 확인합니다.
2. Required Terraform/provider version과 upgrade notes를 읽습니다.
3. Required input, default, output, created resource 목록을 확인합니다.
4. Example을 그대로 production에 복사하지 않고 최소 caller를 작성합니다.

Module page에서 다음 표를 직접 채웁니다.

| 항목 | 확인 내용 |
|---|---|
| Source | namespace/name/provider 또는 registry address |
| Stable version | release와 published date |
| Required Terraform | 현재 1.12 범위와 호환 여부 |
| Required providers | source와 constraint, utility module은 없을 수 있음 |
| Required inputs | type, description, default 없음 여부 |
| Outputs | caller가 실제 사용할 contract |
| Repository | tests, license, changelog, maintenance |

```hcl
module "example" {
  source  = "NAMESPACE/NAME/PROVIDER"
  version = "~> X.Y"
}
```

## Initialize and compare

```bash
terraform init
terraform providers
terraform validate
terraform plan
```

First `init`에서 `Downloading registry.terraform.io/hashicorp/subnets/cidr...`와 `Initializing modules...`를 관찰합니다. Exact selected version은 constraint와 registry release에 따라 달라질 수 있으므로 terminal output을 기록합니다.

```bash
terraform plan -out=tfplan
terraform apply tfplan
terraform output -json network_cidr_blocks
```

Expected output은 `web`, `application`, `data` key별 CIDR map입니다. Module이 managed cloud object를 만들지 않더라도 child configuration과 output evaluation은 Terraform graph에 포함됩니다.

- `.terraform/modules/modules.json`에서 selected module source를 관찰하되 generated metadata를 commit하지 않습니다.
- `.terraform.lock.hcl`에는 provider selection과 checksum이 기록되지만 remote module selection은 기록되지 않습니다.
- Module `version`은 registry source에 사용합니다. Git source는 `?ref=`를 사용하고 local source는 local file을 직접 읽습니다.

Version constraint를 허용 범위 안에서 바꾸고 `terraform init -upgrade` 전후 selection을 비교합니다. Upgrade 후 plan과 changelog를 반드시 review합니다.

## Selection experiments

1. `.terraform/modules/modules.json`에서 module key/source/dir을 관찰합니다. Generated file을 edit하거나 commit하지 않습니다.
2. `.terraform.lock.hcl`을 확인합니다. Module이 provider를 요구하지 않으면 module selection이 dependency lock file에 기록되지 않는 점을 확인합니다.
3. `version = "= 1.0.0"` 같은 exact constraint와 `~> 1.0`의 허용 범위를 비교합니다.
4. 존재하지 않는 version으로 바꿔 `init` resolution error를 확인하고 복구합니다.
5. `terraform init -upgrade` 후 selected version, changelog, plan output을 비교합니다.

`init -upgrade`는 constraint 밖 major version을 자동 선택하지 않습니다. Upgrade가 no-op이어도 registry에서 selection을 다시 검토하는 행동을 이해합니다.

## Source type comparison

```hcl
# Registry: version argument
module "registry" {
  source  = "namespace/name/provider"
  version = "~> 2.3"
}

# Git: source query ref
module "git" {
  source = "git::https://example.com/modules.git//network?ref=v2.3.1"
}

# Local: repository commit
module "local" {
  source = "./modules/network"
}
```

Git branch는 움직일 수 있으므로 immutable tag/commit SHA와 supply-chain review를 고려합니다. Local module은 같은 repository commit이 version boundary입니다.

## Troubleshooting

| 증상 | 확인 |
|---|---|
| module not installed | source 변경 뒤 `terraform init` 실행 여부 |
| no releases match | source address와 version constraint |
| unsupported argument | selected version의 input contract |
| provider conflict | root와 child requirement intersection |
| unexpected large plan | module default와 created resource 전체 목록 |

Registry verified status는 publisher identity signal이지 architecture/security guarantee가 아닙니다. Production module은 source review, tests, version policy와 plan review가 필요합니다.

## Safety and cleanup

Network/VPC module처럼 유료 resource를 많이 만드는 module은 plan까지만 수행해도 목표를 달성할 수 있습니다. Apply했다면 module output이 아니라 plan/state의 전체 resource 목록을 기준으로 destroy 완료를 확인합니다.

```bash
terraform destroy -auto-approve
terraform state list
rm -f tfplan
```

Utility module은 remote infrastructure cleanup이 없지만 local state와 generated `.terraform/modules`는 Lab artifact입니다. 완료 기준은 registry/Git/local source의 version mechanism과 provider lock file이 module selection을 대신하지 않는 이유를 설명하는 것입니다.

**Detailed walkthrough:** [Historical Lab 11](/archive/labs/lab-11-module-registry/readme/)  
**Next:** [Lab 12 HCP Terraform](/labs/12-hcp-terraform/) · [Module questions](/archive/practice-exams/domain-5-modules/)
