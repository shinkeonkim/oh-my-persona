# 15 · Security 학습 노트

> 기반: `15-security/` 문제 98개 전수 분석 + `notes/AWS_SAA-C03_리소스_완전정리.md` 1.6·2.8·2.13·2.14절
> 최종 갱신: 2026-07-31

---

## 1. 카테고리 개요 (Domain 1 — 30%, 시험 최대 비중)

**Security**는 SAA-C03 **Domain 1: Design Secure Architectures (30%)**의 핵심이다. 98문항으로 전체 문제 은행의 ~7.5%를 차지하며, 4개 도메인 중 **가장 높은 배점**(채점 50문항 기준 약 15문항)을 받는다.

98문제 분석 결과, 단독 서비스 지식보다 **"제약 조건(규제·비용·운영 오버헤드) 하에서 최적 보안 서비스를 고르는"** 형태가 압도적이다. 주요 축은 세 가지:

1. **암호화·키 관리**: KMS vs CloudHSM vs SSE 방식 선택, 키 로테이션, Envelope Encryption
2. **네트워크·애플리케이션 방어**: WAF vs Shield vs Network Firewall vs SG vs NACL 계층 구분
3. **위협 탐지·데이터 분류·거버넌스**: GuardDuty vs Inspector vs Macie vs Detective vs Security Hub 역할 구분

**출제 비중 체감**: 15-security 자체 98문항 외에 06-s3(암호화), 17-vpc(SG/NACL), 19-identity(IAM/SCP), 14-monitoring(CloudTrail) 카테고리에서도 보안이 빈번히 등장하므로 **실질 출제 비중은 15~20%** 수준.

---

## 2. 핵심 서비스 한줄 요약

| 서비스 | 한줄 정리 | 시험 포인트 |
|---|---|---|
| **AWS KMS** | AWS 관리형 암호화 키 서비스. 대부분의 저장 데이터 암호화의 기본 | CMK vs AWS Managed vs AWS Owned, 자동 로테이션, 요청 쿼터 |
| **AWS CloudHSM** | 전용 단일 테넌트 HSM. FIPS 140-2 Level 3 | "AWS도 키 접근 불가", 규제·컴플라이언스 |
| **AWS Secrets Manager** | DB 자격 증명·API 키 자동 교체(Lambda 기반) | "비밀번호 자동 교체", RDS 네이티브 통합 |
| **SSM Parameter Store** | 설정값·비밀(SecureString) 저장. 표준 티어 무료 | "비용 최소", 교체 불필요한 설정값 |
| **AWS ACM** | TLS 인증서 무료 발급·자동 갱신 | CloudFront용은 us-east-1, EC2 직접 설치 불가 |
| **AWS WAF** | L7 웹 방화벽 (SQLi/XSS/속도 제한/지역 차단) | ALB·CloudFront·API GW에 연결, NLB 불가 |
| **AWS Shield Standard** | 무료 L3/L4 DDoS 자동 방어 | 모든 AWS 고객 기본 제공 |
| **AWS Shield Advanced** | 유료 L3~L7 DDoS + DRT + 요금 급증 보호 | $3,000/월, "대규모 정교한 DDoS", proactive engagement |
| **AWS Network Firewall** | VPC 경계 상태 저장 L3~L7 방화벽 (IPS) | 도메인 필터링, Suricata 규칙, "승인된 URL만 허용" |
| **AWS Firewall Manager** | Organizations 통합 WAF/Shield/SG/NF 중앙 관리 | "여러 계정 WAF 규칙 일괄 적용" |
| **Amazon GuardDuty** | ML 기반 위협 탐지 (로그 분석, 에이전트 불필요) | VPC Flow/DNS/CloudTrail 자동 분석, RDS Protection |
| **Amazon Inspector** | EC2/ECR/Lambda CVE 취약점 스캔 | "소프트웨어 취약점 스캔", CVSS 점수 |
| **Amazon Macie** | S3 PII/PHI 민감 데이터 자동 탐지·분류 | "S3에서 개인정보 발견", Managed Data Identifier |
| **Amazon Detective** | GuardDuty findings 심층 조사·시각화 | "근본 원인 조사", 탐지가 아닌 조사 |
| **AWS Security Hub** | 보안 결과 단일 대시보드 집계 | CIS/PCI DSS 표준 검사, Organizations 통합 |
| **AWS Audit Manager** | 규정 준수 감사 증거 자동 수집 | "감사 증거 자동화" |
| **AWS Artifact** | AWS SOC/ISO/PCI 규정 보고서 다운로드 포털 | "AWS의 규정 준수 보고서" |
| **Security Group** | ENI 단위, Stateful, Allow만 | Deny 불가 → 특정 IP 차단은 NACL |
| **Network ACL** | 서브넷 단위, Stateless, Allow+Deny | 규칙 번호 순 최초 일치, 임시 포트 아웃바운드 필요 |
| **AWS Backup Vault Lock** | 백업 WORM 보호 | EBS 스냅샷/DynamoDB/RDS 백업 수정·삭제 불가 |

---

## 3. 출제 패턴 분석

98문제에서 추출한 **반복 시나리오 Top 20**:

| # | 시나리오 패턴 | 출현 | 정답 키워드 |
|---|---|---|---|
| 1 | **"DB 비밀번호 자동 교체"** | 8 | `Secrets Manager` + 자동 로테이션 |
| 2 | **"저장 데이터 암호화 + 키 연간 자동 교체 + 감사"** | 7 | `SSE-KMS` + 고객 관리형 키 + 자동 로테이션 |
| 3 | **"SQLi/XSS 방어"** | 7 | `AWS WAF` (관리형 규칙) |
| 4 | **"대규모 DDoS 공격 + DRT"** | 6 | `Shield Advanced` |
| 5 | **"S3 PII 자동 탐지·분류"** | 6 | `Amazon Macie` |
| 6 | **"EC2/컨테이너 CVE 취약점 스캔 + 패치"** | 4 | `Inspector` + `SSM Patch Manager` |
| 7 | **"여러 보안 결과 단일 대시보드"** | 3 | `Security Hub` |
| 8 | **"악성 IP 통신·이상 API 호출 탐지"** | 5 | `GuardDuty` |
| 9 | **"특정 국가만 트래픽 허용"** | 3 | `WAF` 지리적 일치(Geo Match) |
| 10 | **"특정 악성 IP 차단"** | 3 | WAF IP 매치 또는 `NACL` (SG는 Deny 불가) |
| 11 | **"VPC 경계 도메인 필터링 (승인 URL만)"** | 3 | `Network Firewall` 도메인 목록 규칙 |
| 12 | **"Organizations 전체 WAF/SG 중앙 관리"** | 3 | `Firewall Manager` |
| 13 | **"HTTPS TLS 인증서 무료 + 자동 갱신"** | 3 | `ACM` 공인 인증서 + DNS 검증 |
| 14 | **"FIPS 140-2 Level 3 / AWS도 키 접근 불가"** | 2 | `CloudHSM` |
| 15 | **"AWS 클라우드 외부 키 관리 + 규제"** | 2 | `KMS XKS` (외부 키 스토어) 또는 클라이언트 측 암호화 |
| 16 | **"KMS 요청 비용 최적화 + 암호화 유지"** | 2 | `S3 Bucket Key` |
| 17 | **"암호화된 RDS 스냅샷 교차 계정 공유"** | 2 | 스냅샷 공유 + KMS 키 정책에 대상 계정 추가 |
| 18 | **"HTTP 플러드 / 속도 제한"** | 3 | `WAF Rate-based Rule` |
| 19 | **"EBS 기본 암호화 강제"** | 2 | EC2 계정 속성 EBS 기본 암호화 활성화 |
| 20 | **"DBA도 데이터 접근 불가 + 암호화"** | 2 | `KMS 클라이언트 측 암호화` (CSE) |

