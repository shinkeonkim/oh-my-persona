# 21 · Architecture (아키텍처 패턴 · DR · Well-Architected) 학습 노트

> 대상: SAA-C03 · 기반: `21-architecture/` 89개 문제 전수 분석 + `notes/` 참조 자료
> 이 카테고리는 전체 문제 은행(~1,300+)에서 **대형 카테고리(89문제, ~6.8%)**이며, Domain 2(복원력 26%)의 핵심이자 **모든 도메인을 관통하는 통합 아키텍처 관점**의 문제들입니다.

---

## 1. 카테고리 개요

| 항목 | 값 |
|---|---|
| 문제 수 | **89개** (22개 카테고리 중 상위 5위) |
| 주요 도메인 | D2 (복원력 26%) · D3 (고성능 24%) · D4 (비용 최적화 20%) |
| 핵심 주제 | Well-Architected Framework, DR 4전략, 3계층 아키텍처, 서버리스, 마이크로서비스, 디커플링, Multi-AZ/Region |
| 빈출 서비스 | `ALB + ASG`, `Aurora`, `DynamoDB`, `Lambda`, `SQS/SNS`, `Route 53`, `CloudFront`, `AWS Backup`, `ECS Fargate` |
| 체감 중요도 | ★★★★★ — 개별 서비스 지식을 **아키텍처로 조합**하는 능력을 직접 평가 |

> **왜 중요한가?** SAA-C03은 "이 서비스가 무엇인가"보다 **"제약 조건 하에서 어느 조합이 최선인가"**를 묻습니다. 이 카테고리가 바로 그 조합 능력을 테스트하는 핵심입니다. HA · DR · 확장성 · 비용 최적화 · 보안을 **동시에** 만족하는 아키텍처를 선택해야 합니다.

---

## 2. 핵심 개념 한줄 요약

| 개념 | 한줄 요약 |
|---|---|
| **Well-Architected Framework** | AWS 아키텍처 설계의 6대 기둥 — 운영 우수성 · 보안 · 안정성 · 성능 효율성 · 비용 최적화 · 지속 가능성 |
| **RTO (Recovery Time Objective)** | 재해 후 **복구까지 허용되는 최대 시간** — "얼마나 빨리 복구?" |
| **RPO (Recovery Point Objective)** | 재해 시 **허용되는 최대 데이터 손실 시간** — "얼마나 많은 데이터를 잃을 수 있는가?" |
| **DR 4전략** | Backup & Restore → Pilot Light → Warm Standby → Multi-Site Active/Active (비용·RTO 반비례) |
| **3-Tier Architecture** | Web(Public) → App(Private) → DB(Private) 계층 분리 + 각 계층 Multi-AZ |
| **서버리스 (Serverless)** | CloudFront + S3 + API Gateway + Lambda + DynamoDB + Cognito — 유휴 시 비용 0 |
| **마이크로서비스** | 독립 배포·확장 가능한 작은 서비스 단위 — SQS/SNS/EventBridge로 디커플링 |
| **이벤트 기반 (Event-driven)** | S3 이벤트 → Lambda, DynamoDB Streams → Lambda, EventBridge 규칙 → 대상 |
| **Multi-AZ** | AZ 장애 대비 — 같은 리전 내 가용 영역 간 자동 장애 조치 |
| **Multi-Region** | 리전 장애 대비 — Aurora Global, DynamoDB Global Tables, Route 53 Failover |
| **HA (High Availability)** | 최소 다운타임 — Multi-AZ + ALB + ASG |
| **Fault Tolerance** | 다운타임 없음 — 중복 + 자동 페일오버 |
| **디커플링 (Decoupling)** | 구성 요소 간 느슨한 결합 — SQS 버퍼, SNS 팬아웃, EventBridge 라우팅 |
| **CQRS** | Command(쓰기)와 Query(읽기) 경로 분리 — 쓰기 DB + Read Replica/캐시 |

---

## 3. 출제 패턴 분석

### 3.1 문제 유형 분포

89개 문제를 분류하면 다음과 같은 분포를 보입니다:

| 유형 | 비중 | 대표 키워드 |
|---|---|---|
| **고가용성 · Multi-AZ** (ALB + ASG + RDS Multi-AZ) | ~25% | "고가용성", "단일 장애 지점", "AZ 장애 대비" |
| **DR · Multi-Region** (Aurora Global, Route 53 Failover) | ~20% | "재해 복구", "리전 장애", "RTO/RPO" |
| **서버리스 아키텍처** (Lambda + API GW + DynamoDB) | ~18% | "서버리스", "유휴 시간 비용", "운영 오버헤드 최소" |
| **디커플링 · 확장성** (SQS + ASG, SNS, EventBridge) | ~15% | "느슨한 결합", "요청량 급증", "독립 확장" |
| **비용 최적화 아키텍처** (RI, Spot, Savings Plan, 스토리지 계층화) | ~12% | "가장 비용 효율적", "24/7 실행", "간헐적" |
| **백업 · 규정 준수** (AWS Backup, Vault Lock) | ~10% | "장기 보관", "변조 방지", "교차 리전 복사" |

### 3.2 19대 시나리오 패턴

