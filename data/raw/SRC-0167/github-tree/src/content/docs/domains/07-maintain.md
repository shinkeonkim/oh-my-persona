---
title: 07. 인프라 유지보수 / Maintain Infrastructure
description: "Objectives 7a-7c: import, state inspection, and verbose logging."
---

## 7a. Import existing infrastructure

Import connects an existing remote object to a Terraform resource address. It does not automatically guarantee that your configuration matches every remote argument.

```hcl
import {
  to = aws_s3_bucket.logs
  id = "existing-log-bucket"
}

resource "aws_s3_bucket" "logs" {
  bucket = "existing-log-bucket"
}
```

구성 기반 `import` block은 plan에서 검토 가능한 workflow를 제공합니다. CLI `terraform import ADDRESS ID`도 알아야 하지만, import 후 반드시 plan을 실행해 configuration과 remote object의 차이를 확인합니다.

## 7b. Inspect state safely

```bash
terraform state list
terraform state show 'aws_s3_bucket.logs'
terraform show
terraform output
```

- `state list`: addresses in state
- `state show`: attributes for one bound resource instance
- `show`: human-readable state or plan
- `output`: root module output values

Quote addresses containing brackets or string keys so the shell does not reinterpret them.

## 7c. Verbose logging

```bash
export TF_LOG=DEBUG
export TF_LOG_PATH=./terraform-debug.log
terraform plan
unset TF_LOG TF_LOG_PATH
```

Use logs to diagnose initialization, provider communication, graph evaluation, and remote API failures. Logs can contain credentials or sensitive values, so scope collection, protect files, and remove them after diagnosis.

## Troubleshooting order

1. Read the diagnostic and identify Core, provider, backend, or remote API ownership.
2. Run `terraform fmt` and `terraform validate` for configuration issues.
3. Confirm versions, credentials, network, and backend access.
4. Reproduce with the smallest command and enable the least verbose useful log level.
5. Compare state, plan, and remote reality before changing bindings.

## Import의 세 단계 / Import workflow

Import는 existing remote object를 Terraform address에 연결합니다. 성공적인 유지보수 작업은 “import command가 성공했다”에서 끝나지 않습니다.

1. **Configuration 작성:** Resource type, argument, provider configuration과 address를 먼저 정의합니다.
2. **Binding 추가:** Configuration-driven `import` block 또는 CLI `terraform import ADDRESS ID`를 사용합니다.
3. **Convergence 검토:** Normal plan에서 no-op인지, update/replacement가 필요한지 확인하고 configuration을 조직 의도에 맞춥니다.

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "existing-log-bucket"
}

import {
  to = aws_s3_bucket.logs
  id = "existing-log-bucket"
}
```

Import block은 plan에서 검토 가능하고 여러 import를 automation할 수 있습니다. Provider가 config generation을 지원하면 `terraform plan -generate-config-out=generated.tf`로 출발점을 만들 수 있지만 생성 결과가 최소·보안·조직 표준 configuration임을 보장하지 않습니다. 반드시 review하고 불필요한 computed/default argument를 정리합니다.

한 remote object를 동시에 두 address로 import하면 Terraform이 서로 독립 객체로 오해해 예측 불가능한 plan을 만들 수 있습니다. Import ID format은 resource type마다 다르므로 provider registry documentation을 확인합니다.

## State inspection을 질문으로 사용하기

명령을 외우는 대신 어떤 질문에 답하는지 연결합니다.

| 질문 | 명령 |
|---|---|
| 현재 관리 address는 무엇인가? | `terraform state list` |
| 이 address에 기록된 attribute는 무엇인가? | `terraform state show ADDRESS` |
| Saved plan의 전체 action은 무엇인가? | `terraform show PLANFILE` |
| Root output을 script에서 사용할 수 있는가? | `terraform output -json` |
| 어떤 provider requirement가 어디서 왔는가? | `terraform providers` |

`state show`는 provider state representation을 보여주며 configuration source를 출력하는 명령이 아닙니다. Sensitive data가 terminal이나 CI log에 나타날 수 있어 output handling을 통제합니다. Bracket/key가 포함된 address는 shell globbing을 피하도록 quote합니다.

## 안전한 refactoring과 replacement

Resource label/module path를 바꿀 때 `moved` block을 사용하면 binding 이동이 plan에 나타나고 team과 module consumer에게 migration history를 제공합니다. 더 이상 관리하지 않지만 remote object는 유지하려면 `removed` block의 lifecycle에서 `destroy = false`를 선택할 수 있습니다.

실제 object가 비정상이고 replacement가 필요하면 configuration을 왜곡하거나 `taint`에 의존하기보다 `terraform plan -replace=ADDRESS` 또는 `apply -replace=ADDRESS`로 one-operation replacement intent를 review합니다. Replacement는 downtime, quota, unique name constraint를 함께 검토해야 합니다.

## Deprecated refresh command와 review 가능한 대안

Standalone `terraform refresh`는 deprecated입니다. 이 명령은 사실상 refresh-only apply를 자동 승인하는 workflow라서 remote read 결과가 어떤 state/output 변경을 만드는지 별도 plan review 없이 기록할 수 있습니다.

현대적인 절차는 두 단계입니다.

```bash
terraform plan -refresh-only -out=refresh.tfplan
terraform show refresh.tfplan
terraform apply refresh.tfplan
```

Refresh-only는 remote infrastructure를 configuration으로 되돌리지 않습니다. Provider가 관찰한 out-of-band 변경을 state와 root output에 채택합니다. Configuration이 remote reality와 계속 다르면 이후 normal plan이 다시 update 또는 replacement를 제안할 수 있습니다.

| Intent | Correct workflow |
|---|---|
| Drift를 확인만 함 | Normal plan 또는 `plan -refresh-only` 검토 |
| Remote 변경을 state에 채택 | Reviewed `apply -refresh-only` 또는 saved refresh-only plan apply |
| Configuration대로 remote를 복구 | Normal plan/apply |
| 특정 object를 교체 | Reviewed `-replace=ADDRESS` plan/apply |

`-refresh=false`로 provider read를 끄는 것도 일반적인 drift 해결책이 아닙니다. 제한된 troubleshooting/automation 이유가 없다면 stale state를 기반으로 plan할 위험이 있으므로 기본 refresh behavior를 유지합니다.

## Logging 계층과 최소 노출

`TF_LOG`는 `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `OFF` 등의 level을 사용합니다. 가장 상세한 level부터 켜는 대신 diagnostic이 어느 계층인지 먼저 좁힙니다.