### 출제 공식 (시나리오 → 정답 흐름)

```
"비밀번호/자격 증명 자동 교체 + RDS"
  → Secrets Manager (자동 로테이션, RDS 네이티브 통합)

"설정값 저장 + 비용 최소 + 교체 불필요"
  → SSM Parameter Store (표준 티어 무료)

"저장 데이터 암호화 + 키 로테이션 제어"
  → KMS 고객 관리형 키 (CMK) + 자동 로테이션

"AWS도 키 접근 불가 / FIPS 140-2 Level 3"
  → CloudHSM

"S3에 저장하기 전에 암호화"
  → 클라이언트 측 암호화 (CSE)

"SQLi/XSS + ALB/API Gateway"
  → WAF (관리형 규칙)

"DDoS + 구성 변경 최소 + DRT"
  → Shield Advanced

"악의적 활동 지속 모니터링 (에이전트 없이)"
  → GuardDuty

"S3 PII 발견 → SNS 알림"
  → Macie → EventBridge → SNS

"탐지된 사건 근본 원인 조사"
  → Detective

"타사 방화벽 어플라이언스 투명 삽입"
  → Gateway Load Balancer (GWLB)
```

---

## 4. 서비스 심층 노트

### 4.1 AWS KMS (Key Management Service)

#### 4.1.1 키 유형 비교

| 키 유형 | 생성 주체 | 키 정책 수정 | 자동 로테이션 | 비용 | 대표 용도 |
|---|---|---|---|---|---|
| **Customer Managed Key** | 사용자 | **O** | **O** (365일, 사용자 제어) | 키당 $1/월 + 요청 | 대부분의 SSE-KMS 암호화 |
| **AWS Managed Key** | AWS | X | O (자동, 365일) | 요청만 | `aws/s3`, `aws/ebs` 등 기본 키 |
| **AWS Owned Key** | AWS | X | AWS 내부 | **무료** | SSE-S3, DynamoDB 기본 암호화 |

#### 4.1.2 핵심 개념

- **대칭(Symmetric) vs 비대칭(Asymmetric)**: 대부분 대칭 키 사용 (AES-256). 비대칭은 외부에서 암호화해야 할 때 (서명 검증, 퍼블릭 키 배포)
- **Envelope Encryption**: 데이터 키(DEK)로 데이터 암호화 → KMS 마스터 키(CMK)로 DEK 암호화. SSE-KMS의 기본 동작. `GenerateDataKey` API로 평문+암호화된 DEK 쌍 획득
- **Key Rotation**: 고객 관리형 키는 자동 로테이션 활성화 시 연 1회(365일) 새 키 자료 생성. 이전 키 자료 영구 보존 → 기존 데이터 복호화 가능. 키 ID/ARN 불변
- **Key Policy + Grant + IAM Policy**: 키 정책이 1차 게이트. IAM 정책은 키 정책이 허용해야만 유효. Grant는 임시 권한 부여 (프로그래밍 방식)
- **Multi-Region Keys**: 동일 키 ID·키 자료를 여러 리전에 복제 → 교차 리전 암호화/복호화에 동일 키 사용. CRR + SSE-KMS 시 "동일 키 필요" 문제 해결
- **External Key Store (XKS)**: AWS 외부 키 관리자와 통합. 규제로 키가 AWS 밖에 있어야 할 때. 다양한 벤더 지원
- **Custom Key Store (CloudHSM 기반)**: KMS API를 사용하되 키 자료를 CloudHSM 클러스터에 저장. KMS 편의성 + CloudHSM 보안
- **Imported Key Material**: 사용자가 키 자료를 직접 가져옴. **자동 로테이션 불가**, 수동만 가능. 만료 일자 설정 가능
- **요청 쿼터**: 리전별 초당 요청 제한 있음 → **SSE-KMS로 S3 대량 액세스 시 스로틀링 발생 가능** → `S3 Bucket Key`로 KMS 호출 최대 99% 감소
- **S3 Bucket Key**: 버킷 수준 DEK를 생성하여 일정 기간 재사용 → 개별 객체마다 KMS 호출 불필요 → KMS 비용 절감

#### 4.1.3 KMS 키 유형별 제어 수준 비교

| 제어 항목 | Customer Managed | AWS Managed | AWS Owned |
|---|---|---|---|
| 키 정책 수정 | **O** | X | X |
| 활성화/비활성화 | **O** | X | X |
| 삭제 예약 | **O** (7~30일 유예) | X | X |
| 교체 주기 제어 | **O** | X | X |
| CloudTrail 감사 | **O** | **O** | X |
| 교차 계정 공유 | **O** (키 정책) | X | X |
| 비용 | 키 $1/월 + 요청 | 요청만 | **무료** |

> **함정**: AWS 관리형 키는 사용자가 로테이션 주기·키 정책을 제어할 수 없다
> **함정**: Imported Key Material은 자동 로테이션 불가
> **함정**: AWS 관리형 키는 교차 계정 스냅샷 공유에 사용 불가 (키 정책 수정 불가)

#### 4.1.4 S3 암호화 방식 비교 (시험 초다빈출)

| 방식 | 암호화 주체 | 키 관리 | CloudTrail 감사 | 자동 교체 | 비용 | 대표 시나리오 |
|---|---|---|---|---|---|---|
| **SSE-S3** | S3 서버 | AWS 완전 관리 | X (개별 키 추적 불가) | AWS 내부 | **무료** | 기본 암호화 (2023년부터 S3 기본값) |
| **SSE-KMS** (AWS 관리형) | S3 서버 | AWS 관리 KMS 키 | **O** | O (자동) | 요청 비용 | 감사 필요 + 비용 최소 |
| **SSE-KMS** (고객 관리형) | S3 서버 | 사용자 KMS CMK | **O** | O (사용자 제어) | 키 + 요청 | 감사 + 키 제어 + 교차 계정 |
| **SSE-C** | S3 서버 | **고객 직접 관리** | X | X (고객 책임) | 무료 | 고객이 키 완전 제어 (HTTPS 필수) |
| **CSE** (클라이언트) | **클라이언트** | 고객 관리 | X | X | 무료 | "S3에 저장 **전에** 암호화", DBA 접근 차단 |