| # | 시나리오 신호 | 정답 방향 | 빈도 |
|---|---|---|---|
| 1 | "AZ 장애 대비 · 자동 페일오버" | **Multi-AZ**: RDS Multi-AZ + ALB + ASG (여러 AZ) | ★★★★★ |
| 2 | "리전 장애 대비 · RTO 수 분" | **Aurora Global Database** + Route 53 Failover + DR 리전 인프라 | ★★★★★ |
| 3 | "RTO 수 시간 + 비용 최저" | **Backup & Restore**: AWS Backup + CloudFormation | ★★★★☆ |
| 4 | "RTO 수십 분 + 핵심 DB만 복제" | **Pilot Light**: Aurora Global + DR 리전 최소 인프라 (중지 상태) | ★★★★☆ |
| 5 | "RTO 수 분 + DR 리전 축소 가동" | **Warm Standby**: Aurora Global + DR 리전 축소 ASG | ★★★★★ |
| 6 | "RTO 거의 0 + 양 리전 완전 가동" | **Multi-Site Active/Active**: DynamoDB Global Tables + Route 53 | ★★★☆☆ |
| 7 | "3계층 웹앱 (Web/App/DB)" | Public: ALB → Private: EC2/ECS ASG → DB Subnet: RDS Multi-AZ | ★★★★★ |
| 8 | "마이크로서비스 통신 디커플링" | **SQS** (순서 필요시 FIFO) / **SNS** (팬아웃) / **EventBridge** | ★★★★☆ |
| 9 | "이벤트 기반 아키텍처" | S3 이벤트 → Lambda / DynamoDB Streams → Lambda / EventBridge | ★★★★☆ |
| 10 | "완전 서버리스 웹앱" | CloudFront + S3 + API Gateway + Lambda + DynamoDB + Cognito | ★★★★★ |
| 11 | "요청량 급증 흡수 · 주문 유실 방지" | **SQS 버퍼** + ASG (큐 깊이 기반 스케일링) | ★★★★★ |
| 12 | "글로벌 성능 최적화" | **CloudFront** (캐싱) + **Global Accelerator** (비HTTP) | ★★★★☆ |
| 13 | "고비용 EC2 대체 · 운영 부담 최소" | 서버리스: Lambda / Fargate + API Gateway | ★★★★☆ |
| 14 | "레거시 앱 최소 코드로 클라우드로" | Rehost (EC2 + RDS, 코드 변경 최소) → 단계적 Refactor | ★★★☆☆ |
| 15 | "매일 스냅샷 자동 백업 + 크로스 리전" | **AWS Backup** with Backup Plan + 교차 리전 복사 규칙 | ★★★★★ |
| 16 | "변조 방지 · WORM 백업" | AWS Backup **Vault Lock** — **규정 준수 모드** (Compliance Mode) | ★★★★☆ |
| 17 | "여러 리전 데이터 일관성" | **DynamoDB Global Tables** (multi-active) / **Aurora Global** (1초 미만 lag) | ★★★★☆ |
| 18 | "예측 불가 트래픽 + 장기 유휴" | 서버리스 (Lambda + API GW) — 사용량 기반 과금 | ★★★★☆ |
| 19 | "ActiveMQ/RabbitMQ 마이그레이션 + HA" | **Amazon MQ** 활성/대기 브로커 (Multi-AZ) | ★★★☆☆ |

---

## 4. 심층 노트

### 4.1 Well-Architected Framework 6 필러

| 필러 | 핵심 원칙 | 시험 신호어 | 대표 서비스/기능 |
|---|---|---|---|
| **운영 우수성** | 운영을 코드로 자동화 | "운영 부담 최소화", "관리형", "자동화" | CloudFormation, Systems Manager, 서버리스 |
| **보안** | 최소 권한 + 심층 방어 + 암호화 | "최소 권한", "암호화", "감사" | IAM, KMS, WAF, SG, NACL |
| **안정성 (Reliability)** | 자동 복구 + 확장 + 백업 | "고가용성", "내결함성", "Multi-AZ", "RTO/RPO" | Multi-AZ, ASG, AWS Backup |
| **성능 효율성** | 적정 리소스 + 서버리스 + 캐싱 | "지연 시간", "처리량", "확장" | CloudFront, ElastiCache, DAX, Lambda |
| **비용 최적화** | 필요한 만큼만 + 우측 사이징 | "가장 비용 효율적", "최소 비용" | RI, Savings Plans, Spot, S3 수명 주기 |
| **지속 가능성** | 리소스 활용률 극대화 | "리소스 활용률" | Graviton, 서버리스, 자동 스케일링 |

> **시험 핵심 감각**: 보기 4개 중 2개는 명백히 틀리고, 남은 2개는 **둘 다 동작하지만 하나가 더 저렴/더 관리형/더 낮은 지연**입니다. 문제의 **제약 조건 2개**를 모두 만족하는 것이 정답입니다.

> **6 필러 빈출 조합**: 문제에서 제약 조건이 2개 이상일 때 필러 간 충돌이 발생합니다:
>
> | 제약 조합 | 우선 후보 |
> |---|---|
> | "고가용성" + "비용 효율적" | Multi-AZ이지만 최소 규모 (Aurora Serverless v2) |
> | "저지연" + "글로벌" | CloudFront + Global Accelerator |
> | "보안" + "운영 최소" | 관리형 서비스 (RDS, Fargate) + IAM 역할 |
> | "확장성" + "코드 변경 최소" | EC2 ASG + RDS (프로토콜 호환) |
> | "비용 최저" + "장기 보관" | S3 Glacier Deep Archive + AWS Backup 콜드 스토리지 |

---

### 4.2 DR 4전략 (RTO/RPO 비교)

| 전략 | RTO | RPO | 비용 | 특징 | AWS 서비스 |
|---|---|---|---|---|---|
| **Backup & Restore** | 수 시간 | 수 시간 (마지막 백업) | 💰 최저 | 백업만 보관, 장애 시 인프라 재구축 | AWS Backup, S3, CloudFormation |
| **Pilot Light** | 수십 분 | 분 | 💰💰 낮음 | 핵심 DB만 상시 복제, 나머지 중지 | Aurora Global, 최소 인프라 (stopped) |
| **Warm Standby** | 수 분 | 초 | 💰💰💰 중간 | 축소 규모 상시 가동, 확장 가능 | Aurora Global + 축소 ASG + ALB |
| **Multi-Site Active/Active** | 거의 0 | 거의 0 | 💰💰💰💰 최고 | 양 리전 완전 가동, 트래픽 분산 | DynamoDB Global Tables, Route 53 |

```
비용 ↑  ┌─────────────────────────┐
        │  Multi-Site Active/Active │  RTO ≈ 0
        ├─────────────────────────┤
        │     Warm Standby         │  RTO = 분
        ├─────────────────────────┤
        │     Pilot Light          │  RTO = 수십분
        ├─────────────────────────┤
        │   Backup & Restore       │  RTO = 시간
비용 ↓  └─────────────────────────┘
```

> **판별 팁**: "DR 리전에서 **축소 용량으로 실행**" → **Warm Standby**. "DB만 복제, 인프라 **중지**" → **Pilot Light**. "인프라 **없음**, 백업만" → **Backup & Restore**.

---

### 4.3 3계층 웹 애플리케이션 아키텍처

```
인터넷 → CloudFront + WAF
            ↓
    ┌── Public Subnet ──┐
    │   ALB (Multi-AZ)   │
    └────────┬───────────┘
             ↓
    ┌── Private Subnet ──┐
    │  EC2/ECS ASG        │  ← Auto Scaling (Multi-AZ)
    │  (App 계층)         │
    └────────┬───────────┘
             ↓
    ┌── DB Subnet ───────┐
    │  RDS/Aurora          │  ← Multi-AZ (자동 장애 조치)
    │  (Private, 인터넷 ✕) │
    └─────────────────────┘
```

| 계층 | 서브넷 | 핵심 구성 | 보안 |
|---|---|---|---|
| **Web / LB** | Public | ALB, NAT GW (SSM 대체 Bastion) | SG: 80/443 인바운드, WAF |
| **App** | Private | EC2/ECS/EKS + ASG | SG: ALB SG에서만 인바운드 |
| **DB** | Private (DB) | RDS/Aurora Multi-AZ | SG: App SG에서만 인바운드 |

