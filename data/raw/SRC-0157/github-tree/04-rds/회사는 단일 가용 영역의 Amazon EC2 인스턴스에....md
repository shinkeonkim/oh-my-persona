## Question

회사는 단일 가용 영역의 Amazon EC2 인스턴스에서 3계층 웹 애플리케이션을 호스팅합니다. 웹 애플리케이션은 EC2 인스턴스에서 호스팅되는 자체 관리형 MySQL 데이터베이스를 사용하여 Amazon Elastic Block Store(Amazon EBS) 볼륨에 데이터를 저장합니다. MySQL 데이터베이스는 현재 1TB 프로비저닝된 IOPS SSD(io2) EBS 볼륨을 사용합니다. 이 회사는 피크 트래픽에서 읽기 및 쓰기 모두에 대해 1,000 IOPS의 트래픽을 예상합니다.
회사는 두 배의 IOPS 용량을 유지하면서 중단을 최소화하고 성능을 안정화하며 비용을 절감하고자 합니다. 이 회사는 데이터베이스 계층을 가용성이 높고 내결함성이 있는 완전 관리형 솔루션으로 이동하려고 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. io2 Block Express EBS 볼륨이 있는 MySQL DB 인스턴스용 Amazon RDS의 다중 AZ 배포를 사용합니다.
- [ ] B. 범용 SSD(gp2) EBS 볼륨이 있는 MySQL DB 인스턴스용 Amazon RDS의 다중 AZ 배포를 사용합니다.
- [ ] C. Amazon S3 Intelligent-Tiering 액세스 계층을 사용합니다.
- [ ] D. 두 개의 큰 EC2 인스턴스를 사용하여 활성-수동 모드에서 데이터베이스를 호스팅합니다.

## Answer

정답: B

## Explanation

Amazon RDS for MySQL의 Multi-AZ 배포와 범용 SSD(gp2) EBS 볼륨 조합이 가장 비용 효율적입니다. gp2 볼륨은 1TiB(≈1TB) 크기에서 기본 3,072 IOPS를 제공하며(3 IOPS/GiB × 1,024 GiB), 피크 트래픽의 읽기/쓰기 각 1,000 IOPS(총 2,000 IOPS)를 충분히 지원하고 두 배의 IOPS 용량(2,000 IOPS)을 초과하는 여유 용량을 제공합니다. Multi-AZ 배포로 고가용성과 내결함성을 확보하면서, io2 볼륨보다 비용이 낮아 가장 비용 효율적인 완전 관리형 솔루션입니다.

오답 분석

A: io2 Block Express EBS 볼륨은 매우 높은 IOPS를 제공하지만, 1,000 IOPS 수준의 워크로드에는 과도한 사양이며 gp2보다 비용이 높습니다.

C: Amazon S3 Intelligent-Tiering은 객체 스토리지의 비용 최적화 기능이며, 관계형 데이터베이스의 대체 솔루션이 될 수 없습니다.

D: 두 개의 EC2 인스턴스로 활성-수동 데이터베이스를 호스팅하면 데이터베이스 관리, 복제, 장애 조치를 모두 수동으로 관리해야 하므로 완전 관리형 솔루션이 아닙니다.