- Core evaluation/graph 문제: `TF_LOG=DEBUG` 또는 제한적 `TRACE`
- Provider-specific 문제: `TF_LOG_PROVIDER` 지원 여부와 provider logs 확인
- Backend 문제: backend auth/network와 relevant log scope 확인
- 지속 파일: `TF_LOG_PATH`, 단 logging이 활성화돼야 기록됨

```bash
TF_LOG=DEBUG TF_LOG_PATH=./terraform-debug.log terraform plan
```

Log는 credential, HTTP payload, resource attribute를 포함할 수 있습니다. 최소 시간과 최소 verbosity로 수집하고 access를 제한하며 issue/채팅에 원본을 그대로 첨부하지 않습니다. 재현 후 environment variable을 해제하고 안전하게 폐기합니다.

## 진단을 ownership으로 분류

### Core/configuration

Syntax, invalid reference, type mismatch는 `fmt`, `validate`, expression과 module contract를 확인합니다. Unknown value는 apply 전 정상일 수 있으므로 error message와 phase를 함께 읽습니다.

### Provider/API

Credential chain, permission, region/endpoint, quota, eventual consistency, provider version/schema를 확인합니다. `validate` 성공이 remote permission을 보장하지 않습니다.

### Backend/state

Backend credential, network, lock owner, object versioning, state lineage를 확인합니다. Lock error를 `-lock=false`로 우회하지 않습니다.

### Module/dependency

Source/version constraint, `init` 실행, input type, output availability, provider mapping을 확인합니다. Module source 변경 뒤 plan만 반복해도 package가 자동 update되지 않을 수 있습니다.

## Maintain 작업 전후 checklist

### Before

- [ ] Disposable 또는 approved workspace인지 확인
- [ ] State backend versioning/backup과 lock 상태 확인
- [ ] Current plan과 remote ownership 확인
- [ ] Address와 import ID를 quote해 기록
- [ ] Cleanup/rollback이 아니라 recovery path를 정의

### After

- [ ] Normal plan에서 의도한 action만 남는지 확인
- [ ] Configuration과 state binding이 같은 ownership을 표현하는지 확인
- [ ] Temporary plan, state backup, debug log를 안전하게 처리
- [ ] Import/move/remove 이유를 version control에 기록

## 시험 함정과 self-check

- Import는 resource configuration을 항상 자동 완성하지 않습니다.
- `state list/show`는 inspection이고 `state rm/mv/import`는 binding mutation입니다.
- `fmt`는 remote drift나 state corruption을 해결하지 않습니다.
- `TF_LOG=TRACE`는 가장 상세하지만 항상 첫 진단 단계가 아닙니다.
- Plan no-op은 configuration/state/remote가 현재 run context에서 일치한다는 뜻이지 미래 drift가 불가능하다는 뜻이 아닙니다.

다음을 답할 수 있어야 합니다.

1. Import 뒤 immediate normal plan이 필요한 이유는 무엇인가?
2. `state rm`과 `removed { lifecycle { destroy = false } }`의 auditability 차이는 무엇인가?
3. `state show` 결과와 source configuration이 다른 이유는 무엇인가?
4. Provider permission error와 backend permission error를 어떻게 구분하는가?
5. Debug log를 secret으로 취급해야 하는 구체적 이유는 무엇인가?

## 다음 연결 / Why next

로컬 운영 패턴을 팀과 원격 실행으로 확장하면 [HCP Terraform](/domains/08-hcp-terraform/)의 workspace, project, policy가 필요합니다.

**Official sources:** [Import](https://developer.hashicorp.com/terraform/language/v1.12.x/import), [State command](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/state), [Deprecated refresh command](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/refresh), [Debugging](https://developer.hashicorp.com/terraform/internals/v1.12.x/debugging)<br />
**Lab:** [Lab 10 State operations](/labs/10-state-operations/)<br />
**Questions:** [Domain 7 bank](/archive/practice-exams/domain-7-maintain/)