> **핵심 포인트**:
> - 각 계층은 **별도의 보안 그룹**으로 분리 (SG 체인)
> - DB는 **반드시 Private Subnet + Multi-AZ**
> - 웹 계층은 **ALB 뒤에 ASG** (수동 인스턴스 ✕)
> - 정적 자산은 **S3 + CloudFront**로 오프로드

---

### 4.4 서버리스 아키텍처

| 구성 요소 | 서비스 | 역할 |
|---|---|---|
| **Frontend** | CloudFront + S3 (SPA) / AWS Amplify | 정적 콘텐츠 배포, CDN |
| **API** | Amazon API Gateway (REST / HTTP) | RESTful API, 인증, 스로틀링, API 키 |
| **Compute** | AWS Lambda | 비즈니스 로직, 이벤트 처리 |
| **DB** | Amazon DynamoDB | NoSQL, 자동 확장, 한 자릿수 ms 응답 |
| **Auth** | Amazon Cognito (User Pool) | 사용자 인증 (가입/로그인/MFA) |
| **Messaging** | SQS / SNS / EventBridge | 비동기 처리, 디커플링 |
| **Orchestration** | AWS Step Functions | 복잡한 워크플로 조정, 수동 승인 |
| **Storage** | Amazon S3 | 파일/이미지 저장 |

**서버리스 특징**:
- ✅ 자동 스케일 (요청에 비례)
- ✅ 유휴 시 비용 0 (또는 매우 낮음)
- ✅ 관리 부담 최소 (OS 패치, 용량 계획 불필요)
- ⚠️ Lambda 최대 실행 시간 **15분** (초과 시 Fargate/Batch 사용)
- ⚠️ Lambda 콜드 스타트 (VPC 내 배치 시 지연)
- ⚠️ Lambda VPC 내 배치 → 인터넷 접근 끊김 (NAT GW 또는 VPC 엔드포인트 필요)

> **판별 팁**:
> - "예측 불가 트래픽 + 장기 유휴" → **서버리스** (Lambda + API GW)
> - "처리 시간 > 15분" → **ECS Fargate** 또는 **AWS Batch**
> - "PHP/Java 모놀리스" → EC2 또는 ECS 컨테이너 (Lambda ✕)

---

### 4.5 마이크로서비스 & 이벤트 기반 아키텍처

| 패턴 | 설명 | AWS 서비스 |
|---|---|---|
| **API Gateway per Service** | 각 마이크로서비스에 독립 API 엔드포인트 | API Gateway + Lambda |
| **Service Discovery** | 서비스 위치 동적 검색 | AWS Cloud Map |
| **Event Bus** | 이벤트 기반 라우팅 (규칙 매칭) | Amazon EventBridge |
| **SNS Fanout** | 하나의 메시지를 여러 구독자에게 동시 전달 | SNS → SQS, Lambda, HTTP |
| **Message Queue** | 순서 보장 + 버퍼링 + 디커플링 | SQS (Standard / FIFO) |
| **Choreography** | 이벤트로 서비스 간 조정 (탈중앙) | EventBridge, SNS |
| **Orchestration** | 중앙 워크플로 엔진이 순서 조정 | AWS Step Functions |
| **Saga Pattern** | 분산 트랜잭션 보상 처리 | Step Functions + Lambda |
| **CQRS** | 쓰기/읽기 경로 분리 | 쓰기: RDS → 읽기: Read Replica / ElastiCache |

> **"프로세스가 특정 순서로 실행"** → **SQS FIFO** 또는 **Step Functions**
> **"구성 요소 독립 발전"** → **SQS/SNS 디커플링** + 마이크로서비스

---

### 4.6 확장성 · 탄력성 (Scalability & Elasticity)

| 확장 유형 | 설명 | 서비스 예시 |
|---|---|---|
| **수직 확장 (Scale Up)** | 더 큰 인스턴스로 변경 — 다운타임 발생, 한계 있음 | EC2 인스턴스 유형 변경 |
| **수평 확장 (Scale Out)** | 인스턴스 추가 — 다운타임 없음, 무한 확장 | **EC2 ASG**, ECS 서비스 Auto Scaling |
| **서버리스 자동 확장** | 요청에 비례하여 자동 | **Lambda**, **DynamoDB On-Demand**, **Aurora Serverless v2** |
| **캐싱 오리진 부하 감소** | 반복 요청 캐시로 처리 | **CloudFront**, **ElastiCache**, **DAX** |

| 서비스 | 확장 방식 |
|---|---|
| **EC2 ASG** | CPU/네트워크/SQS 큐 깊이 기반 정책 |
| **ECS (Fargate)** | 태스크 수 자동 조정 |
| **Aurora Serverless v2** | ACU 단위 초 단위 스케일 (0.5~128 ACU) |
| **DynamoDB** | 온디맨드 또는 Auto Scaling (RCU/WCU) |
| **Lambda** | 동시 실행 자동 확장 (계정 제한까지) |

> **"원활하게 확장해야 한다"** → **수평 확장 (ASG)** — 수직 확장은 다운타임 발생으로 오답

---

### 4.7 고가용성 (HA) vs 내결함성 (FT) vs 재해 복구 (DR)

| 개념 | 목표 | 범위 | 대표 서비스 |
|---|---|---|---|
| **HA (High Availability)** | 최소 다운타임 | **AZ 내/간** | Multi-AZ RDS, ALB + ASG (여러 AZ) |
| **FT (Fault Tolerance)** | 다운타임 **없음** | AZ 내/간 | S3 (11 9s 내구성), DynamoDB (3 AZ 자동 복제) |
| **DR (Disaster Recovery)** | 재해 후 **복구** | **리전 간** | Aurora Global, S3 CRR, Route 53 Failover |

> ⚠️ **HA ≠ DR**: HA는 AZ 수준, DR은 리전 수준. Multi-AZ RDS는 HA이지 DR이 아닙니다.

---

### 4.8 Multi-AZ vs Multi-Region

| 항목 | Multi-AZ | Multi-Region |
|---|---|---|
| **대비 대상** | AZ 장애 (전력, 네트워크) | 리전 전체 장애, 글로벌 사용자 |
| **지연 시간** | 낮음 (같은 리전, 밀리초) | 높음 (리전 간, 수십~수백 ms) |
| **비용** | 상대적으로 낮음 | 높음 (추가 리전 인프라) |
| **데이터 복제** | 동기식 (RDS Multi-AZ) | 비동기식 (Aurora Global ~1초) |
| **대표 서비스** | RDS Multi-AZ, ALB + ASG | Aurora Global, DynamoDB Global Tables, S3 CRR |
| **라우팅** | ALB가 AZ 간 자동 분산 | Route 53 Failover / Latency-based |

---

### 4.9 디커플링 (Decoupling) 패턴