> **결정 트리**:
> 1. "저장 전에 암호화" → **CSE**
> 2. "키 감사 + 연간 자동 교체" → **SSE-KMS**
> 3. "키 감사 + 자동 교체 + **비용 최소**" → SSE-KMS **(AWS 관리형 키)**
> 4. "키 감사 + 자동 교체 + **키 제어/교차 계정**" → SSE-KMS **(고객 관리형 키)**
> 5. "AWS 외부에서 키 관리" → **SSE-C** 또는 **CSE**
> 6. "기본 암호화, 특별 요구 없음" → **SSE-S3**

### 4.2 AWS CloudHSM

| 항목 | 내용 |
|---|---|
| 테넌시 | **전용 단일 테넌트 HSM** |
| 인증 | **FIPS 140-2 Level 3** |
| 키 접근 | **AWS도 접근 불가** — 고객만 키 관리 |
| 가용성 | **클러스터** (다중 AZ HA) |
| 비용 | 시간당 과금 (비쌈) |
| 대표 용도 | 규제 준수, Oracle TDE, SSL 오프로드 |

### 4.3 KMS vs CloudHSM 비교표

| 항목 | KMS | CloudHSM |
|---|---|---|
| 관리 | AWS 관리형 | 고객 관리 |
| 테넌시 | 공유 | **단일 테넌트** |
| FIPS | 140-2 Level 2 | **140-2 Level 3** |
| 키 접근 | AWS도 가능 (관리형 키) | **고객만** |
| 자동 로테이션 | O (CMK) | 고객 구현 |
| 비용 | 저렴 | 비쌈 |
| 통합 | 대부분 AWS 서비스 네이티브 | 제한적 |

> **판별**: "FIPS 140-2 Level 3" 또는 "AWS도 키 접근 불가" 또는 "규제" → **CloudHSM**
> 그 외 대부분 → **KMS**

### 4.4 AWS Secrets Manager

| 기능 | 설명 |
|---|---|
| **자동 교체 (Auto Rotation)** | Lambda 기반, RDS/Aurora/Redshift/DocumentDB 네이티브 통합 |
| **교체 주기** | 사용자 지정 (예: 14일, 30일, 90일) |
| **교차 리전 복제** | 비밀을 여러 리전에 자동 복제 |
| **Secret Versioning** | `AWSCURRENT` / `AWSPREVIOUS` 자동 관리 |
| **BatchGetSecretValue** | 한 번의 API 호출로 여러 비밀 검색 |
| **비용** | 비밀당 $0.40/월 + API 요청 |

### 4.5 SSM Parameter Store

| 항목 | 표준 티어 | Advanced 티어 |
|---|---|---|
| 비용 | **무료** | 유료 |
| 파라미터 수 | 10,000개까지 | 100,000개까지 |
| 최대 값 크기 | 4KB | 8KB |
| 정책 (만료 알림 등) | X | O |
| Higher Throughput | X | O (최대 1,000 TPS) |

- **타입**: `String` / `StringList` / `SecureString` (KMS 암호화)

### 4.6 Secrets Manager vs Parameter Store 비교표

| 항목 | Secrets Manager | Parameter Store |
|---|---|---|
| 자동 교체 | **O (네이티브)** | X (직접 구현 필요) |
| RDS 통합 교체 | **O** | X |
| 비용 | 유료 ($0.40/비밀/월) | **표준 무료** |
| 교차 리전 복제 | **O** | X |
| 최대 값 크기 | 64KB | 4KB (표준) / 8KB (Advanced) |

> **판별 공식**:
> - "비밀번호 **자동 교체**" + "RDS" → **Secrets Manager**
> - "설정값 저장" + "**비용 최소**" + 교체 불필요 → **Parameter Store** (표준 무료)

### 4.7 AWS Certificate Manager (ACM)

| 항목 | 내용 |
|---|---|
| **Public 인증서** | **무료** + 자동 갱신 (DNS 검증 권장) |
| **Private CA** | 유료 ($400/월~) |
| **CloudFront용** | **반드시 us-east-1** 에서 발급 |
| **연결 대상** | ELB, CloudFront, API Gateway, App Runner |
| **EC2 직접 설치** | **불가** |
| **Import 인증서** | 외부 CA 인증서 가져오기 가능. **자동 갱신 X** → EventBridge로 만료 알림 |
| **DNS vs 이메일 검증** | DNS 검증 = 한 번 설정 후 자동 갱신. 이메일 = 매번 수동 승인 필요 |

> **함정**: ACM 인증서는 EC2에 직접 설치 불가 → ALB/NLB에서 SSL 종료(오프로드)
> **함정**: CloudFront에 붙일 인증서는 **반드시 us-east-1** (다른 리전 불가)
> **함정**: 가져온(import) 인증서는 자동 갱신 불가 → `AWS Config acm-certificate-expiration-check` 규칙 + EventBridge + SNS 알림

### 4.8 AWS WAF

| 구성 요소 | 설명 |
|---|---|
| **Web ACL** | 규칙의 컨테이너. CloudFront/ALB/API GW/AppSync/App Runner에 연결 |
| **Managed Rules** | AWS 또는 마켓플레이스 규칙 그룹 (SQL 주입, XSS, Bot Control 등) |
| **Custom Rules** | IP 매치, 지리적 매치, 문자열 매치, 정규식 등 |
| **Rate-based Rule** | 5분간 IP당 요청 수 임계값 초과 시 자동 차단 → **HTTP 플러드/DDoS 완화** |
| **Geographic Restriction** | 국가 기반 허용/차단 → "특정 국가만 접근" |
| **Bot Control** | 합법 봇 vs 악성 봇 분류·차단 |
| **CAPTCHA / Challenge** | 자동화된 봇 vs 실제 사용자 구분 |
| **Fraud Control** | 계정 탈취·계정 생성 사기 방지 |
| **IP Set** | 최대 10,000개 IP/CIDR → 대규모 IP 화이트리스트/블랙리스트 |
| **IP Reputation** | 알려진 악성 IP 자동 차단 (AWS 관리형 규칙) |
| **로깅** | WAF 로그 → Kinesis Data Firehose → S3 (트래픽 분석) |

**연결 가능 서비스** (시험 단골):

| 연결 가능 | 연결 불가 |
|---|---|
| **CloudFront, ALB, API Gateway (REST), AppSync, Cognito User Pool, App Runner** | **NLB, EC2 직접, Global Accelerator** |

