## Question

한 회사에서 MySQL을 사용하는 온프레미스 온라인 트랜잭션 처리(OLTP) 데이터베이스를 AWS 관리형 데이터베이스 관리시스템으로 마이그레이션하려고 합니다. 여러 보고 및 분석 애플리케이션이 주말과 매월 말에 온프레미스 데이터베이스를 많이 사용합니다. 클라우드 기반 솔루션은 주말과 매월 말에 읽기 중심의 급증을 처리할 수 있어야 합니다.
어떤 솔루션이 이러한 요구 사항을 충족할까요?

- [ ] A. 데이터베이스를 Amazon Aurora MySQL 클러스터로 마이그레이션합니다. 복제본을 사용하여 급증을 처리하도록 Aurora Auto Scaling을 구성합니다.
- [ ] B. 데이터베이스를 MySQL을 실행하는 Amazon EC2 인스턴스로 마이그레이션합니다. 임시 스토리지가 있는 EC2 인스턴스 유형을 사용합니다. 인스턴스에 Amazon EBS Provisioned IOPS SSD(io2) 볼륨을 연결합니다.
- [ ] C. 데이터베이스를 Amazon RDS for MySQL 데이터베이스로 마이그레이션합니다. 다중 AZ 배포를 위해 RDS for MySQL 데이터베이스를 구성하고 자동 확장을 설정합니다.
- [ ] D. 데이터베이스에서 Amazon Redshift로 마이그레이션합니다. OLTP 및 분석 애플리케이션 모두에 대한 데이터베이스로 Amazon Redshift를 사용합니다.

## Answer

정답: A

## Explanation

Amazon Aurora MySQL 클러스터로 마이그레이션하고 Aurora Auto Scaling을 구성하면, 읽기 전용 복제본을 자동으로 추가/제거하여 주말과 월말의 읽기 급증을 처리할 수 있습니다. Aurora는 MySQL 호환이므로 마이그레이션이 용이합니다.

오답 분석

B: EC2 인스턴스에서 MySQL을 자체 관리하면 데이터베이스 관리 오버헤드가 높으며, 임시 스토리지(ephemeral storage)는 데이터 지속성을 보장하지 못합니다.

C: RDS for MySQL Multi-AZ는 고가용성을 제공하지만, 읽기 전용 복제본의 자동 확장 기능이 없어 읽기 급증을 자동으로 처리할 수 없습니다.

D: Amazon Redshift는 OLAP(분석) 워크로드에 최적화되어 있으며, OLTP(트랜잭션) 워크로드에는 적합하지 않습니다.