| 패턴 | 서비스 | 특징 | 사용 시나리오 |
|---|---|---|---|
| **Message Queue** | **SQS** | Pull 모델, 메시지 버퍼링, 순서 보장 (FIFO) | 프론트-백엔드 분리, 부하 흡수 |
| **Pub/Sub** | **SNS** | Push 모델, 팬아웃 (여러 구독자) | 알림, 이벤트 브로드캐스트 |
| **Event Bus** | **EventBridge** | 규칙 기반 라우팅, 스키마 검증 | 이벤트 기반 아키텍처, SaaS 통합 |
| **Streaming** | **Kinesis Data Streams** | 실시간 대용량 스트림, 순서 보장 | 실시간 분석, IoT 데이터 |
| **Workflow** | **Step Functions** | 시각적 워크플로, 상태 관리, 수동 승인 | 복잡한 비즈니스 프로세스 |

> **판별 팁**:
> - "요청량 급증 흡수" → **SQS** + ASG (큐 깊이 기반 스케일링)
> - "여러 서비스에 동시 전달" → **SNS 팬아웃** → 각 SQS 큐
> - "이벤트 기반 규칙 라우팅" → **EventBridge**
> - "실시간 스트리밍" → **Kinesis**
> - "순서가 있는 복잡한 워크플로" → **Step Functions**

---

### 4.10 Route 53 라우팅 정책 활용

| 정책 | 용도 | DR/HA 활용 |
|---|---|---|
| **Failover** | Active-Passive | DR: 기본 리전 장애 → 보조 리전 자동 전환 |
| **Weighted** | 비율 기반 분배 | Blue/Green 배포, Canary 배포 |
| **Latency** | 최저 지연 리전 | 글로벌 사용자 → 가장 가까운 리전 |
| **Geolocation** | 사용자 위치 기반 | 규정 준수 (데이터 주권), 언어별 콘텐츠 |
| **Geoproximity** | 리전 트래픽 비율 조절 (bias) | 특정 리전으로 점진적 트래픽 이동 |
| **Multivalue Answer** | 다중 응답 + 헬스체크 | 간이 부하 분산 (ALB 대체 ✕) |
| **Simple** | 단일 레코드 | 헬스체크 미지원 — DR 오답 |

> ⚠️ **Route 53 Simple 라우팅은 상태 확인/장애 조치를 지원하지 않습니다** — DR에서 사용 시 오답

---

### 4.11 API 통합 패턴

| 패턴 | 구성 | 특징 | 적합한 워크로드 |
|---|---|---|---|
| **서버리스 3종** | API Gateway + Lambda + DynamoDB | 완전 서버리스, 유휴 비용 0 | 간헐적, 예측 불가 트래픽 |
| **컨테이너 기반** | ALB + ECS Fargate + Aurora | 서버리스 컨테이너, 15분 초과 작업 가능 | 장기 실행, 복잡한 앱 |
| **EC2 기반** | ALB + EC2 ASG + RDS | 전통적 아키텍처, 유연한 OS 제어 | 레거시, 커스텀 런타임 |

> **판별 팁**:
> - "API 키 + 사용 계획 + 스로틀링" → **API Gateway REST API** (HTTP API는 API 키 미지원)
> - "WAF 연결" → **ALB** 또는 **CloudFront** 또는 **API Gateway** (NLB는 WAF 미지원)

---

### 4.12 하이브리드 아키텍처

| 서비스 | 용도 |
|---|---|
| **Direct Connect** | 전용 네트워크 연결 (10Gbps), 일관된 지연 시간 |
| **Site-to-Site VPN** | DX 백업, 또는 단독 사용 (인터넷 경유, 암호화) |
| **Storage Gateway** | 온프렘 앱 → AWS 스토리지 (S3, EBS, Tape) |
| **AWS Outposts** | 온프렘에 AWS 하드웨어 설치 (로컬 컴퓨팅/스토리지) |
| **Wavelength** | 5G 엣지 컴퓨팅 (초저지연) |
| **Local Zones** | 도시 근처 AWS 인프라 (저지연) |

---

### 4.13 AWS Backup 전략 심화

89개 문제 중 **약 10%가 AWS Backup 관련**으로, 이 서비스의 중요성이 매우 높습니다.

#### 4.13.1 AWS Backup 핵심 기능

| 기능 | 설명 |
|---|---|
| **백업 계획 (Backup Plan)** | 일정 + 보존 기간 + 수명 주기 (콜드 스토리지 전환) 정의 |
| **백업 볼트 (Backup Vault)** | 백업 저장소, Vault Lock으로 삭제 방지 |
| **교차 리전 복사** | 백업 규칙에 복사 대상 리전 지정 → 자동 복제 |
| **교차 계정 백업** | AWS Organizations 통합, 중앙 관리 계정에서 백업 |
| **태그 기반 리소스 할당** | 태그로 백업 대상 자동 식별 (수백 개 리소스도 자동) |
| **지원 서비스** | EC2, EBS, RDS, Aurora, DynamoDB, EFS, FSx, S3 등 |

#### 4.13.2 AWS Backup vs 대안 비교

| 항목 | AWS Backup | DLM (Data Lifecycle Manager) | 수동 스크립트 (Lambda) |
|---|---|---|---|
| **EC2/EBS** | ✅ | ✅ | ✅ |
| **RDS/Aurora** | ✅ | ✕ | ✅ (복잡) |
| **DynamoDB** | ✅ | ✕ | ✅ (복잡) |
| **EFS** | ✅ | ✕ | ✕ |
| **S3** | ✅ | ✕ | ✅ |
| **교차 리전 복사** | ✅ (네이티브) | ✅ (EBS만) | ✅ (수동) |
| **콜드 스토리지 전환** | ✅ | ✕ | ✕ |
| **Vault Lock (WORM)** | ✅ | ✕ | ✕ |
| **운영 오버헤드** | 최소 | 낮음 (EBS만) | 높음 |

> **판별 팁**: "여러 서비스 백업 중앙 관리" → **AWS Backup**. "EBS 스냅샷만 자동화" → DLM도 가능하지만 AWS Backup이 더 포괄적.

#### 4.13.3 Vault Lock 모드 비교

| 항목 | Governance Mode | Compliance Mode |
|---|---|---|
| **삭제 가능** | 특별 권한(루트) 있으면 가능 | **불가** (누구도, 루트 포함) |
| **잠금 해제** | 가능 | **불가** |
| **사용 사례** | 일반 보호, 관리 유연성 유지 | 규정 준수, WORM, 변조 방지 |
| **시험 키워드** | — | "변조 불가", "규정 준수", "삭제 방지" |

#### 4.13.4 DynamoDB 장기 보관 비교

