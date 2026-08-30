# 16. 보안 & 규정 준수 — GuardDuty, Inspector, Macie, WAF, Shield, KMS, Secrets Manager

> **CLF-C02 매핑**: Domain 2 — Security and Compliance (30%) — Task 2.3 (보안 서비스), Task 2.4 (컴플라이언스)
> **폴더 문제 수**: 약 54개 (Domain 2 최대 비중)
> **핵심 목표**: **위협 탐지 3인방 (GuardDuty/Inspector/Macie)** 정확한 구별, **DDoS (Shield) vs 웹 방화벽 (WAF)**, **암호화 3서비스 (KMS/CloudHSM/ACM)**, **자격 증명 관리 (Secrets Manager vs STS vs Cognito)**, **규정 준수 (Artifact)**

> ⚠️ **CLF-C02 강조**: 보안 도메인 30% 최대 비중. 서비스 목적 반사적으로 매칭 필요.

---

## 1. 보안 서비스 결정 트리

| 요구사항 | 정답 서비스 |
|---|---|
| **위협 탐지** (계정/네트워크/워크로드 이상 행동) | **Amazon GuardDuty** |
| **EC2/컨테이너/Lambda 취약점 스캔** | **Amazon Inspector** |
| **S3 민감 데이터 자동 식별/분류** | **Amazon Macie** |
| **SQL 인젝션 / XSS / 지리 차단** (웹 애플리케이션) | **AWS WAF** |
| **DDoS 방어 (기본)** | **AWS Shield Standard** (무료) |
| **DDoS 방어 (고급, 네트워크 계층 심층)** | **AWS Shield Advanced** |
| **암호화 키 관리** (EBS/S3/RDS 등) | **AWS KMS** |
| **하드웨어 수준 키 보호** (전용 HW) | **AWS CloudHSM** |
| **SSL/TLS 인증서 관리** | **AWS Certificate Manager (ACM)** |
| **자격 증명/암호 안전 저장 + 자동 교체** | **AWS Secrets Manager** |
| **임시 보안 자격 증명** (assume role) | **AWS STS** |
| **모바일/웹 앱 사용자 인증/가입** | **Amazon Cognito** |
| **규정 준수 보고서 (AOC/SOC/PCI/ISO)** | **AWS Artifact** |
| **보안 알림 통합 대시보드 (CSPM)** | **AWS Security Hub** |
| **보안 조사 분석** | **Amazon Detective** |
| **방화벽 정책 중앙 관리 (여러 계정/리소스)** | **AWS Firewall Manager** |

---

## 2. 위협 탐지 3인방 — 대상별 정확한 구별 (최다 출제)

| 서비스 | 대상 | 목적 | 특징 |
|---|---|---|---|
| **Amazon GuardDuty** | **계정 / 네트워크 / 워크로드** | **위협 탐지 (이상 행동)** | ML + 위협 인텔리전스, 24/7 자동 모니터링 |
| **Amazon Inspector** | **EC2 / 컨테이너 이미지 / Lambda** | **취약점 스캔 (CVE)** | 사전 정의 평가 템플릿, 자동 검색 + 지속 스캔 |
| **Amazon Macie** | **S3 데이터** | **민감 데이터 (PII/PHI/자격 증명)** 자동 식별 | ML 기반 분류, 지적 재산 보호 |

### 시나리오 매칭 (반사적으로)
| 시나리오 문구 | 정답 |
|---|---|
| "AWS 워크로드 위협 자동 모니터링" | **GuardDuty** |
| "악성 활동, 이상 API 호출 탐지" | **GuardDuty** |
| "EC2 인스턴스 소프트웨어 취약점 스캔" | **Inspector** |
| "사전 정의 평가 템플릿으로 EC2 점검" | **Inspector** |
| "지속적 자동 취약점 스캔" | **Inspector** |
| "S3 민감 데이터 검색/보호" | **Macie** |
| "지적 재산 자동 인식/분류" | **Macie** |
| "PII/PHI/개인 정보 식별" | **Macie** |

### 함정: 세 서비스의 역할 절대 바꾸지 말 것
- ❌ Macie로 EC2 취약점 스캔 → **Inspector**
- ❌ Inspector로 S3 민감 데이터 → **Macie**
- ❌ GuardDuty로 취약점 스캔 → **Inspector**

---

## 3. 웹 & 네트워크 방어 — WAF vs Shield vs Firewall Manager

