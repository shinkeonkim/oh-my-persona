## Question

회사는 AWS에 사용자 디바이스에서 센서 데이터를 수집하는 3계층 환경을 가지고 있습니다. 트래픽은 NLB(Network Load Balancer)를 거쳐 웹 계층용 Amazon EC2 인스턴스로 이동하고 마지막으로 데이터베이스 호출을 수행하는 애플리케이션 계층용 EC2 인스턴스로 이동합니다.
솔루션 설계자는 웹 계층으로 전송되는 데이터의 보안을 개선하기 위해 무엇을 해야 합니까?

- [ ] A. TLS 수신기를 구성하고 NLB에 서버 인증서를 추가합니다.
- [ ] B. AWS Shield Advanced를 구성하고 NLB에서 AWS WAF를 활성화합니다.
- [ ] C. 로드 밸런서를 Application Load Balancer로 변경하고 여기에 AWS WAF를 연결합니다.
- [ ] D. AWS Key Management Service(AWS KMS)를 사용하여 EC2 인스턴스에서 Amazon Elastic Block Store(Amazon EBS) 볼륨을 암호화합니다.

## Answer

정답: A

## Explanation

NLB(Network Load Balancer)에서 TLS 리스너를 구성하고 서버 인증서를 추가하면, 클라이언트(사용자 디바이스)와 NLB 간의 통신이 TLS/SSL로 암호화됩니다. 이는 전송 중(in transit) 데이터의 보안을 직접적으로 향상시키는 방법입니다. NLB는 TLS 종료(TLS Termination)를 기본 지원하며, 포트 443에서 TLS 리스너를 구성하면 클라이언트와의 모든 통신이 암호화됩니다. AWS Certificate Manager(ACM)에서 무료로 발급한 인증서를 NLB에 직접 연결할 수 있으며, ALPN(Application-Layer Protocol Negotiation) 정책을 통해 HTTP/2 등의 프로토콜 협상도 지원합니다. NLB는 TLS 1.0~1.3을 지원하며, 보안 정책(Security Policy)을 선택하여 허용할 TLS 버전과 암호 스위트를 제어할 수 있습니다.

오답 분석

B: AWS Shield Advanced는 DDoS(분산 서비스 거부) 공격 방어 서비스이고, AWS WAF는 SQL 인젝션, XSS 등 웹 애플리케이션 공격을 방어하는 방화벽입니다. 이 두 서비스는 네트워크 및 애플리케이션 보안 위협으로부터 보호하지만, 전송 중 데이터 암호화(TLS/SSL)와는 직접적인 관련이 없습니다. 또한 AWS WAF는 NLB에 직접 연결할 수 없고 ALB, CloudFront, API Gateway, AppSync, Cognito 사용자 풀, App Runner, Verified Access에만 연결 가능합니다.

C: ALB로 변경하고 WAF를 연결하는 것은 7계층 보안(웹 공격 방어)에 도움이 되지만, 문제에서 요구하는 '웹 계층으로 전송되는 데이터의 보안 개선'(전송 중 암호화)을 직접 해결하지 않습니다. WAF는 요청 패턴 필터링을 수행하며 데이터 암호화 기능이 아닙니다. NLB에서 TLS를 구성하는 것이 더 직접적인 해결책입니다.

D: AWS KMS를 사용한 EBS 볼륨 암호화는 저장 중(at rest) 데이터를 보호하는 것이며, 네트워크를 통해 전송되는 데이터(in transit)의 보안과는 완전히 다른 영역입니다. EBS 암호화는 디스크 I/O 수준에서 AES-256 암호화를 적용하지만 네트워크 트래픽에는 영향을 주지 않습니다.

