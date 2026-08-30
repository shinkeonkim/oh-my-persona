## Question

한 회사가 3개의 가용 영역에서 작동하는 AWS 클라우드에서 3계층 웹 애플리케이션을 실행합니다. 애플리케이션 아키텍처에는 Application Load Balancer, 사용자 세션 상태를 호스팅하는 Amazon EC2 웹 서버, EC2 인스턴스에서 실행되는 MySQL 데이터베이스가 있습니다. 회사는 애플리케이션 트래픽이 갑자기 증가할 것으로 예상합니다. 이 회사는 미래의 애플리케이션 용량 수요를 충족하고 3개의 가용 영역 모두에서 고가용성을 보장하기 위해 확장할 수 있기를 원합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 다중 AZ DB 클러스터 배포를 통해 MySQL 데이터베이스를 MySQL용 Amazon RDS로 마이그레이션합니다. 고가용성 Redis용 Amazon ElastiCache를 사용하여 세션 데이터를 저장하고 읽기를 캐시합니다. 세 개의 가용 영역에 있는 Auto Scaling 그룹으로 웹 서버를 마이그레이션합니다.
- [ ] B. 다중 AZ DB 클러스터 배포를 통해 MySQL 데이터베이스를 MySQL용 Amazon RDS로 마이그레이션합니다. 고가용성 Memcached용 Amazon ElastiCache를 사용하여 세션 데이터를 저장하고 읽기를 캐시합니다. 세 개의 가용 영역에 있는 Auto Scaling 그룹으로 웹 서버를 마이그레이션합니다.
- [ ] C. MySQL 데이터베이스를 Amazon DynamoDB로 마이그레이션합니다. DynamoDB Accelerator(DAX)를 사용하여 읽기를 캐시합니다. DynamoDB에 세션 데이터를 저장합니다. 세 개의 가용 영역에 있는 Auto Scaling 그룹으로 웹 서버를 마이그레이션합니다.
- [ ] D. 단일 가용 영역에서 MySQL 데이터베이스를 MySQL용 Amazon RDS로 마이그레이션합니다. 고가용성 Redis용 Amazon ElastiCache를 사용하여 세션 데이터를 저장하고 읽기를 캐시합니다. 세 개의 가용 영역에 있는 Auto Scaling 그룹으로 웹 서버를 마이그레이션합니다.

## Answer

정답: A

## Explanation

MySQL 데이터베이스를 Amazon RDS for MySQL Multi-AZ DB 클러스터로 마이그레이션하면 3개 가용 영역에서 고가용성을 확보할 수 있습니다. ElastiCache for Redis를 사용하면 세션 데이터를 중앙에서 관리하고 데이터베이스 읽기를 캐시하여 성능을 향상시킵니다. Redis는 데이터 지속성과 복제를 지원하여 고가용성을 보장합니다. Auto Scaling 그룹으로 웹 서버를 마이그레이션하면 트래픽 증가에 자동으로 대응할 수 있습니다.

오답 분석

B: Memcached는 데이터 지속성을 지원하지 않으므로, 노드 장애 시 세션 데이터가 손실될 수 있습니다. 고가용성 세션 관리에는 Redis가 더 적합합니다.

C: DynamoDB로의 마이그레이션은 MySQL에서 NoSQL로의 대규모 스키마 변환이 필요하며, DAX는 DynamoDB 전용 캐시입니다. 기존 MySQL 기반 애플리케이션의 변경이 큽니다.

D: 단일 가용 영역의 RDS는 고가용성 요구 사항을 충족하지 못합니다. 3개 가용 영역 모두에서 고가용성이 필요합니다.