| 서비스 | 계층 | 목적 | 대상 |
|---|---|---|---|
| **AWS WAF** | **Layer 7 (HTTP)** | **SQL 인젝션, XSS, 봇넷, 지리 차단** | CloudFront, ALB, API Gateway, AppSync |
| **AWS Shield Standard** | Layer 3/4 (네트워크) | **기본 DDoS 방어** | 모든 AWS 리소스 (**무료**) |
| **AWS Shield Advanced** | Layer 3/4/7 | **고급 DDoS 방어**, 실시간 가시성 | 유료 ($3,000/월), DDoS 대응 팀 (DRT) |
| **AWS Firewall Manager** | 조직 전체 | **여러 계정/리소스 방화벽 정책 중앙 관리** | WAF/Shield/SG/NACL 통합 |
| **AWS Network Firewall** | Layer 3/4 (VPC) | VPC 전반 네트워크 방화벽 | 사용자 지정 규칙 |

### 시나리오 매칭
| 시나리오 문구 | 정답 |
|---|---|
| "SQL 삽입 공격 차단" | **WAF** |
| "SQL 인젝션 + 상세 로깅" | **WAF** |
| "XSS (교차 사이트 스크립팅) 방어" | **WAF** |
| "특정 국가 사용자 웹사이트 차단 (지리 차단)" | **WAF** |
| "**상시 탐지 + 자동 인라인 완화** DDoS" | **Shield** |
| "DDoS 공격 방어" | **Shield** (일반) |
| "**네트워크 계층** DDoS 심층 방어" | **Shield Advanced** |
| "DDoS 기본 (무료)" | **Shield Standard** |

**핵심**: WAF는 **웹(Layer 7)**, Shield는 **DDoS(네트워크)**. Shield는 SQL 인젝션 방어 X, WAF는 DDoS 방어 X.

---

## 4. 암호화 서비스 3인방

| 서비스 | 특징 |
|---|---|
| **AWS KMS (Key Management Service)** | **암호화 키 생성/관리 (관리형)**, EBS/S3/RDS 등 통합 |
| **AWS CloudHSM** | **하드웨어 보안 모듈 (전용 HW)**, 규정 준수 요구 시 |
| **AWS Certificate Manager (ACM)** | **SSL/TLS 인증서** 관리 |

### 시나리오 매칭
| 시나리오 | 정답 |
|---|---|
| "EBS 암호화" | **KMS** |
| "다양한 AWS 서비스 데이터 암호화" | **KMS** |
| "클라우드 암호화 키 관리 (전용 HW)" | **CloudHSM** |
| "하드웨어 수준 키 보호" | **CloudHSM** |
| "SSL/TLS 인증서" | **ACM** |

### KMS vs CloudHSM 구별
- **KMS**: 완전 관리형, **공유 인프라** (multi-tenant)
- **CloudHSM**: **전용 하드웨어**, 사용자가 직접 관리, FIPS 140-2 Level 3

---

## 5. 자격 증명 관리 서비스

| 서비스 | 대상 | 특징 |
|---|---|---|
| **AWS Secrets Manager** | **DB 자격 증명, API 키** | 안전 저장 + **자동 교체** |
| **AWS STS (Security Token Service)** | AWS 사용자 | **임시 자격 증명** 발급 (assume role) |
| **Amazon Cognito** | **모바일/웹 앱 최종 사용자** | 사용자 가입/인증 |
| **AWS Systems Manager Parameter Store** | 구성 데이터/시크릿 | 저렴 (자동 교체 제한) |
| **AWS KMS** | 암호화 키 | (자격 증명이 아님) |

### 시나리오 매칭
| 시나리오 | 정답 |
|---|---|
| "암호화된 자격 증명 안전 저장/검색" | **Secrets Manager** |
| "RDS DB 자격 증명 + **자동 교체**" | **Secrets Manager** |
| "임시 보안 자격 증명" | **AWS STS** |
| "모바일/웹 앱 사용자 가입/인증" | **Cognito** |
| "가장 안전한 암호 저장" | **Secrets Manager** |

### Secrets Manager vs Parameter Store (자주 헷갈림)
- **Secrets Manager**: **자동 교체 필요** → 고급/비용 높음
- **Parameter Store**: **비용 효율 필요** → 자동 교체 제한 (Systems Manager)

---

## 6. 규정 준수 & 보안 관리 서비스