| 방법 | 최대 보관 | 자동화 | 운영 오버헤드 |
|---|---|---|---|
| **PITR (Point-in-Time Recovery)** | **35일** | 자동 | 최소 |
| **온디맨드 백업** | 무제한 | **수동** | 높음 |
| **AWS Backup** | 무제한 | **자동** (일정 + 보존) | **최소** |

> ⚠️ **"7년 보관"** 문제에서 PITR은 항상 오답 (35일 한계). AWS Backup이 정답.

---

### 4.14 AWS Well-Architected Tool

| 항목 | 설명 |
|---|---|
| **목적** | 워크로드를 6대 필러 기준으로 자가 검토 |
| **워크플로** | 워크로드 등록 → 질문 응답 → 개선 계획(Improvement Plan) 생성 |
| **출력** | High Risk Issue (HRI), Medium Risk Issue (MRI) 식별 |
| **비용** | 무료 |
| **시험 포인트** | "Well-Architected Review 도구" → **AWS Well-Architected Tool** |

---

### 4.14 데이터 일관성 패턴

| 패턴 | 설명 | 서비스 |
|---|---|---|
| **Strong Consistency** | 쓰기 직후 읽기 일관성 보장 | DynamoDB (강력한 일관된 읽기), S3 (PUT 후 즉시 GET) |
| **Eventual Consistency** | 짧은 지연 후 일관성 보장 | DynamoDB (기본 읽기), Aurora Read Replica |
| **Multi-Region 복제** | 리전 간 비동기 복제 | DynamoDB Global Tables (밀리초), Aurora Global (~1초) |
| **Read Replica lag** | 읽기 복제본 지연 | RDS Read Replica (초~분), Aurora Replica (밀리초) |

> **DynamoDB Global Tables**는 **multi-active** (양쪽 읽기/쓰기 가능, 충돌 자동 해결)
> **Aurora Global Database**는 **read-only secondary** (writer 승격 시 RTO ~1분)

---

### 4.15 성능 최적화 패턴

| 패턴 | 서비스 | 효과 |
|---|---|---|
| **CDN 캐싱** | **CloudFront** | 정적/동적 콘텐츠 엣지 캐싱, 오리진 부하 감소 |
| **인메모리 캐싱** | **ElastiCache** (Redis/Memcached) | DB 쿼리 결과 캐싱, 마이크로초 응답 |
| **DynamoDB 캐싱** | **DAX** | DynamoDB 전용 캐시, 마이크로초 응답 |
| **읽기 분리** | **Read Replica** (RDS/Aurora) | 읽기 부하 오프로드 |
| **업로드 최적화** | **S3 Transfer Acceleration** | 엣지 네트워크 활용 업로드 가속 |
| **글로벌 네트워크 가속** | **Global Accelerator** | AWS 글로벌 네트워크 경유, 비HTTP 가속 |
| **파티션 키 설계** | DynamoDB Partition Key | 핫 파티션 방지, 균등 분산 |

> **CloudFront vs Global Accelerator**:
> - CloudFront: **캐싱** (정적/동적 콘텐츠 CDN)
> - Global Accelerator: **비HTTP 가속** (TCP/UDP, 게임, IoT) + Anycast IP

---

## 5. 시험 신호어 → 정답 매핑

| 신호어 | 정답 방향 |
|---|---|
| "**고가용성**" + "자동 확장" | ALB + EC2 ASG (Multi-AZ) + RDS Multi-AZ |
| "**재해 복구**" + "리전 장애" | Multi-Region: Aurora Global + Route 53 Failover |
| "**RTO 수 분**" + "축소 용량" | **Warm Standby** (DR 리전 축소 ASG) |
| "**RTO 수 시간**" + "비용 최저" | **Backup & Restore** (AWS Backup + CloudFormation) |
| "**RTO 거의 0**" + "양 리전 가동" | **Multi-Site Active/Active** |
| "**서버리스**" + "운영 오버헤드 최소" | Lambda + API Gateway + DynamoDB |
| "**유휴 시간 길고**" + "비용 효율적" | 서버리스 (사용량 기반 과금) |
| "**24/7 실행**" + "비용 효율적" | **예약 인스턴스 (RI)** 또는 **Savings Plans** |
| "**중단 불가 배치 작업**" | **EC2 On-Demand** (Spot ✕) |
| "**중단 가능 배치 작업**" | **EC2 Spot** |
| "**요청량 급증**" + "유실 방지" | **SQS 버퍼** + ASG |
| "**마이크로서비스**" + "독립 확장" | SQS/SNS 디커플링 + ECS Fargate 또는 Lambda |
| "**처리 시간 > 15분**" | **ECS Fargate** 또는 **AWS Batch** (Lambda ✕) |
| "**처리 시간 < 15분**" | **Lambda** (가장 비용 효율적) |
| "**7년 장기 보관**" + "백업" | **AWS Backup** (콜드 스토리지 전환, PITR은 35일 한계) |
| "**변조 방지**" + "규정 준수" | AWS Backup **Vault Lock Compliance Mode** |
| "**교차 리전 백업**" | AWS Backup **교차 리전 복사 규칙** |
| "**정적 콘텐츠**" + "글로벌 성능" | **CloudFront + S3** |
| "**코드 변경 최소**" + "MySQL" | **RDS for MySQL** 또는 **Aurora MySQL** (MySQL 호환) |
| "**ActiveMQ/RabbitMQ**" | **Amazon MQ** (관리형 브로커) |
| "**API 키 + 속도 제한**" | **API Gateway REST API** (HTTP API는 미지원) |
| "**WAF**" | ALB / CloudFront / API Gateway (NLB ✕) |

---

## 6. 자주 틀리는 함정

> ⚠️ **HA ≠ DR**: HA는 AZ 수준 (Multi-AZ), DR은 리전 수준 (Multi-Region). Multi-AZ RDS는 HA이지 DR이 아닙니다.

> ⚠️ **Read Replica는 HA 솔루션이 아닙니다**: 자동 페일오버가 없으며 수동 승격이 필요합니다. Multi-AZ가 HA 솔루션입니다.

> ⚠️ **Multi-AZ 대기본은 읽기 불가**: RDS Multi-AZ의 대기 인스턴스는 읽기 트래픽을 처리할 수 없습니다. (**Multi-AZ DB Cluster**는 예외 — 리더 엔드포인트 사용 가능)

> ⚠️ **Aurora Global Database는 read-only secondary**: 보조 리전은 읽기 전용입니다. writer로 승격 시 RTO ~1분, RPO ~1초.

> ⚠️ **Route 53 Failover는 primary/secondary만**: 2개 레코드 기반 Active-Passive. multi-active가 필요하면 **Weighted** 또는 **Latency** 정책 사용.

> ⚠️ **Route 53 Simple 라우팅은 헬스체크 미지원**: DR/Failover에 Simple 라우팅이 나오면 오답입니다.

