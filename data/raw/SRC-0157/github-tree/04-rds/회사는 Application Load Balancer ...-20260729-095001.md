## Question

회사는 Application Load Balancer 뒤의 Amazon EC2 인스턴스에서 전자상거래 애플리케이션을 실행합니다. 인스턴스는 여러 가용 영역에 걸쳐 Amazon EC2 Auto Scaling 그룹에서 실행됩니다. Auto Scaling 그룹은 CPU 사용률 지표를 기반으로 확장됩니다. 전자 상거래 애플리케이션은 대규모 EC2 인스턴스에서 호스팅되는 MySQL 8.0 데이터베이스에 트랜잭션 데이터를 저장합니다.
애플리케이션 로드가 증가하면 데이터베이스 성능이 빠르게 저하됩니다. 애플리케이션은 쓰기 트랜잭션보다 더 많은 읽기 요청을 처리합니다. 회사는 고가용성을 유지하면서 예측할 수 없는 읽기 워크로드의 수요를 충족하기 위해 데이터베이스를 자동으로 확장하는 솔루션을 원합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 리더 및 컴퓨팅 기능을 위해 단일 노드와 함께 Amazon Redshift를 사용합니다.
- [ ] B. 단일 AZ 배포와 함께 Amazon RDS를 사용합니다. Amazon RDS를 구성하여 다른 가용 영역에 리더 인스턴스를 추가합니다.
- [ ] C. 다중 AZ 배포와 함께 Amazon Aurora를 사용합니다. Aurora 복제본으로 Aurora Auto Scaling을 구성합니다.
- [ ] D. EC2 스팟 인스턴스와 함께 Memcached용 Amazon ElastiCache를 사용합니다.

## Answer

정답: C

## Explanation

Amazon Aurora는 Multi-AZ 배포와 함께 Aurora Replicas를 사용하여 고가용성과 자동 읽기 확장을 제공합니다. Aurora Auto Scaling은 읽기 워크로드의 수요에 따라 Aurora Replicas의 수를 자동으로 조정하므로, 예측할 수 없는 읽기 워크로드 증가에 효과적으로 대응할 수 있습니다. Aurora는 MySQL 8.0과 호환되며, 기존 MySQL 데이터베이스에서 마이그레이션이 용이하고 최대 15개의 읽기 전용 복제본을 지원합니다.

오답 분석

A: Amazon Redshift는 OLAP(온라인 분석 처리)용 데이터 웨어하우스 서비스로, 전자상거래 애플리케이션의 OLTP(온라인 트랜잭션 처리) 워크로드에는 적합하지 않습니다.

B: Amazon RDS Single-AZ 배포는 고가용성을 제공하지 않으며, RDS의 리더 인스턴스 추가는 Aurora처럼 자동 확장이 되지 않습니다.

D: Memcached용 ElastiCache는 캐싱 솔루션이며, EC2 스팟 인스턴스는 중단될 수 있어 데이터베이스 워크로드에 적합하지 않습니다. 또한 자동 읽기 확장 기능을 제공하지 않습니다.

