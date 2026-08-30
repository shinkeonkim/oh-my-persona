## Question

내장형 NoSQL 데이터베이스가 포함된 회사의 웹 애플리케이션은 ALB(Application Load Balancer) 뒤의 Amazon EC2 인스턴스에서 작동합니다. 이러한 인스턴스는 단일 가용 영역으로 제한된 Amazon EC2 Auto Scaling 그룹 내에 있습니다. 트래픽 증가로 인해 애플리케이션은 고가용성을 달성해야 하며 데이터베이스는 최종 일관성을 유지해야 합니다.
이러한 요구 사항을 충족하면서 운영 오버헤드를 최소화하는 솔루션은 무엇입니까?

- [ ] A. ALB를 Network Load Balancer로 교체하고 내장형 NoSQL 데이터베이스를 EC2 인스턴스의 복제 서비스와 함께 유지합니다.
- [ ] B. ALB를 Network Load Balancer로 교체하고 AWS Database Migration Service(AWS DMS)를 사용하여 내장형 NoSQL 데이터베이스를 Amazon DynamoDB로 마이그레이션합니다.
- [ ] C. EC2 인스턴스의 복제 서비스와 함께 내장된 NoSQL 데이터베이스를 유지하면서 3개의 가용 영역에서 EC2 인스턴스를 활용하도록 Auto Scaling 그룹을 수정합니다.
- [ ] D. 3개의 가용 영역에서 EC2 인스턴스를 활용하고 AWS Database Migration Service(AWS DMS)를 사용하여 내장된 NoSQL 데이터베이스를 Amazon DynamoDB로 마이그레이션하도록 Auto Scaling 그룹을 수정합니다.

## Answer

정답: D

## Explanation

Auto Scaling 그룹을 3개 가용 영역으로 확장하면 단일 AZ 장애 시에도 다른 AZ에서 애플리케이션이 계속 실행되어 고가용성을 확보합니다. 내장형 NoSQL 데이터베이스를 Amazon DynamoDB로 마이그레이션하면, DynamoDB가 최종 일관성(Eventually Consistent) 읽기를 기본 지원하고 여러 AZ에 걸쳐 데이터를 자동 복제하므로 별도의 데이터베이스 복제 관리가 불필요합니다. AWS DMS를 사용하면 마이그레이션 과정이 간소화됩니다.

오답 분석

A: ALB를 NLB로 교체하면 HTTP/HTTPS 계층 7 라우팅 기능(경로 기반, 호스트 기반 라우팅, 헤더 기반 라우팅 등)을 잃게 됩니다. 또한 단일 AZ에서만 인스턴스를 실행하므로 고가용성 문제가 해결되지 않으며, 내장형 NoSQL의 복제도 수동 관리가 필요합니다.

B: NLB로 교체하고 DynamoDB로 마이그레이션하는 것은 데이터베이스 측면에서는 좋지만, Auto Scaling 그룹이 여전히 단일 AZ에 제한되어 있어 고가용성이 보장되지 않습니다. AZ 장애 시 모든 인스턴스가 영향을 받습니다.

C: 3개 AZ로 확장하여 고가용성을 확보하지만, 내장형 NoSQL 데이터베이스의 복제 서비스를 직접 관리해야 합니다. 여러 AZ에 걸친 데이터 복제, 일관성 관리, 장애 복구 등의 운영 오버헤드가 DynamoDB 사용보다 훨씬 높습니다.