> ⚠️ **"RTO 수 분 + 비용" → Pilot Light 또는 Warm Standby**: 문맥으로 구분 — "축소 용량 가동" → Warm Standby, "인프라 중지 + DB만 복제" → Pilot Light.

> ⚠️ **서버리스가 항상 정답 아닙니다**: Lambda 15분 제한, 콜드 스타트, PHP 미지원 (커스텀 런타임 필요), VPC 내 인터넷 끊김 등의 제약을 확인하세요.

> ⚠️ **Multi-Site Active/Active는 데이터 충돌 해결 필요**: DynamoDB Global Tables는 last-writer-wins로 자동 해결. Aurora Global은 read-only secondary이므로 충돌 없음.

> ⚠️ **DynamoDB PITR은 최대 35일**: 7년 장기 보관에는 **AWS Backup** 사용 (콜드 스토리지 전환 지원).

> ⚠️ **3계층 아키텍처의 DB는 반드시 Multi-AZ + Private Subnet**: DB가 Public Subnet이면 오답.

> ⚠️ **Auto Scaling 그룹은 리전 내 서비스**: 여러 리전에 걸쳐 구성할 수 없습니다. 각 리전에 별도의 ASG가 필요합니다.

> ⚠️ **EBS는 AZ를 넘지 못합니다**: 다른 AZ에서 사용하려면 스냅샷 → 새 AZ에서 복원.

> ⚠️ **Spot 인스턴스는 중단 가능 워크로드 전용**: "중단되면 안 됨" 또는 "24/7 실행" → Spot은 오답.

> ⚠️ **NLB에는 WAF를 연결할 수 없습니다**: WAF는 ALB, CloudFront, API Gateway, AppSync에만 연결 가능.

> ⚠️ **API Gateway HTTP API는 API 키를 지원하지 않습니다**: API 키 + 사용 계획이 필요하면 **REST API**.

> ⚠️ **S3 정적 웹 호스팅은 HTTPS를 지원하지 않습니다**: HTTPS가 필요하면 **CloudFront** 배포 필요.

> ⚠️ **AWS Backup Vault Lock**: **Governance Mode** — 특별 권한으로 삭제 가능. **Compliance Mode** — 누구도 삭제 불가 (WORM). "변조 불가" 요구 → **Compliance Mode**.

> ⚠️ **NAT Gateway는 웹 트래픽 관리용이 아닙니다**: 프라이빗 서브넷 → 인터넷 아웃바운드 전용. 인바운드 웹 트래픽은 ALB가 처리.

---

## 7. 대표 문제 풀이 예시

### 예시 0: 비용 최적화 아키텍처 선택

> **문제**: 24/7 실행되는 레거시 애플리케이션을 AWS로 마이그레이션. DB 스토리지는 계속 증가. **가장 비용 효율적** 솔루션은?

**정답**: EC2 **예약 인스턴스** + Aurora **예약 인스턴스**

**판별 포인트**:
- 24/7 실행 → RI가 On-Demand 대비 최대 72% 절감
- Spot → 중단 가능해서 24/7 레거시에 부적합 (오답)
- **앱과 DB 모두** RI 필요 — 한쪽만 RI는 "가장 비용 효율적"이 아님
- Aurora → 스토리지 자동 확장 (10GB 단위, 최대 128TiB)으로 "계속 증가" 대응

---

### 예시 1: Warm Standby DR 전략

> **문제**: 전자상거래 회사가 다른 AWS 리전을 포함하는 DR 전략을 생성해야 합니다. DR 리전의 데이터베이스를 최신 상태로 유지해야 하며, 나머지 인프라는 **감소된 용량으로 실행**되어야 합니다. **가장 낮은 RTO**를 충족하는 솔루션은?

**정답**: Amazon Aurora 글로벌 데이터베이스 + **Warm Standby** 배포

**판별 포인트**:
- "감소된 용량으로 실행" → **Warm Standby** (Pilot Light는 인프라 중지)
- Aurora Global → 1초 미만 복제 지연으로 DB 최신 유지
- Warm Standby > Pilot Light RTO → "가장 낮은 RTO" 충족

---

### 예시 2: 서버리스 웹앱

> **문제**: 웹사이트 접근이 예측 불가하고 오랫동안 유휴 상태일 수 있습니다. 가입 고객만 로그인 가능합니다. **가장 비용 효율적인** 3개 조합은?

**정답**: A (Lambda + API GW + DynamoDB), C (Cognito User Pool), E (Amplify + CloudFront)

**판별 포인트**:
- "예측 불가 + 장기 유휴" → **서버리스** (ECS/RDS는 유휴 비용 발생)
- "가입 고객 인증" → **Cognito User Pool** (Identity Pool은 AWS 자격 증명 부여용)
- "프론트엔드" → **Amplify** (S3 + PHP는 서버사이드 미지원)

---

### 예시 3: SQS 버퍼 + 독립 Auto Scaling

> **문제**: 판매 API의 프론트엔드는 ALB + EC2, 백엔드는 SQS로 느슨하게 결합. 신제품 출시 기간 **요청량 급증** 대비. API가 증가된 부하를 처리할 수 있도록 보장.

**정답**: 프론트/백엔드 **별도 Auto Scaling 그룹** — 프론트는 네트워크 트래픽 기반, 백엔드는 **SQS 큐 백로그 기반** 확장

**판별 포인트**:
- 프론트만 ASG → 백엔드 병목 (오답)
- 인스턴스 수 고정 → 수요 대응 불가 (오답)
- 각 계층 독립 확장이 핵심

---

### 예시 4: AWS Backup 중앙 관리

> **문제**: EC2 + EBS + RDS + DynamoDB 인프라의 백업을 **중앙 집중화**하고 자동화. **AWS 기본 옵션** 사용.

**정답**: **AWS Backup** — 백업 계획으로 모든 서비스 통합 관리

**판별 포인트**:
- DLM → EBS/AMI만 지원 (RDS/DynamoDB ✕)
- Storage Gateway → 하이브리드 스토리지 (백업 도구 ✕)
- AWS Config → 구성 변경 추적 (백업 ✕)

---

### 예시 5: Vault Lock Compliance Mode

> **문제**: EC2 + S3 백업 전략. 보유 기간 동안 파일을 **변조해서는 안 됨**.

**정답**: AWS Backup — **규정 준수 모드 (Compliance Mode)** Vault Lock

**판별 포인트**:
- Governance Mode → 특별 권한으로 삭제 가능 (오답)
- Compliance Mode → 루트 포함 누구도 삭제/변경 불가 (WORM)

---

### 예시 6: Amazon MQ + RDS Multi-AZ

> **문제**: ActiveMQ → EC2 → MySQL(EC2). 운영 복잡성 낮으면서 **가장 높은 가용성**.