**WAF 시나리오별 적용 규칙 가이드**:

| 시나리오 | 적용 규칙 |
|---|---|
| SQL 주입 방어 | `AWSManagedRulesSQLiRuleSet` 관리형 규칙 |
| XSS 방어 | `AWSManagedRulesCommonRuleSet` (XSS 포함) |
| HTTP 플러드 / 속도 제한 | **Rate-based Rule** (임계값 설정) |
| 특정 국가만 허용 | **Geo Match** 규칙 |
| 알려진 악성 IP 차단 | **IP Reputation** 관리형 규칙 |
| 봇 트래픽 차단 | **Bot Control** 관리형 규칙 |
| 특정 IP 화이트리스트 | **IP Set** + Allow 규칙 |
| CVE/새로운 취약점 방어 | **AWS Managed Rules** (AWS가 자동 업데이트) |

> **함정**: WAF는 NLB에 연결 불가. NLB 뒤에 WAF를 쓰려면 ALB를 중간에 배치해야 한다
> **함정**: WAF는 L7만 (HTTP/HTTPS). L3/L4 DDoS는 Shield
> **함정**: WAF는 Global Accelerator에 직접 연결 불가. GA 뒤의 ALB에 연결해야 함

### 4.9 AWS Shield

| | Standard | Advanced |
|---|---|---|
| 비용 | **무료** (모든 AWS 고객) | **$3,000/월** + 데이터 전송 |
| 보호 계층 | L3/L4 | **L3/L4/L7** |
| DDoS 대응 팀 (DRT) | X | **O (24/7)** |
| 요금 급증 보호 | X | **O** (DDoS로 인한 스케일링 비용 환불) |
| 사전 대응 (Proactive Engagement) | X | **O** |
| WAF/Firewall Manager 포함 | X | **O** |
| 보호 대상 | 자동 | CloudFront, Route 53, ALB, NLB, EIP, Global Accelerator |

> **판별**: "DDoS" + "무료/기본" → Shield Standard (이미 적용됨)
> "DDoS" + "대규모/정교한" + "DRT" + "요금 보호" → **Shield Advanced**

### 4.10 AWS Network Firewall

| 항목 | 내용 |
|---|---|
| 위치 | **VPC 경계** (전용 방화벽 서브넷) |
| 계층 | **상태 저장 L3~L7** |
| IPS | **침입 방지 시스템** |
| 도메인 필터링 | **FQDN 기반** 아웃바운드 트래픽 제어 |
| 규칙 엔진 | **Suricata** 오픈소스 규칙 호환 |
| 대표 용도 | "승인된 타사 리포지토리 URL만 허용", VPC 인/아웃바운드 검사 |

> **WAF vs Network Firewall 구분**:
> - WAF = L7 **웹 애플리케이션** 방화벽 (HTTP 요청 필터링, ALB/CloudFront에 연결)
> - Network Firewall = L3~L7 **VPC 네트워크** 방화벽 (모든 프로토콜, 도메인 필터링, IPS)

### 4.11 AWS Firewall Manager

| 항목 | 내용 |
|---|---|
| 전제 | **AWS Organizations** 필수 |
| 관리 대상 | WAF, Shield Advanced, Network Firewall, **VPC Security Groups** |
| 핵심 가치 | **다중 계정·리전에 걸쳐 보안 정책 일괄 적용·감사** |
| SG 감사 | 미사용·중복 규칙 탐지 |

> **판별**: "여러 계정" + "WAF/SG 규칙 중앙 관리" → **Firewall Manager**

### 4.12 Amazon GuardDuty

| 항목 | 내용 |
|---|---|
| 분석 소스 | **VPC Flow Logs, CloudTrail, DNS 로그** (자동, 별도 활성화 불필요) |
| 에이전트 | **불필요** (로그 기반) |
| ML | 이상 탐지 (비정상 API 호출, 악성 IP 통신, 암호화폐 채굴 등) |
| **Protection 모듈** | S3 Protection, EKS Protection, **RDS Protection** (비정상 로그인 탐지), Lambda Protection, **Malware Protection** (EBS 볼륨 스캔) |
| 자동화 | Findings → **EventBridge** → Lambda/SNS/WAF 규칙 업데이트 |
| Organizations | 위임 관리자 계정으로 중앙 관리 |

**GuardDuty 주요 Finding 유형**:

| Finding 카테고리 | 예시 | 의미 |
|---|---|---|
| **Recon** | Recon:EC2/PortProbeUnprotectedPort | EC2 포트 스캔 탐지 |
| **UnauthorizedAccess** | UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration | EC2 인스턴스 자격 증명 외부 사용 |
| **CryptoCurrency** | CryptoCurrency:EC2/BitcoinTool.B | 암호화폐 채굴 활동 |
| **Trojan** | Trojan:EC2/BlackholeTraffic | 블랙홀 IP로 트래픽 전송 |
| **Impact** | Impact:EC2/DenialOfService.Dns | EC2가 DDoS 소스로 사용됨 |

**GuardDuty 자동 대응 파이프라인 (시험 빈출)**:
```
GuardDuty Finding
  → EventBridge Rule (severity 필터)
    → Lambda Function
      → WAF IP 차단 규칙 추가
      → NACL 규칙 추가
      → SNS 알림 전송
      → EC2 격리 (SG 변경)
```

> **핵심 구분**: GuardDuty는 **탐지(Detection)** 전용. **차단(Prevention)은 하지 않는다** → 차단은 WAF/NACL/Lambda 자동화로 별도 구현
> **RDS Protection**: Aurora PostgreSQL/MySQL의 **비정상 로그인 시도** (실패, 불완전, 비정상 패턴) 자동 탐지

### 4.13 Amazon Inspector

| 항목 | 내용 |
|---|---|
| 스캔 대상 | **EC2, ECR 컨테이너 이미지, Lambda 함수** |
| 스캔 내용 | **소프트웨어 취약점 (CVE)**, 네트워크 노출 |
| 점수 | **CVSS 점수** 기반 우선순위 |
| 에이전트 | SSM Agent 사용 (EC2) |
| 자동화 | 지속적 스캔 (새 CVE 발표 시 자동 재스캔) |

> **Inspector vs GuardDuty**: Inspector = "이 소프트웨어에 **알려진 버그**가 있는가" / GuardDuty = "누군가 **악의적으로 행동**하고 있는가"

### 4.14 Amazon Macie

| 항목 | 내용 |
|---|---|
| 대상 | **Amazon S3만** |
| 탐지 | PII, PHI, PCI, 금융 정보 등 **민감 데이터** |
| 방법 | ML + 패턴 매칭 |
| 식별자 | **Managed Data Identifier** (사전 정의) + **Custom Data Identifier** (사용자 정의 정규식) |
| 알림 | Findings → **EventBridge** → SNS/Lambda |
| 스코프 | **리전별 서비스** → 각 리전에서 별도 활성화 필요 |
| Organizations | 위임 관리자 계정으로 중앙 관리 |

