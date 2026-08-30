## Question

한 전자상거래 회사가 AWS에서 하루에 하나의 거래 웹사이트를 시작하려고 합니다. 매일 24시간 동안 정확히 하나의 제품이 판매됩니다. 이 회사는 사용량이 많은 시간에 밀리초 대기 시간으로 시간당 수백만 건의 요청을 처리할 수 있기를 원합니다. 최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. Amazon S3를 사용하여 다른 S3 버킷에서 전체 웹 사이트를 호스팅합니다. Amazon CloudFront 배포를 추가합니다. S3 버킷을 배포의 원본으로 설정합니다. 주문 데이터를 Amazon S3에 저장합니다.
- [ ] B. 여러 가용 영역의 Auto Scaling 그룹에서 실행되는 Amazon EC2 인스턴스에 전체 웹 사이트를 배포합니다. ALB(Application Load Balancer)를 추가하여 웹 사이트 트래픽을 분산합니다. 백엔드 API에 대해 다른 ALB를 추가합니다. MySQL용 Amazon RDS에 데이터를 저장합니다.
- [ ] C. 전체 애플리케이션을 마이그레이션하여 컨테이너에서 실행합니다. Amazon Elastic Kubernetes Service(Amazon EKS)에서 컨테이너를 호스팅합니다. Kubernetes ClusterAutoscaler를 사용하여 팟(Pod) 수를 늘리거나 줄여 트래픽의 버스트를 처리합니다. MySQL용 Amazon RDS에 데이터를 저장합니다.
- [ ] D. Amazon S3 버킷을 사용하여 웹 사이트의 정적 콘텐츠를 호스팅합니다. Amazon CloudFront 배포를 배포합니다. S3 버킷을 오리진으로 설정합니다. 백엔드 API에 Amazon API Gateway 및 AWS Lambda 함수를 사용합니다. Amazon DynamoDB에 데이터를 저장합니다.

## Answer

정답: D

## Explanation

S3 정적 웹 호스팅 + CloudFront CDN으로 정적 콘텐츠를 글로벌 에지 로케이션에서 밀리초 지연시간으로 제공하고, API Gateway + Lambda로 백엔드 API를 서버리스로 처리합니다. DynamoDB는 on-demand 모드로 시간당 수백만 요청에 자동 확장되며 단일 자릿수 밀리초 응답 시간을 보장합니다. 전체 아키텍처가 서버리스이므로 서버 유지보수나 패칭이 불필요하여 운영 오버헤드가 최소화됩니다. 이 구성은 AWS Well-Architected 서버리스 웹 애플리케이션의 표준 패턴입니다.

오답 분석

A: S3만으로는 백엔드 주문 처리 로직을 구현할 수 없습니다. S3는 정적 파일 호스팅용이며, 주문 데이터를 S3에 저장하는 것은 트랜잭션 처리와 실시간 쿼리에 부적합합니다.

B: EC2 인스턴스 기반 아키텍처는 서버 관리, OS 패칭, Auto Scaling 구성 등 상당한 운영 오버헤드가 발생합니다. RDS도 데이터베이스 유지보수가 필요하여 '최소 운영 오버헤드' 요구사항에 부합하지 않습니다.

C: Amazon EKS는 Kubernetes 클러스터 관리, 노드 그룹 관리, pod 스케줄링 등 높은 운영 복잡성을 수반합니다. RDS와 함께 사용하면 서버리스 대비 운영 오버헤드가 크게 증가합니다.