### AWS Artifact — 규정 준수 문서
- **AWS 발행 보고서/인증서/인가서/제3자 증명서** (온디맨드)
- **AOC (Attestation of Compliance)**, SOC, PCI DSS, ISO, HIPAA, FedRAMP 등
- **셀프 서비스** 즉시 다운로드
- 시나리오: "**규정 준수 보고서 온디맨드 검색**", "감사자에게 제공"

### AWS Security Hub — 보안 통합 대시보드 (CSPM)
- **다양한 AWS 서비스 + 파트너 제품** 알림 표준 형식으로 집계
- **Cloud Security Posture Management (CSPM)**
- GuardDuty, Inspector, Macie 등 통합 결과 표시
- 시나리오: "여러 AWS + 파트너 제품 경고 표준 형식 수집"

### Amazon Detective — 보안 조사
- **보안 이슈 원인 분석 및 조사**
- GuardDuty 발견 사항의 근본 원인 조사

### AWS Firewall Manager
- **조직 전체 방화벽 정책 중앙 관리**
- WAF/Shield/SG/NACL 정책 여러 계정 일괄 적용

---

## 7. 시나리오 → 정답 매핑 (통합)

| 시나리오 문구 | 정답 |
|---|---|
| "위협 자동 모니터링 (계정/네트워크/워크로드)" | **GuardDuty** |
| "EC2 취약점 스캔 (사전 정의 템플릿)" | **Inspector** |
| "EC2 지속적 자동 취약점 스캔" | **Inspector** |
| "S3 민감 데이터 자동 식별/분류" | **Macie** |
| "지적 재산 자동 인식" | **Macie** |
| "SQL 인젝션 차단 + 상세 로깅" | **WAF** |
| "XSS 방어" | **WAF** |
| "특정 국가 웹사이트 접근 차단" | **WAF** |
| "DDoS 방어" | **Shield** |
| "네트워크 계층 DDoS 심층 방어" | **Shield Advanced** |
| "상시 탐지 + 자동 인라인 완화 DDoS" | **Shield** |
| "EBS 암호화" | **KMS** |
| "하드웨어 수준 키 관리" | **CloudHSM** |
| "SSL/TLS 인증서" | **ACM** |
| "암호화된 자격 증명 안전 저장" | **Secrets Manager** |
| "RDS 자격 증명 + 자동 교체" | **Secrets Manager** |
| "임시 보안 자격 증명" | **AWS STS** |
| "모바일/웹 앱 사용자 가입/인증" | **Cognito** |
| "AWS 규정 준수 보고서 온디맨드" | **AWS Artifact** |
| "AOC / SOC / PCI DSS 보고서" | **AWS Artifact** |
| "여러 AWS + 파트너 보안 경고 표준 집계 (CSPM)" | **Security Hub** |
| "여러 계정 방화벽 정책 중앙 관리" | **Firewall Manager** |
| "보안 조사 분석" | **Detective** |

---

## 8. 자주 등장하는 함정 & 오답 패턴

### 함정 1 — "GuardDuty = SQL 인젝션 방어" (❌)
- GuardDuty는 **위협 탐지**. SQL 인젝션은 **WAF**.

### 함정 2 — "GuardDuty = DDoS 방어" (❌)
- GuardDuty는 **탐지**. DDoS 방어는 **Shield**.

### 함정 3 — "WAF = DDoS 방어" (❌)
- WAF는 **웹(Layer 7)**. DDoS는 **Shield**.

### 함정 4 — "Shield = SQL 인젝션 방어" (❌)
- Shield는 **네트워크(Layer 3/4) DDoS**. SQL 인젝션은 **WAF**.

### 함정 5 — "Inspector = S3 민감 데이터" (❌)
- Inspector는 **EC2/컨테이너/Lambda 취약점**. S3는 **Macie**.

### 함정 6 — "Macie = EC2 취약점 스캔" (❌)
- Macie는 **S3 민감 데이터**. EC2는 **Inspector**.

### 함정 7 — "KMS = 하드웨어 보안 모듈" (❌)
- KMS는 **관리형 (공유)**. 하드웨어 전용은 **CloudHSM**.

### 함정 8 — "Certificate Manager = 암호화 키 관리" (❌)
- ACM은 **SSL/TLS 인증서**. 암호화 키는 **KMS**.

### 함정 9 — "Secrets Manager = 규정 준수 문서" (❌)
- Secrets Manager는 **자격 증명 저장**. 규정 준수는 **Artifact**.