> **함정**: Macie는 **S3만** 스캔한다. EC2, RDS 등 다른 서비스의 데이터는 스캔 불가

### 4.15 Amazon Detective

| 항목 | 내용 |
|---|---|
| 목적 | GuardDuty findings의 **심층 조사·시각화** |
| 데이터 | CloudTrail, VPC Flow Logs, GuardDuty findings 자동 수집 |
| 출력 | **자동 그래프 생성** (관계·시간축 시각화) |

> **핵심**: Detective는 **조사(Investigation)** 도구. **탐지하지 않는다** (탐지 = GuardDuty)

### 4.16 AWS Security Hub

| 항목 | 내용 |
|---|---|
| 역할 | **단일 대시보드**에 보안 결과 집계 |
| 소스 | GuardDuty, Inspector, Macie, Firewall Manager, IAM Access Analyzer 등 |
| 표준 | **CIS AWS Foundations Benchmark**, **PCI DSS**, **AWS Foundational Security Best Practices**, **NIST SP 800-53** |
| Aggregator | 다중 계정·리전 결과 통합 |
| Custom Insights | 사용자 정의 필터 |
| Organizations | 위임 관리자 계정으로 중앙 관리 |

> **핵심**: Security Hub는 **집계(Aggregation)** 도구. 자체적으로 탐지하지 않는다

### 4.17 AWS Audit Manager

| 항목 | 내용 |
|---|---|
| 목적 | **규정 준수 감사 증거 자동 수집** |
| 프레임워크 | PCI DSS, SOC 2, GDPR, HIPAA 등 |
| 출력 | 감사 보고서 자동 생성 |

### 4.18 AWS Artifact

| 항목 | 내용 |
|---|---|
| 목적 | **AWS의 규정 준수 보고서·계약 다운로드** 포털 |
| 제공 | SOC 1/2/3, ISO 27001, PCI DSS 보고서 등 |
| 비용 | 무료 |

> **Audit Manager vs Artifact**: Audit Manager = "**내 환경**의 감사 증거 수집" / Artifact = "**AWS 자체**의 규정 보고서 다운로드"

### 4.19 Security Group vs NACL 비교표

| | Security Group (SG) | Network ACL (NACL) |
|---|---|---|
| 적용 대상 | **ENI (인스턴스)** | **서브넷** |
| 상태 | **Stateful** — 인바운드 허용 시 아웃바운드 자동 | **Stateless** — 양방향 각각 규칙 필요 |
| 규칙 종류 | **Allow만** | Allow + **Deny** |
| 규칙 평가 | 모든 규칙 종합 | **규칙 번호 낮은 순 최초 일치** |
| 기본값 | 인바운드 전체 거부 / 아웃바운드 전체 허용 | 기본 NACL: 전부 허용 / 커스텀: 전부 거부 |
| 규칙 수 제한 | 기본 60개 인바운드 + 60개 아웃바운드 | 기본 20개 (최대 40) |
| 대표 용도 | 인스턴스 단위 세밀 제어 | **특정 IP 차단** (SG로 불가) |

> **함정**: "특정 악성 IP를 **차단**하라" → **NACL** (SG에는 Deny 규칙이 없음)
> **함정**: NACL은 Stateless → **임시 포트(1024–65535) 아웃바운드 허용** 을 잊으면 응답이 막힘
> **함정**: NACL 규칙 수 제한(기본 20) → 대규모 IP 목록에는 **WAF IP Set** 사용

### 4.20 IAM 정책 vs SCP vs 리소스 정책 (상세는 19-identity로)

| | IAM 정책 | SCP | 리소스 기반 정책 |
|---|---|---|---|
| 부착 대상 | 사용자/그룹/역할 | 루트/OU/계정 | S3 버킷, KMS 키, SQS 큐 등 |
| 효과 | 권한 부여 | **권한 상한(가드레일)** — 부여 아님 | 권한 부여 + 교차 계정 허용 |
| 핵심 | - | 관리 계정에는 미적용 | 역할 전환 없이 다른 계정 접근 허용 |

**정책 평가 순서**: ① 명시적 Deny → ② SCP 경계 → ③ 명시적 Allow → ④ 기본 암묵적 Deny

> **한 줄 요약**: **명시적 거부는 무엇으로도 뒤집을 수 없다**

### 4.21 보안 서비스 5형제 역할 구분표 (초다빈출)

| 서비스 | 질문 | 대상 | 행동 | 비유 |
|---|---|---|---|---|
| **GuardDuty** | "누가 **악의적으로 행동**하는가" | 계정·워크로드·네트워크 | **위협 탐지** (로그 분석) | 경비원 CCTV |
| **Inspector** | "이 소프트웨어에 **알려진 버그**가 있는가" | EC2/ECR/Lambda | **취약점 스캔** (CVE) | 건물 안전 점검 |
| **Macie** | "이 데이터에 **개인정보**가 있는가" | **S3만** | **민감 데이터 분류** | 문서 분류 담당자 |
| **Detective** | "이 사건의 **원인**은 무엇인가" | GuardDuty findings | **사건 조사·시각화** | 형사 수사관 |
| **Security Hub** | "전체 보안 상태를 **한눈에** 보여달라" | 위 서비스 결과 집계 | **대시보드·표준 검사** | 지휘본부 상황판 |

```
탐지 서비스들의 관계:

GuardDuty (위협 탐지)  ──┐
Inspector  (취약점 스캔) ──┤── findings ──→ Security Hub (집계 대시보드)
Macie      (PII 분류)   ──┤                      ↓
                          │              CIS / PCI DSS 표준 평가
Detective  (사건 조사) ←──┘
     ↑
  GuardDuty findings를 심층 분석
```

### 4.22 저장 시(At Rest) vs 전송 중(In Transit) 암호화

| 계층 | 저장 시 암호화 (At Rest) | 전송 중 암호화 (In Transit) |
|---|---|---|
| S3 | SSE-S3 / SSE-KMS / SSE-C / CSE | HTTPS (TLS), `aws:SecureTransport` 버킷 정책 |
| EBS | EBS 암호화 (KMS 통합) | EC2 ↔ EBS: AWS 내부 암호화 |
| RDS | RDS 암호화 활성화 (KMS) | SSL/TLS (AWS 루트 인증서 다운로드) |
| DynamoDB | 기본 암호화 (AWS Owned Key) 또는 KMS | HTTPS (기본) |
| EFS | KMS 암호화 | TLS 마운트 헬퍼 |

