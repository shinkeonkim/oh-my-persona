## Question

한 회사에 AWS에서 호스팅되는 웹사이트가 있습니다. 웹사이트는 HTTP와 HTTPS를 별도로 처리하도록 구성된 ALB(Application Load Balancer) 뒤에 있습니다. 회사는 요청이 HTTPS를 사용하도록 모든 요청을 웹 사이트로 전달하려고 합니다.
솔루션 설계자는 이 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. HTTPS 트래픽만 허용하도록 ALB의 네트워크 ACL을 업데이트합니다.
- [ ] B. URL의 HTTP를 HTTPS로 바꾸는 규칙을 만듭니다.
- [ ] C. ALB에서 리스너 규칙을 생성하여 HTTP 트래픽을 HTTPS로 리디렉션합니다.
- [ ] D. ALB를 SNI(Server Name Indication)를 사용하도록 구성된 Network Load Balancer로 교체합니다.

## Answer

정답: C

## Explanation

Application Load Balancer(ALB)는 리스너 규칙(Listener Rule)을 통해 HTTP 트래픽을 HTTPS로 자동 리다이렉트하는 기능을 기본 제공합니다. HTTP 리스너(포트 80)에 리다이렉트 액션을 설정하면 클라이언트의 HTTP 요청이 자동으로 HTTPS(포트 443)로 전환되어 모든 웹사이트 트래픽이 암호화됩니다. 이 방법은 애플리케이션 코드 변경 없이 ALB 설정만으로 구현 가능하여 가장 효율적입니다.

오답 분석

A: Network ACL은 Layer 4(TCP/UDP) 수준의 트래픽 제어만 가능하며, HTTP를 HTTPS로 리다이렉트하는 기능을 제공하지 않습니다. HTTP 트래픽을 차단하면 리다이렉트 없이 연결이 거부됩니다.

B: URL에서 HTTP를 HTTPS로 교체하는 독립적인 규칙은 ALB에 존재하지 않습니다. 리다이렉트 액션이 올바른 방법입니다.

D: NLB는 Layer 4 로드밸런서로 HTTP/HTTPS 프로토콜 수준의 리다이렉트 기능을 제공하지 않으며, SNI는 여러 TLS 인증서를 지원하는 기능일 뿐 리다이렉트와 무관합니다.

