## Question

병원은 환자 기록을 Amazon S3 버킷에 저장해야 합니다. 병원의 규정 준수 팀은 모든 PHI(보호된 건강 정보)가 전송 및 저장 중에 암호화되도록 해야 합니다. 규정 준수 팀은 미사용 데이터에 대한 암호화 키를 관리해야 합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. AWS Certificate Manager(ACM)에서 퍼블릭 SSL/TLS 인증서를 생성합니다. 인증서를 Amazon S3와 연결합니다. AWS KMS 키(SSE-KMS)로 서버 측 암호화를 사용하도록 각 S3 버킷에 대한 기본 암호화를 구성합니다. KMS 키를 관리할 규정 준수 팀을 할당합니다.
- [ ] B. S3 버킷 정책에서 aws:SecureTransport 조건을 사용하여 HTTPS(TLS)를 통한 암호화된 연결만 허용합니다. S3 관리형 암호화 키(SSE-S3)로 서버 측 암호화를 사용하도록 각 S3 버킷에 대한 기본 암호화를 구성합니다. SSE-S3 키를 관리할 규정 준수 팀을 할당합니다.
- [ ] C. S3 버킷 정책에서 aws:SecureTransport 조건을 사용하여 HTTPS(TLS)를 통한 암호화된 연결만 허용합니다. AWS KMS 키(SSE-KMS)로 서버 측 암호화를 사용하도록 각 S3 버킷에 대한 기본 암호화를 구성합니다. KMS 키를 관리할 규정 준수 팀을 할당합니다.
- [ ] D. S3 버킷 정책에서 aws:SecureTransport 조건을 사용하여 HTTPS(TLS)를 통한 암호화된 연결만 허용합니다. Amazon Macie를 사용하여 Amazon S3에 저장된 민감한 데이터를 보호합니다. Macie를 관리할 규정 준수 팀을 지정합니다.

## Answer

정답: C

## Explanation

S3 버킷 정책에서 aws:SecureTransport 조건 키를 사용하여 HTTPS(TLS)를 통한 암호화된 연결만 허용하면 전송 중 암호화가 보장됩니다. 또한 AWS KMS 키(SSE-KMS)로 서버 측 암호화를 S3 버킷의 기본 암호화로 구성하면 저장 시(미사용) 데이터가 자동으로 암호화됩니다. SSE-KMS를 사용하면 규정 준수 팀이 KMS 키의 생성, 순환, 비활성화, 접근 정책을 직접 관리할 수 있어 '암호화 키 관리' 요구 사항을 충족합니다.

오답 분석

A: AWS Certificate Manager(ACM)의 SSL/TLS 인증서는 CloudFront, ALB, API Gateway 등과 연결할 수 있지만, Amazon S3와는 직접 연결할 수 없습니다. S3는 기본적으로 HTTPS 엔드포인트를 제공하며 버킷 정책으로 HTTPS를 강제합니다.

B: SSE-S3(S3 관리형 키)는 Amazon이 암호화 키를 자동으로 관리하므로 규정 준수 팀이 키를 직접 관리할 수 없습니다. '암호화 키를 관리해야 한다'는 요구 사항에 부합하지 않습니다.

D: Amazon Macie는 기계 학습을 사용하여 S3에 저장된 민감한 데이터(PII, PHI 등)를 자동으로 검색하고 분류하는 서비스이며, 데이터 암호화나 암호화 키 관리 기능을 제공하지 않습니다.

