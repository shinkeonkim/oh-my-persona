---
title: "Variable Sets & Run Triggers 상세"
description: "Legacy study material imported from 08-hcp-terraform/variables-triggers.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 학습 목표

- Workspace Variables 관리
- Variable Sets 로 공유 변수 관리
- Run Triggers 로 Workspace 간 자동화
- Variable Precedence 이해
- Notification 설정

---

## 1. Workspace Variables

### 2가지 유형

**Terraform Variables:**
- `var.xxx` 로 참조
- HCL 값 (complex types 지원)

**Environment Variables:**
- `AWS_ACCESS_KEY_ID` 등
- 실행 환경 변수

### 설정 (UI)

**Workspace → Variables → Add variable**

```
Category: Terraform | Environment
Key: instance_type
Value: t3.large
HCL: [ ] (기본 문자열)
Sensitive: [ ]
```

### HCL 값

```
Category: Terraform
Key: subnets
Value: ["10.0.1.0/24", "10.0.2.0/24"]
HCL: [✓]
```

### Sensitive Variables

```
Sensitive: [✓]
```

- UI 에 표시 안 됨
- Log 마스킹
- 저장 시 암호화
- API 로도 조회 불가

---

## 2. Variable Sets

### 목적

**여러 Workspace 에서 공유되는 변수 집합.**

### 사용 사례

**AWS Credentials:**
```
Variable Set: AWS Prod Credentials
├── AWS_ACCESS_KEY_ID (env, sensitive)
├── AWS_SECRET_ACCESS_KEY (env, sensitive)
└── AWS_DEFAULT_REGION (env)

Applied to:
├── prod-app-workspace
├── prod-db-workspace
└── prod-network-workspace
```

**Common Tags:**
```
Variable Set: Common Tags
└── common_tags (terraform, HCL)
    = { Environment = "prod", ManagedBy = "Terraform" }
```

### 생성 (UI)

**Settings → Variable Sets → Create**

```
Name: AWS Production Credentials
Scope:
  ○ Global (모든 workspace)
  ○ Specific Projects
  ● Specific Workspaces
  
Variables:
  - AWS_ACCESS_KEY_ID (env, sensitive)
  - AWS_SECRET_ACCESS_KEY (env, sensitive)
```

### Scope

**Global:** Organization 의 모든 workspace 에 적용.

**Project:** 특정 Project 의 모든 workspace 에 적용.

**Workspace:** 선택한 workspace 만.

---

## 3. Variable Precedence (HCP Terraform)

### 우선순위 (높음 → 낮음)

```
1. Command line -var / -var-file
2. Workspace variables (workspace 자체 설정)
3. Variable Sets (Workspace scope)
4. Variable Sets (Project scope)
5. Variable Sets (Global scope)
6. *.auto.tfvars
7. terraform.tfvars
8. Environment variables (TF_VAR_*)
9. Default 값
```

### 실전 예제

```
Variable "region"
├── Global Variable Set: "us-east-1"
├── Project Variable Set: "us-west-2"      ← 이것이 우선
└── Workspace Variable: (없음)

결과: "us-west-2"
```

---

## 4. Run Triggers

### 목적

**한 Workspace 의 apply 성공 시 다른 Workspace 를 자동 실행.**

### 시나리오

```
network-workspace (VPC 생성)
   ↓ Apply 성공
app-workspace (VPC 사용) → 자동 Plan
```

### 설정 (UI)

**Destination Workspace → Settings → Run Triggers**

```
Add Source Workspace:
├── network-workspace
└── Save
```

**동작:**
```
network-workspace 에서 apply 완료
  ↓
app-workspace 에서 자동 Plan 시작
```

### 여러 Source

```
network-workspace ─┐
security-workspace ─┼─→ app-workspace (자동 plan)
dns-workspace ──────┘
```

### 실전 시나리오

```
base-network
  ├─ Run Trigger → web-tier
  ├─ Run Trigger → app-tier
  └─ Run Trigger → data-tier
```

Network 변경 → 모든 하위 workspace 재계획.

### 주의사항

- **자동 Plan** 만 트리거 (Apply 는 수동/자동 설정에 따름)
- Source 순서 보장 안 됨
- Circular dependency 방지

---

## 5. Notification Configuration

### 지원 채널

- **Slack**
- **Microsoft Teams**
- **Email**
- **Custom Webhook** (Generic HTTP)

### 설정

**Workspace → Settings → Notifications → Create**

```
Destination Type: Slack
Name: prod-alerts
Webhook URL: https://hooks.slack.com/services/...
Triggers:
  [✓] Runs planning
  [✓] Runs needs attention
  [✓] Runs applying
  [✓] Runs completed
  [✓] Runs errored
```

