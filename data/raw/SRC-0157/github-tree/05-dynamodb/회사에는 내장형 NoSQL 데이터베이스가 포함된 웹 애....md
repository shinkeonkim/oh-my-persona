## Question

회사에는 내장형 NoSQL 데이터베이스가 포함된 웹 애플리케이션이 있습니다. 애플리케이션은 ALB(Application Load Balancer) 뒤의 Amazon EC2 인스턴스에서 실행됩니다. 인스턴스는 단일 가용 영역의 Amazon EC2 Auto Scaling 그룹에서 실행됩니다.
최근 트래픽이 증가함에 따라 애플리케이션의 가용성이 높아야 하고 데이터베이스가 최종 일관성을 유지해야 합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. ALB를 Network Load Balancer로 교체합니다. EC2 인스턴스의 복제 서비스를 통해 내장형 NoSQL 데이터베이스를 유지 관리합니다.
- [ ] B. ALB를 Network Load Balancer로 교체합니다. AWS Database Migration Service(AWS DMS)를 사용하여 내장형 NoSQL 데이터베이스를 Amazon DynamoDB로 마이그레이션합니다.
- [ ] C. 3개의 가용 영역에서 EC2 인스턴스를 사용하도록 Auto Scaling 그룹을 수정합니다. EC2 인스턴스의 복제 서비스를 통해 내장형 NoSQL 데이터베이스를 유지 관리합니다.
- [ ] D. 세 개의 가용 영역에서 EC2 인스턴스를 사용하도록 Auto Scaling 그룹을 수정합니다. AWS Database Migration Service(AWS DMS)를 사용하여 내장형 NoSQL 데이터베이스를 Amazon DynamoDB로 마이그레이션합니다.

## Answer

정답: D

## Explanation

Auto Scaling 그룹을 3개 가용 영역으로 확장하여 고가용성을 확보하고, AWS DMS를 사용하여 내장형 NoSQL 데이터베이스를 Amazon DynamoDB로 마이그레이션하면 최종 일관성을 제공하면서 운영 오버헤드를 최소화합니다. DynamoDB는 완전관리형이므로 복제를 별도로 관리할 필요가 없습니다.

오답 분석

A: ALB를 NLB로 교체하면 HTTP 기반 라우팅 기능을 잃게 되며, 단일 AZ 문제를 해결하지 못합니다. 이는 해당 시나리오의 요구사항에 적합하지 않습니다.

B: NLB로 교체하고 DynamoDB로 마이그레이션해도 단일 AZ에서만 EC2를 실행하므로 고가용성이 보장되지 않습니다. 이는 해당 시나리오의 요구사항에 적합하지 않습니다.

C: 3개 AZ로 확장하는 것은 좋지만, 내장형 NoSQL의 복제 서비스를 직접 관리하면 운영 오버헤드가 높습니다. 이는 해당 시나리오의 요구사항에 적합하지 않습니다.