**시험 포인트**:
- "**저장 시** 암호화" → KMS / EBS 암호화 / RDS 암호화
- "**전송 중** 암호화" → TLS/SSL / HTTPS / ACM 인증서
- "**둘 다**" → KMS (저장) + ACM 인증서 on ALB (전송)
- SSL/TLS 인증서 = **전송 중** 암호화. ACM 인증서로 "저장 시" 암호화는 **불가**

### 4.23 교차 계정 암호화 리소스 공유 패턴

**암호화된 RDS/Aurora 스냅샷 교차 계정 공유**:

| 단계 | 작업 |
|---|---|
| 1 | 소스 계정에서 DB 스냅샷 생성 |
| 2 | **고객 관리형 KMS 키**로 암호화 확인 (AWS 관리형 키는 공유 불가) |
| 3 | KMS 키 정책에 대상 계정의 `kms:Decrypt`, `kms:CreateGrant` 권한 추가 |
| 4 | RDS 스냅샷을 대상 계정과 공유 |
| 5 | 대상 계정에서 스냅샷으로부터 새 DB 인스턴스 복원 |

**암호화된 AMI 교차 계정 공유**:

| 단계 | 작업 |
|---|---|
| 1 | AMI의 `launchPermission` 속성에 대상 계정 추가 |
| 2 | KMS 키 정책에 대상 계정의 사용 권한 추가 |
| 3 | 대상 계정에서 AMI로 인스턴스 시작 |

> **핵심**: 암호화된 리소스 교차 계정 공유 = **고객 관리형 KMS 키 필수** + 키 정책에 대상 계정 권한 추가

### 4.24 AWS 보안 서비스 — Organizations 통합 요약

| 서비스 | Organizations 통합 | 위임 관리자 | 중앙 관리 기능 |
|---|---|---|---|
| **GuardDuty** | O | O | 모든 멤버 계정 위협 탐지 |
| **Inspector** | O | O | 모든 멤버 계정 취약점 스캔 |
| **Macie** | O | O | 모든 멤버 계정 S3 민감 데이터 분류 |
| **Security Hub** | O | O | 모든 멤버 계정 보안 결과 집계·표준 검사 |
| **Firewall Manager** | **필수** | O | 모든 멤버 계정 WAF/SG/NF 규칙 적용 |
| **CloudTrail** | O | - | 조직 추적 (모든 계정 API 로깅) |
| **AWS Config** | O | O | 조직 전체 구성 규정 준수 |

### 4.25 암호화되지 않은 리소스를 암호화로 전환

| 리소스 | 전환 방법 | 직접 활성화 가능? |
|---|---|---|
| **EBS 볼륨** | 스냅샷 → 암호화된 스냅샷 복사 → 복원 또는 **계정 기본 암호화** 활성화 | X (기존 볼륨 불가) |
| **RDS DB** | 스냅샷 → 암호화된 스냅샷 복사 → 새 인스턴스 복원 | X (기존 인스턴스 불가) |
| **S3 객체** | S3 Inventory → S3 Batch Operations COPY (SSE-KMS 지정) | X (기존 객체 개별 재암호화) |
| **EFS** | 암호화된 새 EFS 생성 → DataSync로 복사 | X |

> **공통 패턴**: 암호화되지 않은 리소스는 **직접 암호화 활성화 불가** → **스냅샷/복사 → 암호화된 새 리소스 복원** 패턴

---

## 5. 시험 신호어 → 정답 매핑

| # | 신호어 / 키워드 | → 정답 |
|---|---|---|
| 1 | "비밀번호 **자동 교체**", "RDS 자격 증명 교체" | **Secrets Manager** |
| 2 | "설정값 저장", "**비용 최소**", "교체 불필요" | **SSM Parameter Store** (표준 무료) |
| 3 | "FIPS 140-2 Level 3", "AWS도 키 접근 불가" | **CloudHSM** |
| 4 | "S3 **PII** 자동 탐지" | **Macie** |
| 5 | "악성 IP 통신", "이상 API 호출 탐지", "에이전트 불필요" | **GuardDuty** |
| 6 | "EC2/컨테이너 **CVE 취약점 스캔**" | **Inspector** |
| 7 | "탐지된 사건 **근본 원인 조사**·시각화" | **Detective** |
| 8 | "여러 보안 서비스 결과 **단일 대시보드**" | **Security Hub** |
| 9 | "L7 웹 방화벽", "**SQLi/XSS**", "속도 제한" | **WAF** |
| 10 | "L3/L4 **DDoS 무료** 기본 방어" | **Shield Standard** |
| 11 | "L7 DDoS + **DRT** + 요금 급증 보호" | **Shield Advanced** |
| 12 | "VPC 경계 **도메인 필터링**", "IPS" | **Network Firewall** |
| 13 | "Organizations 전체 **WAF/SG 중앙 관리**" | **Firewall Manager** |
| 14 | "특정 악성 IP **차단**" (Allow만인 SG 불가) | **NACL** 또는 **WAF IP 매치** |
| 15 | "**HTTPS 인증서 무료** + 자동 갱신" | **ACM** 공인 인증서 |
| 16 | "CloudFront TLS 인증서" | **ACM us-east-1** |
| 17 | "저장 데이터 암호화 + 키 감사 + 연간 자동 교체" | **SSE-KMS 고객 관리형 키** |
| 18 | "KMS 요청 비용 절감 + 암호화 유지" | **S3 Bucket Key** |
| 19 | "두 리전에서 **동일 키**로 암호화" | **KMS Multi-Region Key** |
| 20 | "AWS 외부에서 키 관리 + 규제" | **KMS XKS** 또는 **클라이언트 측 암호화** |
| 21 | "EBS **기본 암호화** 강제" | **EC2 계정 속성** (EBS encryption by default) |
| 22 | "암호화된 RDS 스냅샷 **교차 계정 공유**" | 스냅샷 공유 + **KMS 키 정책에 대상 계정 추가** |
| 23 | "규정 준수 감사 증거 자동 수집" | **Audit Manager** |
| 24 | "AWS SOC/ISO/PCI 규정 보고서" | **Artifact** |
| 25 | "타사 가상 방화벽 어플라이언스 투명 삽입" | **Gateway Load Balancer** |
| 26 | "특정 국가만 트래픽 허용" | **WAF Geo Match** |
| 27 | "Aurora 비정상 로그인 시도 탐지" | **GuardDuty RDS Protection** |
| 28 | "보안 데이터 중앙 수집 (OCSF)" | **Amazon Security Lake** |
| 29 | "DBA도 데이터 접근 불가" | **KMS 클라이언트 측 암호화 (CSE)** |
| 30 | "HTTP 플러드 / 봇 요청 속도 제한" | **WAF Rate-based Rule** |

---

## 6. 자주 틀리는 함정

> **⚠️ SG는 Deny 규칙 없음** → 특정 IP 차단은 **NACL** 또는 **WAF**