**정답**: Amazon MQ (Active/Standby) + ASG (Multi-AZ) + RDS Multi-AZ

**판별 포인트**:
- EC2에서 ActiveMQ 직접 운영 → 운영 복잡성 높음 (오답)
- EC2에서 MySQL 직접 운영 → RDS가 운영 부담 경감
- 소비자 EC2도 **ASG** 필요 (수동 관리 ✕)

---

### 예시 7: CloudWatch 경보 EC2 복구

> **문제**: 레거시 시스템, 코드 수정 불가, **단일 인스턴스만** 가능. 시스템 **복구 시간 향상**.

**정답**: Amazon CloudWatch 경보 → **EC2 인스턴스 복구 (Recover)** 액션

**판별 포인트**:
- 종료 방지 → 하드웨어 장애 복구 ✕
- Multi-AZ EC2 → 존재하지 않는 개념
- RAID EBS → 인스턴스 수준 장애 복구 ✕
- CloudWatch 복구 → 동일 IP/ID/EBS 유지하며 새 호스트에서 재시작

---

### 예시 8: 60초 RTO DR

> **문제**: 3계층 웹앱, 60초 RTO. DR 솔루션.

**정답**: DR 리전에 **실행 중인** EC2 + ALB + S3 CRR + Route 53 **상태 확인 기반 장애 조치**

**판별 포인트**:
- EC2 중지(stopped) → 시작에 수 분, 60초 RTO 미충족 (오답)
- CloudFormation 배포 → 수십 분, 60초 RTO 미충족 (오답)
- 인스턴스 **실행 중** + Route 53 자동 장애 조치 = 즉시 전환

---

### 예시 9: ECS Fargate + Step Functions

> **문제**: 대용량 비디오 파일, 처리에 **최대 30분**. 서버리스 확장 가능 아키텍처.

**정답**: S3 이벤트 → EventBridge → **Step Functions** → **AWS Fargate** 작업

**판별 포인트**:
- Lambda → 15분 제한으로 30분 처리 불가 (오답)
- EFS → 이벤트 트리거 미지원 (오답)
- Fargate → 시간 제한 없음 + 서버리스

---

### 예시 10: 온프레미스 DR — Elastic Disaster Recovery

> **문제**: 온프레미스 3계층 웹 애플리케이션. RTO 15분. 장애 조치 **테스트 가능**해야 하며 **자동화된** 장애 조치 메커니즘.

**정답**: **AWS Elastic Disaster Recovery (DRS)** — VM을 AWS에 증분 복제, DR 프로세스 자동화

**판별 포인트**:
- AWS Backup → 스냅샷 복원에 시간이 걸려 15분 RTO 보장 어려움 (오답)
- DMS + Storage Gateway → 자동화된 장애 조치 메커니즘 미제공 (오답)
- DRS → 지속적 증분 복제 + 자동 장애 조치 + **장애 조치 드릴 테스트** 가능

---

### 예시 11: 모놀리스 → 마이크로서비스 분해

> **문제**: 기존 온프레미스 모놀리식 애플리케이션을 AWS로 마이그레이션. 프론트/백엔드 코드를 최대한 유지하면서 더 작은 응용 프로그램으로 분리. 팀별 관리. **운영 오버헤드 최소 + 확장성**.

**정답**: **AWS Amplify** (프론트엔드) + **API Gateway + Lambda** (백엔드 마이크로서비스)

**판별 포인트**:
- Lambda만 → 프론트엔드 호스팅 방법 없음 (불완전)
- EC2 + ASG → 운영 오버헤드 크고 마이크로서비스 독립 배포 복잡
- ECS + ALB → 프론트엔드 호스팅 미포함
- Amplify + API GW + Lambda → 완전 서버리스, 팀별 독립 배포, 운영 최소

---

### 예시 12: FSx + AWS Backup Vault Lock

> **문제**: FSx for Windows File Server. RPO 5분, us-west-2에 복제. 복제 데이터 **5년간 삭제 불가**.

**정답**: **Multi-AZ** FSx + AWS Backup (교차 리전 복사) + **Compliance Mode** Vault Lock (5년)

**판별 포인트**:
- Single-AZ → 동기식 복제 없어 5분 RPO 미충족 (오답)
- Governance Mode → 특별 권한으로 삭제 가능 — "삭제 불가" 미충족 (오답)
- Multi-AZ → AZ 간 동기식 복제로 RPO 5분 이하 보장
- Compliance Mode → 루트 포함 누구도 삭제 불가 (WORM)

---

### 예시 13: 컴퓨팅 비용 + 스토리지 비용 동시 최적화

> **문제**: 영수증 이미지 분석 앱. ALB + ASG + EC2 On-Demand. 인기 증가로 컴퓨팅·스토리지 비용 모두 증가. **성능 영향 없이 가장 큰 비용 절감**.

**정답**: 최소 인스턴스 수에 **Compute Savings Plan** + 30일 후 원시 이미지를 **S3 Glacier Deep Archive** (S3 수명 주기 정책)

**판별 포인트**:
- 최대 인스턴스에 Savings Plan → 과도한 약정, 미사용 용량 (오답)
- EFS → S3보다 GB당 비용 높음 (오답)
- 최대 인스턴스 수 줄임 → 피크 처리 불가, 성능 영향 (오답)
- 기본 용량 RI/SP + 피크는 On-Demand + S3 수명 주기 = 최적 조합

---

## 7-1. 아키텍처 의사 결정 플로우차트

### 컴퓨팅 선택 플로우

```
실행 시간은?
├── < 15분 → Lambda (서버리스, 최저 비용)
├── 15분 ~ 수 시간 → ECS Fargate (서버리스 컨테이너)
├── 수 시간 이상 → EC2 또는 AWS Batch
└── 지속적 실행 (24/7)
    ├── 예측 가능 → EC2 RI / Savings Plan
    ├── 가변적 → ASG (On-Demand + Spot 혼합)
    └── 중단 가능? → Spot 인스턴스
```

### DR 전략 선택 플로우

```
RTO 요구사항은?
├── 수 시간 허용 → Backup & Restore (최저 비용)
├── 수십 분 → Pilot Light (핵심 DB만 복제)
├── 수 분 → Warm Standby (축소 인프라 상시 가동)
└── 거의 0 → Multi-Site Active/Active (최고 비용)

추가 고려:
├── "비용 최소화" → 한 단계 낮은 전략 선택
├── "데이터베이스 최신 유지" → Aurora Global 또는 DynamoDB Global Tables
└── "기본 인프라 정상 시 부하 불필요" → Active-Passive (Failover)
```

### 데이터베이스 선택 플로우

