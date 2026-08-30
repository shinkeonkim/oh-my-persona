## Question

회사는 TCP 기반 애플리케이션을 회사의 VPC로 마이그레이션할 계획입니다. 애플리케이션은 회사 데이터 센터의 하드웨어 어플라이언스를 통해 비표준 TCP 포트에서 공개적으로 액세스할 수 있습니다. 이 퍼블릭 엔드포인트는 짧은 대기 시간으로 초당 최대 300만 개의 요청을 처리할 수 있습니다. 회사는 AWS의 새로운 퍼블릭 엔드포인트에 대해 동일한 수준의 성능을 요구합니다.
이 요구 사항을 충족하기 위해 솔루션 설계자는 무엇을 권장해야 합니까?

- [ ] A. NLB(Network Load Balancer)를 배포합니다. 애플리케이션에 필요한 TCP 포트를 통해 공개적으로 액세스할 수 있도록 NLB를 구성합니다.
- [ ] B. ALB(Application Load Balancer)를 배포합니다. 애플리케이션에 필요한 TCP 포트를 통해 공개적으로 액세스할 수 있도록 ALB를 구성합니다.
- [ ] C. 애플리케이션에 필요한 TCP 포트를 수신하는 Amazon CloudFront 배포를 배포합니다. Application Load Balancer를 원본으로 사용합니다.
- [ ] D. 애플리케이션에 필요한 TCP 포트로 구성된 Amazon API Gateway API를 배포합니다. 요청을 처리하기 위해 프로비저닝된 동시성을 사용하여 AWS Lambda 함수를 구성합니다.

## Answer

정답: A

## Explanation

NLB(Network Load Balancer)는 OSI 모델 4계층(전송 계층)에서 작동하며, 비표준 TCP 포트를 포함한 모든 TCP 트래픽을 지원합니다. NLB는 초당 수백만 건의 연결을 처리할 수 있으며, 극도로 낮은 지연 시간(마이크로초 수준)을 제공합니다. 기존 하드웨어 어플라이언스가 초당 300만 건의 요청을 저지연으로 처리했던 것과 동등한 성능을 AWS에서 제공할 수 있는 가장 적합한 서비스입니다. NLB는 정적 IP 주소도 제공하여 DNS 기반 접근이 용이합니다.

오답 분석

B: ALB(Application Load Balancer)는 HTTP/HTTPS(7계층) 트래픽에 최적화되어 있으며, 비표준 TCP 포트의 원시(raw) TCP 트래픽을 처리하는 용도로는 NLB보다 적합하지 않습니다. ALB는 HTTP 헤더 파싱 등 7계층 처리 오버헤드가 있어 NLB보다 지연 시간이 높습니다.

C: Amazon CloudFront는 HTTP/HTTPS 기반 콘텐츠 전송 네트워크(CDN)이며, HTTP(80, 8080, 8888) 및 HTTPS(443, 8443) 등 제한된 포트의 HTTP/HTTPS 트래픽만 지원합니다. 임의의 비표준 TCP 포트의 원시 TCP 트래픽을 직접 수신하는 것은 지원하지 않습니다. CloudFront는 정적/동적 웹 콘텐츠 가속에 적합하며, 원시 TCP 트래픽 처리에는 부적합합니다.

D: Amazon API Gateway는 RESTful API 및 WebSocket API를 관리하기 위한 서비스로, HTTP/HTTPS 기반 API 요청 처리에 적합합니다. 비표준 TCP 포트의 원시 TCP 트래픽을 처리할 수 없으며, Lambda의 동시 실행 제한(기본 1,000, 증가 가능)으로 초당 300만 요청 처리에 한계가 있습니다.