> **⚠️ NACL은 Stateless** → 인바운드를 허용해도 아웃바운드에서 **임시 포트(1024–65535) 허용** 규칙을 빠뜨리면 응답이 차단됨

> **⚠️ ACM 인증서는 EC2에 직접 설치 불가** → ELB/CloudFront/API Gateway에 부착. EC2에서 SSL을 쓰려면 자체 인증서를 직접 설치하거나 **ALB로 SSL 오프로드**

> **⚠️ CloudFront용 ACM은 반드시 us-east-1** → 다른 리전에서 발급한 인증서는 CloudFront에 연결 불가

> **⚠️ Macie는 S3만** → RDS, DynamoDB, EC2 등 다른 서비스의 데이터는 스캔하지 않음

> **⚠️ GuardDuty는 로그 기반 (에이전트 없음)** → 탐지만 하고 **차단하지 않음**. 차단은 EventBridge → Lambda → WAF/NACL 자동화로 구현

> **⚠️ Inspector는 스캔 기반** → EC2/ECR/Lambda의 소프트웨어 취약점(CVE)만 스캔. 실시간 위협 탐지 아님

> **⚠️ Detective는 조사 도구** → 탐지하지 않음 (탐지 = GuardDuty). 탐지된 사건의 **근본 원인 조사**

> **⚠️ Security Hub는 집계 도구** → 자체적으로 탐지하지 않음. GuardDuty/Inspector/Macie 결과를 **대시보드에 모아서 보여줌**

> **⚠️ KMS는 요청 쿼터 있음** → SSE-KMS로 S3 대량 접근 시 **스로틀링 발생 가능** → S3 Bucket Key로 해결

> **⚠️ Secrets Manager는 자동 교체 지원, Parameter Store는 X** → RDS 자격 증명 자동 교체는 Secrets Manager만 네이티브 지원

> **⚠️ Shield Standard는 무료 자동, Advanced는 $3,000/월** → "무료"와 "비용 보호" 키워드 구분

> **⚠️ WAF는 L7만, Shield는 L3~L7** → SQLi/XSS = WAF, DDoS = Shield

> **⚠️ Network Firewall과 WAF는 다른 계층** → Network Firewall = L3~L7 **VPC 경계** 방화벽 / WAF = L7 **웹 앱** 방화벽

> **⚠️ WAF 연결 대상 제한** → ALB, CloudFront, API GW(REST), AppSync, Cognito User Pool, App Runner에만 연결. **NLB, Global Accelerator, EC2 직접 연결 불가**

> **⚠️ 명시적 Deny는 무엇으로도 뒤집을 수 없음** → IAM 정책 + SCP + 리소스 정책 전부 평가해도 하나라도 Deny가 있으면 거부

> **⚠️ AWS 관리형 KMS 키는 교차 계정 스냅샷 공유 불가** → 키 정책을 수정할 수 없으므로 대상 계정에 권한 부여 불가. **고객 관리형 키** 필요

> **⚠️ Imported Key Material은 자동 로테이션 불가** → "자동 키 교체" 요구 시 imported key는 오답

---

## 7. 대표 문제 풀이 예시

### 예시 1: Secrets Manager vs Parameter Store

> **문제**: 회사가 RDS 데이터베이스 자격 증명을 하드코딩하지 않고 정기적으로 자동 교체해야 합니다. 최소 운영 오버헤드 솔루션은?

**정답**: AWS Secrets Manager에 자격 증명 저장 + 자동 로테이션 활성화 + EC2 IAM 역할로 접근

**함정 보기**: Parameter Store (자동 교체 미지원) / Lambda 환경 변수 (보안 취약) / S3 파일 (중앙 관리 불가)

---

### 예시 2: KMS 키 로테이션

> **문제**: S3 데이터 암호화, 키 매년 자동 교체, CloudTrail로 키 사용 감사, 비용 최소화

**정답**: SSE-KMS (AWS 관리형 키) — 자동 교체, CloudTrail 감사, 고객 관리형 키보다 저렴

**주의**: "키 로테이션 **제어**"가 요구되면 → **고객 관리형 키** (AWS 관리형은 제어 불가)

---

### 예시 3: DDoS 방어

> **문제**: ALB 뒤 EC2, DDoS 공격, 구성 변경 최소, 감사 추적 필요

**정답**: AWS Shield Advanced 구독 + DRT 참여

**함정 보기**: WAF만 (DDoS 전문 방어 아님) / GuardDuty (탐지만, 차단 X) / CloudFront 추가 (구성 변경 큼)

---

### 예시 4: PII 탐지

> **문제**: S3 버킷에서 PII 자동 감지 → 보안팀 이메일 알림

**정답**: Amazon Macie → EventBridge → SNS (이메일 구독)

**함정 보기**: GuardDuty (PII 탐지 기능 없음) / Inspector (EC2 취약점 스캔) / SQS (이메일 전송 불가)

---

### 예시 5: WAF 연결 대상

> **문제**: NLB + API Gateway 구성에서 SQL 주입과 DDoS 방어를 동시에

**정답**: API Gateway에 WAF 연결 (SQL 주입 방어) + NLB에 Shield Advanced (DDoS 방어)

**핵심**: WAF는 NLB에 직접 연결 **불가** → API Gateway에 연결

---

### 예시 6: 보안 서비스 역할 구분

> **문제**: AWS 환경에서 의심스러운 동작 자동 탐지 → WAF 규칙 자동 업데이트

**정답**: GuardDuty (탐지) → EventBridge (필터링) → Lambda (WAF 규칙 조정)

**함정 보기**: Firewall Manager (위협 탐지 아님) / Inspector (실시간 탐지 아님) / Macie (S3 민감 데이터만)

---

### 예시 7: 외부 CA 인증서

> **문제**: 외부 CA 발급 인증서를 ALB에 적용, 매년 교체 필요

**정답**: ACM에 외부 인증서 **Import** → ALB 적용 → EventBridge로 만료 알림 → **수동 교체**

**핵심**: Import 인증서는 ACM 자동 갱신 **불가**. ACM 발급(AWS CA) 인증서만 자동 갱신.

---

### 예시 8: 암호화된 스냅샷 교차 계정 공유

> **문제**: KMS 고객 관리형 키로 암호화된 Aurora 스냅샷을 인수 회사의 AWS 계정과 안전하게 공유해야 합니다.

**정답**: DB 스냅샷 생성 → KMS 키 정책에 대상 계정 추가 → 스냅샷을 대상 계정과 공유

**함정 보기**:
- 암호화되지 않은 스냅샷으로 복사 (보안 저하, 기밀 데이터 부적합)
- AWS 관리형 키 사용 (키 정책 수정 불가 → 교차 계정 공유 불가)
- S3로 내보내기 (RDS 스냅샷 다운로드 불가)

---

### 예시 9: VPC 아웃바운드 도메인 필터링

