---
title: Lab 06. Remote State와 Locking
description: Migrate local state to an S3 backend using Terraform 1.12 lock files and verify safe locking behavior.
---

| Level | Time | Objectives |
|---|---:|---|
| Intermediate | 50-70 min | 6a-6c |

**Read first:** [State management](/domains/06-state/), [Terraform 1.12 S3 locking](/reference/terraform-1-12-deep-dive/#s3-state-locking)

## Outcome

Local state를 pre-created S3 backend로 migrate하고 `use_lockfile = true`의 lock object를 확인합니다. DynamoDB table은 만들지 않습니다.

:::caution[Bootstrap and recovery]
Backend bucket을 같은 state 안에서 생성하지 마세요. Backend는 state를 읽기 전에 존재해야 합니다. Versioning과 encryption을 활성화하고 disposable key prefix를 사용합니다.
:::

## Configure

```hcl
terraform {
  backend "s3" {
    bucket       = "YOUR_EXISTING_STATE_BUCKET"
    key          = "labs/06/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }
}
```

Credential을 backend block에 작성하지 말고 environment, profile, workload identity 같은 standard credential chain을 사용합니다.

## Prerequisites and bootstrap

이 Lab은 두 종류의 infrastructure를 구분합니다.

1. **Backend infrastructure:** 미리 존재하는 S3 bucket. Versioning, encryption, public access blocking을 활성화하고 Lab state와 분리된 bootstrap process로 관리합니다.
2. **Lab managed object:** 비용이 없는 `terraform_data` resource. 이 state를 local에서 S3로 이동합니다.

필요 권한은 bucket/key read-write, list, lock object create/delete, version 조회입니다. Production bucket 대신 disposable prefix `labs/06/<learner>/terraform.tfstate`를 사용합니다. Bucket name, account ID, credential을 repository에 기록하지 않습니다.

```text
lab-06/
├── versions.tf
├── main.tf
└── backend.tf.disabled
```

```hcl title="versions.tf"
terraform {
  required_version = ">= 1.12.0, < 1.13.0"
}
```

```hcl title="main.tf"
resource "terraform_data" "migration_marker" {
  input = {
    lab     = "06"
    purpose = "observe backend migration"
  }
}

output "marker_id" {
  value = terraform_data.migration_marker.id
}
```

먼저 backend block 없이 local state를 생성합니다.

```bash
terraform init
terraform apply -auto-approve
terraform state list
terraform state pull > before-migration.tfstate
```

Expected address는 `terraform_data.migration_marker` 한 개입니다. Backup은 secret으로 취급하고 public Git에 넣지 않습니다.

이제 위 backend configuration을 `backend.tf`로 활성화하되 실제 bucket/key/region으로 바꿉니다. Backend block에서는 input variable을 사용할 수 없으므로 환경별 partial configuration이 필요하면 `-backend-config`와 보호된 config file을 사용합니다.

## Migrate and observe

```bash
terraform init -migrate-state
terraform state pull > state-backup.json
terraform plan
```

Expected initialization flow:

```text
Initializing the backend...
Do you want to copy existing state to the new backend?
Successfully configured the backend "s3"!
```

Prompt wording은 version과 상황에 따라 달라질 수 있습니다. 반드시 local source state와 intended S3 destination을 확인한 뒤 승인합니다. Migration 뒤 local `terraform.tfstate`를 authoritative snapshot으로 계속 사용한다고 가정하지 않습니다.

1. Migration prompt의 source와 destination을 읽고 승인합니다.
2. S3에서 state object와 version history를 확인합니다.
3. State write operation 동안 같은 key의 `.tflock` object가 생성되는지 확인합니다.
4. 두 번째 writer가 lock을 얻지 못하면 operation이 계속되지 않는 이유를 설명합니다.

## Lock observation without corruption

State write가 충분히 짧으면 `.tflock` object를 눈으로 보기 어렵습니다. Configuration에 local-exec sleep을 추가하거나 operation을 강제로 지연시키는 방식은 불필요한 위험을 만듭니다. 대신 두 terminal에서 같은 key에 대해 normal plan/apply를 준비하고, 첫 operation이 lock을 보유하는 자연스러운 시점에 두 번째 command가 lock diagnostic을 받는지 관찰합니다. Lock을 얻지 못했다면 두 번째 operation을 취소하고 첫 operation이 정상 종료하며 lock을 자동 해제하도록 둡니다.

```bash
# Terminal A
terraform apply

# Terminal B, A가 state operation 중일 때만 실행
terraform plan -lock-timeout=10s
```

`-lock-timeout`은 lock을 제거하는 option이 아니라 지정 시간 동안 acquisition을 재시도합니다. `-lock=false`는 shared backend에서 사용하지 않습니다.

S3 version listing에서 migration 전/후 state version을 확인하고 current object에 marker address가 있는지 `terraform state pull`로 확인합니다. Raw JSON의 secret value를 terminal history나 issue에 복사하지 않습니다.

## Migration decisions

| 상황 | 선택 |
|---|---|
| Existing local state를 새 backend로 이동 | `init -migrate-state` |
| Backend address만 다시 설정하고 migration하지 않음 | `init -reconfigure`를 recovery 문맥에서 검토 |
| Backend credential 변경 | standard chain/config 갱신 후 `init` 필요 여부 확인 |
| State key 변경 | 다른 state boundary가 될 수 있으므로 migration 의도 확인 |

Key를 잘못 쓰면 Terraform이 빈 state처럼 보여 create plan을 만들 수 있습니다. 그때 apply하지 말고 backend key/workspace/source snapshot을 먼저 확인합니다.

## Troubleshooting

| 증상 | 확인 |
|---|---|
| AccessDenied on state | bucket policy, KMS permission, credential identity |
| failed to lock state | active writer, stale lock 여부, system clock/network |
| no state after migration | bucket/key/region과 source prompt 선택 |
| checksum/serialization error | manual object edit 여부, versioned restore 후보 |
| variable not allowed | backend block에서 `var.*` 사용 여부 |

Stale lock이라고 판단해도 original writer process, CI run, HCP/automation job이 끝났는지 확인합니다. Lock ID와 backend를 재확인한 뒤 조직 recovery procedure에서만 `force-unlock`을 사용합니다.

`-lock=false`와 `force-unlock`을 정상 workflow로 사용하지 않습니다. Force unlock은 원래 writer가 종료됐고 자동 unlock이 실패한 자신의 lock에만 사용합니다.

## Cleanup

1. Managed Lab resources를 먼저 destroy합니다.
2. 필요하면 backend block을 제거하고 `terraform init -migrate-state`로 local state를 복구합니다.
3. State와 lock object가 안전하게 정리된 뒤 Lab key prefix를 삭제합니다.
4. Backup에는 secret이 있을 수 있으므로 안전하게 폐기합니다.

Detailed cleanup:

```bash
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
terraform state list
```

Managed object가 없는 것을 확인한 뒤 backend block을 제거하거나 다시 `.disabled`로 바꾸고 다음을 실행합니다.

```bash
terraform init -migrate-state
terraform state list
```

Local destination이 맞는지 prompt를 읽습니다. State가 비어 있어도 migration metadata가 올바르게 바뀌었는지 확인한 다음에만 Lab key와 old versions를 retention policy에 맞게 정리합니다. Shared backend bucket 자체를 이 Lab에서 삭제하지 않습니다.

완료 기준은 state location, locking, encryption/access control이 서로 다른 책임임을 설명하고 local→S3→local migration의 각 source/destination을 기록하는 것입니다.

**Detailed walkthrough:** [Historical Lab 06](/archive/labs/lab-06-remote-state/readme/)의 DynamoDB 설명보다 이 페이지의 Terraform 1.12 절차를 우선합니다.  
**Next:** [Lab 07 Lifecycle](/labs/07-lifecycle/) · [State questions](/archive/practice-exams/domain-6-state/)
