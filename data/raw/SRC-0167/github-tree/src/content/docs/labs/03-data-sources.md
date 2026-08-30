---
title: Lab 03. 기존 정보 조회 / Data Sources and References
description: Compare read-only data sources with managed resources and inspect the dependency edges created by references.
---

| Level | Time | Objectives |
|---|---:|---|
| Beginner | 35-50 min | 4a-4b |

**Read first:** [Configuration 4a-4b](/domains/04-configuration/#4a-4b-resource-data-and-references)

## Outcome

AWS AMI와 availability zone을 data source로 읽고 managed resource argument에서 참조합니다. “조회한다”와 “lifecycle을 관리한다”의 차이를 plan에서 구분합니다.

:::caution[Cost boundary]
Download solution에는 EC2 resource가 있습니다. Data source 학습만 필요하면 `terraform plan`까지만 수행하세요. Apply하면 compute 비용이 발생할 수 있습니다.
:::

## Prepare

1. [Lab 03 downloads](/guide/labs-and-practice/#lab-03)을 disposable directory에 저장합니다.
2. Region에서 default VPC와 해당 instance type이 사용 가능한지 확인합니다.
3. AMI owner, architecture, name filter가 너무 넓지 않은지 읽습니다.

## No-cost producer and consumer

먼저 cloud API 없이 data source의 read-only 역할을 확인합니다. Producer state를 consumer가 built-in `terraform_remote_state` data source로 읽습니다.

```text
lab-03/
├── producer/
│   ├── main.tf
│   └── outputs.tf
└── consumer/
    └── main.tf
```

```hcl title="producer/main.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}

resource "terraform_data" "catalog" {
  input = {
    endpoint = "catalog.internal"
    port     = 8443
  }
}

output "service" {
  value = terraform_data.catalog.output
}
```

```hcl title="consumer/main.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}

data "terraform_remote_state" "producer" {
  backend = "local"
  config = {
    path = "../producer/terraform.tfstate"
  }
}

resource "terraform_data" "consumer" {
  input = {
    upstream_endpoint = data.terraform_remote_state.producer.outputs.service.endpoint
    upstream_port     = data.terraform_remote_state.producer.outputs.service.port
  }
}

output "resolved_upstream" {
  value = terraform_data.consumer.output
}
```

Producer를 먼저 apply합니다.

```bash
cd producer
terraform init
terraform apply -auto-approve
terraform output -json

cd ../consumer
terraform init
terraform plan -out=tfplan
terraform show tfplan
```

Consumer plan에서 `data.terraform_remote_state.producer`는 existing state output을 읽고 `terraform_data.consumer`만 lifecycle-managed create 대상입니다. Reference가 data read 결과를 consumer input으로 전달하므로 graph dependency도 생깁니다.

:::caution
`terraform_remote_state`는 output만 configuration에서 참조하더라도 caller가 underlying state snapshot에 접근할 credential을 필요로 할 수 있습니다. Production에서는 state access가 너무 넓지 않은지 검토하고 HCP Terraform data sharing 등 더 제한적인 mechanism도 비교합니다.
:::

## Execute and inspect

```bash
terraform init
terraform validate
terraform plan -out=tfplan
terraform show tfplan
```

Plan에서 다음을 구분합니다.

- `data.aws_ami.ubuntu`: existing information read
- `data.aws_availability_zones.available`: provider API result
- `aws_instance.web`: managed lifecycle proposal
- `data.aws_ami.ubuntu.id` reference: value flow와 implicit dependency

`most_recent = true` 결과는 시간이 지나면 바뀔 수 있습니다. 같은 configuration이 새 AMI를 선택할 때 plan에 어떤 change가 나타날지 설명합니다.

## Provider data source와 비교

AWS credential이 준비됐다면 apply 없이 다음 read-only configuration을 별도 directory에서 실행합니다.

```hcl
terraform {
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

data "aws_availability_zones" "available" {
  state = "available"
}

output "zone_names" {
  value = data.aws_availability_zones.available.names
}
```

```bash
terraform init
terraform plan
terraform apply -refresh-only
terraform output zone_names
```

Data source는 provider API read가 필요하므로 credential과 network가 필요합니다. 하지만 availability zone을 Terraform이 생성하거나 삭제하지 않습니다. `state show data.aws_availability_zones.available`에 read result가 기록될 수 있다는 사실과 lifecycle ownership을 구분합니다.

## Deliberate experiments

1. Consumer를 producer보다 먼저 plan해 missing state file 오류를 확인합니다.
2. Producer output 이름 `service`를 `service_info`로 바꾸되 consumer를 그대로 두고 unsupported attribute 오류를 확인합니다.
3. Producer endpoint를 변경하고 apply한 뒤 consumer plan에서 input update를 확인합니다.
4. AWS variant에서 region을 바꾸고 returned zone set과 data source address가 어떻게 유지되는지 관찰합니다.

## Expected failures

| 증상 | 의미 | 수정 |
|---|---|---|
| state snapshot not found | producer artifact가 아직 없음 | producer apply와 path 확인 |
| unsupported attribute | output contract 이름 불일치 | producer outputs와 consumer reference 정렬 |
| no valid credential source | provider data read 인증 실패 | standard AWS credential chain 확인 |
| no matching AMI | filter/owner/architecture가 region과 불일치 | provider registry와 image publisher 기준 확인 |

Data source query가 너무 넓으면 결과가 시간에 따라 바뀌고 downstream replacement를 유발할 수 있습니다. Owner ID, architecture, virtualization, name pattern을 구체화하고 `most_recent` 사용의 upgrade 의도를 문서화합니다.

## Verify and cleanup

- Apply하지 않았다면 remote cleanup은 필요하지 않으며 saved plan만 제거합니다.
- Apply했다면 `terraform state list`, `terraform state show aws_instance.web`을 확인한 뒤 즉시 destroy합니다.
- Data source는 state에 일부 read result가 기록될 수 있지만 remote object lifecycle을 소유하지 않습니다.

Cleanup은 dependency의 역순으로 수행합니다.

```bash
cd consumer
terraform destroy -auto-approve
rm -f tfplan

cd ../producer
terraform destroy -auto-approve
```

AWS plan-only variant는 `.terraform/`, lock file 유지 정책, saved plan만 정리하면 remote cleanup이 없습니다. EC2 variant를 apply했다면 instance가 destroy plan에 포함됐는지 확인하고 data source를 삭제 대상으로 세지 않습니다.

완료 기준은 resource와 data source를 plan action, state address, remote lifecycle 세 관점에서 구분하고, reference가 만드는 value flow를 설명하는 것입니다.

**Detailed walkthrough:** [Historical Lab 03](/archive/labs/lab-03-data-sources/readme/)  
**Next:** [Lab 04 count and for_each](/labs/04-count-for-each/) · [Official data sources](https://developer.hashicorp.com/terraform/language/v1.12.x/data-sources)