> **문제**: 프라이빗 서브넷 EC2가 승인된 타사 소프트웨어 리포지토리 URL에만 접근, 나머지 인터넷 차단

**정답**: AWS Network Firewall + 도메인 목록 규칙 그룹

**함정 보기**:
- SG (URL/도메인 기반 필터링 불가, IP와 포트만)
- WAF (아웃바운드 트래픽 제어 불가, 인바운드 웹 트래픽만)
- ALB (아웃바운드 라우팅 불가)

**핵심**: "도메인/URL 기반 아웃바운드 필터링" = **Network Firewall**

---

### 예시 10: Lambda 환경 변수 암호화

> **문제**: Lambda 함수 환경 변수를 개발자가 평문으로 볼 수 없게 해야 합니다.

**정답**: KMS 키 생성 → Lambda 함수 **암호화 도우미(encryption helpers)** 활성화

**함정 보기**:
- ACM 인증서 (TLS 인증서, 환경 변수 암호화 아님)
- CloudHSM (과도한 솔루션, 비용 높음)
- EC2 배포 (Lambda의 서버리스 이점 포기)

---

### 예시 11: NIST/PCI DSS 규정 준수 모니터링

> **문제**: 수백 개 AWS 계정에서 NIST/PCI DSS 보안 통제 상태를 중앙 모니터링, 감사인에게 증거 제공

**정답**: AWS Security Hub (위임 관리자 계정) + NIST/PCI DSS 표준 활성화

**함정 보기**:
- GuardDuty (위협 탐지, 규정 준수 표준 검사 아님)
- Inspector (소프트웨어 취약점 스캔, 규정 준수 표준 아님)
- CloudTrail (API 로깅, 규정 준수 대시보드 아님)

---

### 예시 12: SSL 오프로드로 성능 개선

> **문제**: EC2 인스턴스의 SSL 암호화/복호화로 CPU 최대 한도. 성능 개선 방법은?

**정답**: SSL 인증서를 ACM에 **Import** → HTTPS 리스너가 있는 **ALB 생성** → SSL 종료를 ALB로 오프로드

**핵심**: ACM 인증서는 EC2에 직접 설치 불가 → ALB/NLB에서 SSL 종료. 자체 인증서이므로 ACM에 "Import"

---

## 8. 방어 계층별 서비스 매핑 (심층 방어 전략)

SAA-C03에서는 **심층 방어(Defense in Depth)** 원칙에 따라 여러 계층에 걸쳐 보안 서비스를 배치하는 문제가 출제된다. 각 계층에서 어떤 서비스가 역할을 하는지 한눈에 파악해야 한다.

```
┌─────────────────────────────────────────────────────┐
│                    엣지 계층                          │
│  CloudFront (DDoS 흡수) + WAF (L7 필터링)            │
│  Shield Standard/Advanced (L3/L4 DDoS)              │
│  Route 53 (DNS 라우팅, 헬스 체크)                     │
├─────────────────────────────────────────────────────┤
│                  네트워크 계층                         │
│  VPC + 서브넷 분리 (퍼블릭/프라이빗)                    │
│  NACL (서브넷 단위, Stateless, Allow+Deny)           │
│  Security Group (ENI 단위, Stateful, Allow만)        │
│  Network Firewall (VPC 경계, IPS, 도메인 필터링)      │
│  VPC Endpoint (S3/DynamoDB 게이트웨이, PrivateLink)   │
├─────────────────────────────────────────────────────┤
│                애플리케이션 계층                        │
│  ALB + WAF (SQL 주입/XSS 방어)                       │
│  API Gateway + WAF (API 보호, 사용량 계획)             │
│  ACM (TLS 인증서 — 전송 중 암호화)                     │
├─────────────────────────────────────────────────────┤
│                  데이터 계층                           │
│  KMS (저장 시 암호화 — EBS/RDS/S3/EFS)               │
│  CloudHSM (FIPS 140-2 Level 3, 전용 HSM)            │
│  Secrets Manager (자격 증명 자동 교체)                  │
│  Parameter Store (설정값 저장)                         │
├─────────────────────────────────────────────────────┤
│                탐지·모니터링 계층                       │
│  GuardDuty (위협 탐지)                                │
│  Inspector (취약점 스캔)                               │
│  Macie (S3 민감 데이터 분류)                           │
│  Detective (사건 조사)                                │
│  Security Hub (결과 집계 대시보드)                      │
│  CloudTrail (API 감사 로그)                           │
│  Config (구성 규정 준수 모니터링)                       │
├─────────────────────────────────────────────────────┤
│                거버넌스 계층                            │
│  Organizations + SCP (권한 상한)                      │
│  Firewall Manager (다중 계정 보안 정책 중앙 관리)       │
│  Audit Manager (감사 증거 자동 수집)                   │
│  Artifact (AWS 규정 보고서)                            │
└─────────────────────────────────────────────────────┘
```

### 방어 계층별 시험 문제 접근법

| 문제 키워드 | 해당 계층 | 1순위 서비스 |
|---|---|---|
| "웹 공격 방어 (SQLi/XSS)" | 엣지/애플리케이션 | **WAF** |
| "DDoS 공격 방어" | 엣지 | **Shield** (Standard/Advanced) |
| "특정 IP 차단" | 네트워크 | **NACL** 또는 **WAF IP Set** |
| "VPC 아웃바운드 도메인 제어" | 네트워크 | **Network Firewall** |
| "저장 데이터 암호화" | 데이터 | **KMS** |
| "전송 중 암호화" | 애플리케이션 | **ACM** (TLS 인증서) |
| "자격 증명 자동 교체" | 데이터 | **Secrets Manager** |
| "위협 탐지" | 탐지 | **GuardDuty** |
| "취약점 스캔" | 탐지 | **Inspector** |
| "PII 발견" | 탐지 | **Macie** |
| "보안 결과 집계" | 탐지 | **Security Hub** |
| "다중 계정 보안 정책" | 거버넌스 | **Firewall Manager** |

---

## 9. 연관 카테고리

| 연관 주제 | 학습 노트 | 연관 포인트 |
|---|---|---|
| IAM · 거버넌스 (SCP, Identity Center) | [19-identity-and-governance.md](19-identity-and-governance.md) | IAM 정책 평가, SCP 가드레일, 교차 계정 접근 |
| VPC (SG/NACL 상세, VPC Endpoint) | [17-vpc.md](17-vpc.md) | SG vs NACL 심층, VPC Flow Logs, PrivateLink |
| 모니터링 (CloudTrail 감사) | [14-monitoring.md](14-monitoring.md) | CloudTrail 감사 로그, CloudWatch 알람, Config 규칙 |
| S3 (Object Lock, 암호화 방식) | [06-s3.md](06-s3.md) | SSE-S3/SSE-KMS/SSE-C, Object Lock Compliance/Governance, Bucket Key |