### 함정 10 — "Security Hub = 규정 준수 문서" (❌)
- Security Hub는 **보안 알림 통합**. 규정 준수 문서는 **Artifact**.

### 함정 11 — "Cognito = 워크포스 직원 SSO" (❌)
- Cognito는 **최종 사용자 (앱 고객)**. 직원 SSO는 **IAM Identity Center**.

### 함정 12 — "Parameter Store = 자동 교체" (❌)
- Parameter Store는 **자동 교체 제한**. 자동 교체는 **Secrets Manager**.

### 함정 13 — "Detective = 위협 탐지" (❌)
- Detective는 **조사/분석**. 탐지는 **GuardDuty**.

### 함정 14 — "GuardDuty = 취약점 스캔" (❌)
- GuardDuty는 **이상 행동 탐지**. 취약점 스캔은 **Inspector**.

### 함정 15 — "AWS Network Firewall = 웹 방화벽" (❌)
- Network Firewall은 **VPC 네트워크**. 웹은 **WAF**.

### 서비스명 함정 (전혀 다른 서비스)
| 오답 선택지 | 실제 |
|---|---|
| AWS Control Tower | 다중 계정 랜딩 존 |
| Amazon Fraud Detector | 사기 탐지 ML |
| Amazon Pinpoint | 마케팅 커뮤니케이션 |
| AWS Amplify | 웹앱 호스팅 |
| Amazon Cognito | 앱 사용자 인증 (직원 SSO 아님) |
| AWS Resource Access Manager | 리소스 공유 |
| AWS Encryption SDK | 클라이언트 측 암호화 라이브러리 |
| AWS Directory Service | Active Directory |

---

## 9. 시험 대비 팁

1. **위협 탐지 3인방** 대상별 반사적으로:
   - **GuardDuty**: 계정/네트워크/워크로드 **이상 행동 탐지**
   - **Inspector**: EC2/컨테이너/Lambda **취약점 스캔**
   - **Macie**: **S3 민감 데이터** 자동 식별
2. **WAF = SQL 인젝션/XSS/지리 차단 (Layer 7)**, **Shield = DDoS (Layer 3/4)**.
3. **Shield Standard = 무료**, **Shield Advanced = 유료 심층 방어**.
4. **암호화 키 = KMS**, **하드웨어 전용 = CloudHSM**, **SSL/TLS = ACM**.
5. **자격 증명 자동 교체 = Secrets Manager** (Parameter Store는 자동 교체 제한).
6. **임시 자격 증명 = STS**, **앱 사용자 = Cognito**, **직원 SSO = IAM Identity Center** (15번).
7. **규정 준수 문서 = AWS Artifact** (AOC/SOC/PCI/ISO).
8. **보안 통합 대시보드 (CSPM) = Security Hub**.
9. **보안 조사 = Detective**, **위협 탐지 = GuardDuty** (역할 다름).
10. **여러 계정 방화벽 정책 = Firewall Manager**.
11. **지리 차단 = WAF** (Route 53/CloudFront 오답).
12. **Shield는 SQL 인젝션 방어 X**, **WAF는 DDoS 방어 X** — 역할 절대 바꾸지 말 것.

---

## 10. 관련 CLF-C02 태스크 스테이트먼트

- **Task 2.3**: AWS 보안 서비스 및 도구 정의 (GuardDuty, Inspector, Macie, WAF, Shield, KMS, CloudHSM, Secrets Manager, Security Hub, Detective, Firewall Manager)
- **Task 2.4**: AWS 컴플라이언스 및 거버넌스 리소스 (Artifact, AOC, PCI DSS)
- **Task 2.2**: 액세스 관리 (STS, Cognito, KMS)

---

## 11. 다음/이전 폴더와의 연결

- **← 05-shared-responsibility-model**: 데이터 암호화 활성화는 고객 책임 (KMS 도구 활용)
- **← 15-iam**: IAM (User/Role) + STS 임시 자격 + Cognito는 별개 (직원 vs 앱 사용자)
- **← 17-vpc**: NACL/SG (VPC 방화벽) + Firewall Manager로 여러 계정 통합
- **← 19-management-and-governance**: Config (구성 감사) + Security Hub 결합
- **← 23-others**: AWS Artifact의 PCI DSS AOC 보고서 (23번에서 언급)
- **→ 20-well-architected-framework**: Security 기둥 (**추적 가능성 = CloudTrail**, 데이터 보호 = KMS)