### Slack 알림 예시

```
🔵 Run needs attention
Workspace: prod-app
Trigger: VCS webhook
Author: alice@example.com

Plan: 3 to add, 1 to change, 0 to destroy

View: https://app.terraform.io/...
Actions: Approve | Discard
```

---

## 6. Terraform Cloud Agent Pools

### 목적

**Private network 리소스** 관리 (VPN 없이).

### 동작

```
HCP Terraform (Cloud)
   ↓ Job 전송
Agent (자체 인프라)
   ↓ Terraform 실행 (private network 접근)
   ↓ 결과 전송
HCP Terraform (Cloud)
```

### 설정

**1. Agent Pool 생성**
```
Settings → Agents → Create Agent Pool
Name: on-premise-agents
```

**2. Agent Token 생성**
```
Add Token → Copy token
```

**3. Agent 설치 (자체 서버)**
```bash
docker run -d \
  -e TFC_AGENT_TOKEN=<TOKEN> \
  -e TFC_AGENT_NAME=agent-1 \
  hashicorp/tfc-agent:latest
```

**4. Workspace Execution Mode**
```
Execution Mode: Agent
Agent Pool: on-premise-agents
```

---

## 7. 실전 시나리오

### 시나리오 1: Multi-tier 배포 자동화

```
Organization: my-company

Project: Production Infrastructure
├── network-prod
│   └── VCS: my-org/network-config, main branch
├── compute-prod
│   ├── VCS: my-org/compute-config, main branch
│   └── Run Trigger: network-prod
└── database-prod
    ├── VCS: my-org/database-config, main branch
    └── Run Trigger: network-prod

Variable Set: AWS Credentials
└── Scope: Project (Production Infrastructure)
```

**동작:**
1. network-prod PR merge
2. network-prod 자동 plan → apply
3. compute-prod, database-prod 자동 plan (Run Trigger)
4. 팀 리뷰 후 apply

### 시나리오 2: 환경별 Variable Sets

```
Variable Set 1: Common Config (Global)
├── common_tags
└── organization

Variable Set 2: Prod Credentials (Project: Prod)
├── AWS_ACCESS_KEY_ID (sensitive)
└── AWS_SECRET_ACCESS_KEY (sensitive)

Variable Set 3: Dev Credentials (Project: Dev)
├── AWS_ACCESS_KEY_ID (sensitive)
└── AWS_SECRET_ACCESS_KEY (sensitive)

Workspaces:
├── app-prod (Variable Set 1 + 2 자동 적용)
└── app-dev (Variable Set 1 + 3 자동 적용)
```

### 시나리오 3: 알림 파이프라인

```
Workspace: prod-app

Notifications:
├── Slack #prod-alerts (모든 이벤트)
├── Slack #on-call (needs-attention, errored)
└── Webhook to PagerDuty (errored)
```

---

## 8. Best Practices

### ✅ DO

- **Sensitive variables 항상 Sensitive 체크**
- **Variable Sets 로 중복 제거**
- **AWS Credentials 는 Variable Set 으로**
- **Run Triggers 로 종속성 자동화**
- **Notification 으로 실패 조기 감지**

### ❌ DON'T

- 각 workspace 에 credentials 중복 저장
- Circular Run Trigger
- Sensitive 없이 secrets 저장
- 무단 Global Variable Set

---

## 9. 시험 자주 나오는 함정

### 함정 1: Variable Sets Scope

```
Q: Variable Set 은 어떤 scope 를 지원?
A: Global, Project, Workspace (3가지).
```

### 함정 2: Run Triggers 방향

```
Q: Run Trigger 는 어디에서 설정?
A: Destination workspace 에서 source 를 지정.
```

### 함정 3: Run Trigger 는 무엇을 실행?

```
Q: Source apply 후 destination 은 자동 apply?
A: ❌ NO. 자동 Plan 만. Apply 는 destination workspace 설정에 따름.
```

### 함정 4: Sensitive Variable

```
Q: Sensitive variable 값을 UI 에서 다시 볼 수 있나요?
A: ❌ NO. 한번 저장 후 조회 불가. 재입력 필요.
```

---

## 참고 자료

- [Variable Sets](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/variables)
- [Run Triggers](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-triggers)
- [Notifications](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/notifications)
- [Agents](https://developer.hashicorp.com/terraform/cloud-docs/agents)
- 관련: [Workspaces & Projects](/archive/08-hcp-terraform/workspaces-projects/), [Policy](/archive/08-hcp-terraform/policy/)