```
데이터 모델은?
├── 관계형 (SQL, JOIN, 트랜잭션)
│   ├── 코드 변경 최소 + MySQL → RDS for MySQL 또는 Aurora MySQL
│   ├── 코드 변경 최소 + PostgreSQL → RDS for PostgreSQL 또는 Aurora PostgreSQL
│   ├── SQL Server/Oracle → RDS for SQL Server/Oracle 또는 RDS Custom
│   ├── 가변 트래픽 → Aurora Serverless v2
│   └── 다중 리전 DR → Aurora Global Database
├── NoSQL (Key-Value, 문서)
│   ├── 한 자릿수 ms 응답 → DynamoDB
│   ├── 다중 리전 active-active → DynamoDB Global Tables
│   └── 캐싱 필요 → DynamoDB + DAX
└── 캐시/세션
    └── 마이크로초 응답 → ElastiCache for Redis
```

### 정적 콘텐츠 호스팅 플로우

```
콘텐츠 유형은?
├── 정적 (HTML/CSS/JS) → S3 + CloudFront
│   ├── CI/CD 필요 → AWS Amplify
│   ├── HTTPS 필요 → CloudFront + ACM (us-east-1)
│   └── IP 제한 필요 → CloudFront + WAF IP Set
├── 동적 (PHP/Java/Python) → EC2/ECS/Lambda (S3 불가)
└── SPA (React/Vue) → S3 + CloudFront (API는 API GW + Lambda)
```

---

## 7-2. 아키텍처 패턴 비교 종합표

### 웹 애플리케이션 아키텍처 패턴 비교

| 패턴 | 구성 | 장점 | 단점 | 적합 워크로드 |
|---|---|---|---|---|
| **전통 3계층** | ALB + EC2 ASG + RDS Multi-AZ | 유연성, 커스텀 런타임 | 운영 오버헤드 (패치, AMI) | 레거시, 상태 유지 앱 |
| **컨테이너 기반** | ALB + ECS Fargate + Aurora | 서버리스 컨테이너, 이식성 | 컨테이너화 필요 | Docker 앱, 마이크로서비스 |
| **완전 서버리스** | CloudFront + S3 + API GW + Lambda + DynamoDB | 유휴 비용 0, 무한 확장 | 15분 제한, 콜드 스타트 | SPA, API, 간헐적 트래픽 |
| **하이브리드** | CloudFront + ALB + EC2/ECS + RDS | CDN + 전통 백엔드 | 복잡성 | 글로벌 + 레거시 백엔드 |

### DR 전략별 AWS 서비스 매핑

| 전략 | 컴퓨팅 | 데이터베이스 | 스토리지 | 라우팅 |
|---|---|---|---|---|
| **Backup & Restore** | CloudFormation (필요 시 배포) | AWS Backup → 스냅샷 복원 | S3 CRR | Route 53 수동 변경 |
| **Pilot Light** | AMI 준비 (인스턴스 중지) | Aurora Global (상시 복제) | S3 CRR | Route 53 Failover |
| **Warm Standby** | 축소 ASG + ALB (상시 가동) | Aurora Global (상시 복제) | S3 CRR | Route 53 Failover |
| **Multi-Site** | 전체 ASG + ALB (양 리전) | DynamoDB Global Tables | S3 CRR | Route 53 Weighted/Latency |

### 메시지 서비스 비교 (디커플링)

| 서비스 | 모델 | 순서 보장 | 메시지 보존 | 실시간 | 사용 사례 |
|---|---|---|---|---|---|
| **SQS Standard** | Pull | ✕ (best-effort) | 최대 14일 | ✕ | 범용 디커플링 |
| **SQS FIFO** | Pull | ✅ (엄격) | 최대 14일 | ✕ | 순서 중요한 처리 |
| **SNS** | Push | ✕ | ✕ (즉시 전달) | ✅ | 팬아웃, 알림 |
| **EventBridge** | Push (규칙) | ✕ | ✕ | ✅ | 이벤트 기반 라우팅 |
| **Kinesis** | Pull (샤드) | ✅ (샤드 내) | 최대 365일 | ✅ | 실시간 스트리밍 |
| **Amazon MQ** | Push/Pull | ✅ | 구성 가능 | ✅ | 레거시 브로커 대체 |

### 컴퓨팅 비용 모델 비교

| 모델 | 할인율 | 약정 | 중단 위험 | 적합 워크로드 |
|---|---|---|---|---|
| **On-Demand** | 0% (기준) | 없음 | 없음 | 단기, 예측 불가 |
| **RI (1년)** | ~40% | 1년 | 없음 | 24/7, 예측 가능 |
| **RI (3년)** | ~60-72% | 3년 | 없음 | 장기 안정적 |
| **Savings Plan** | ~40-72% | 1-3년 ($/hr) | 없음 | 유연한 인스턴스 타입 |
| **Spot** | 최대 90% | 없음 | **있음** (2분 통보) | 배치, CI/CD, 중단 가능 |

---

## 8. 연관 카테고리

이 카테고리는 **전체 카테고리에 걸쳐 통합적 아키텍처 관점**을 제공합니다.

| 연관 카테고리 | 연결 포인트 |
|---|---|
| [03-elb-and-asg.md](03-elb-and-asg.md) | ALB + ASG 구성, 헬스체크, 스케일링 정책 |
| [04-rds.md](04-rds.md) | RDS/Aurora Multi-AZ, Read Replica, Aurora Global, RDS Proxy |
| [05-dynamodb.md](05-dynamodb.md) | DynamoDB Global Tables, Auto Scaling, DAX |
| [06-s3.md](06-s3.md) | S3 CRR, 수명 주기 정책, 암호화, Transfer Acceleration |
| [08-container.md](08-container.md) | ECS Fargate, EKS, 컨테이너 기반 마이크로서비스 |
| [09-service-communication.md](09-service-communication.md) | SQS/SNS/EventBridge/Step Functions 디커플링 패턴 |
| [10-caching.md](10-caching.md) | CloudFront, ElastiCache, DAX 캐싱 전략 |
| [15-security.md](15-security.md) | WAF, SG/NACL, KMS, Cognito, IAM |
| [17-vpc.md](17-vpc.md) | VPC 설계, 서브넷 분리, NAT GW, VPC 엔드포인트 |
| [18-endpoint.md](18-endpoint.md) | API Gateway, CloudFront, Global Accelerator |

> **학습 순서 권장**: 개별 서비스 카테고리 (01~20)를 먼저 학습한 후, 이 카테고리(21-architecture)로 **통합 복습**하면 효과적입니다.

---

> **주의**: AWS 서비스 할당량·가격·이름은 수시로 변경됩니다. 시험 직전 공식 문서로 재확인하세요.
> 본 노트는 `21-architecture/` 89개 문제 전수 분석을 기반으로 도출된 학습 자료입니다.
