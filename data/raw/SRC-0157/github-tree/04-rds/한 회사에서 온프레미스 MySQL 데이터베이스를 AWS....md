## Question

한 회사에서 온프레미스 MySQL 데이터베이스를 AWS로 이전하려고 합니다. 데이터베이스는 클라이언트 측 애플리케이션에서 정기적으로 가져오기를 허용하므로 쓰기 작업의 양이 많아집니다. 회사에서는 트래픽 양으로 인해 애플리케이션 내에서 성능 문제가 발생할 수 있다는 점을 우려하고 있습니다.
솔루션 아키텍트는 AWS에서 아키텍처를 어떻게 설계해야 합니까?

- [ ] A. 프로비저닝된 IOPS SSD 스토리지를 사용하여 MySQL DB 인스턴스용 Amazon RDS를 프로비저닝합니다. Amazon CloudWatch를 사용하여 쓰기 작업 지표를 모니터링합니다. 필요한 경우 프로비저닝된 IOPS를 조정합니다.
- [ ] B. 범용 SSD 스토리지를 갖춘 MySQL DB 인스턴스용 Amazon RDS를 프로비저닝합니다. DB 인스턴스 앞에 Amazon ElastiCache 클러스터를 배치합니다. 대신 ElastiCache를 쿼리하도록 애플리케이션을 구성합니다.
- [ ] C. 메모리 최적화 인스턴스 유형으로 Amazon DocumentDB(MongoDB 호환) 인스턴스를 프로비저닝합니다. 성능 관련 문제가 있는지 Amazon CloudWatch를 모니터링합니다. 필요한 경우 인스턴스 클래스를 변경합니다.
- [ ] D. 범용 성능 모드에서 Amazon Elastic File System(Amazon EFS) 파일 시스템을 프로비저닝합니다. IOPS 병목 현상이 있는지 Amazon CloudWatch를 모니터링합니다. 필요한 경우 프로비저닝된 처리량 성능 모드로 변경합니다.

## Answer

정답: A

## Explanation

쓰기 작업이 많은 MySQL 데이터베이스를 AWS로 마이그레이션할 때, Amazon RDS for MySQL에 프로비저닝된 IOPS SSD(io1/io2) 스토리지를 사용하면 일관되고 높은 I/O 성능을 제공할 수 있습니다. 프로비저닝된 IOPS는 스토리지 성능을 세밀하게 제어할 수 있으며, Amazon CloudWatch를 통해 쓰기 작업 지표를 모니터링하고 필요에 따라 IOPS를 조정할 수 있어 쓰기 집약적 워크로드에 가장 적합합니다. 이는 MySQL 호환성을 유지하면서 성능 문제를 해결하는 가장 직접적인 방법입니다.

오답 분석

B: 범용 SSD는 버스트 방식으로 IOPS를 제공하므로 지속적인 높은 쓰기 작업에는 부적합합니다. 또한 ElastiCache는 읽기 캐싱에 주로 사용되며, 쓰기 작업의 성능 문제를 해결하지 못합니다.

C: Amazon DocumentDB는 MongoDB 호환 서비스로, MySQL 데이터베이스를 직접 마이그레이션할 수 없습니다. 스키마 변환과 애플리케이션 코드 변경이 필요합니다.

D: Amazon EFS는 파일 스토리지 서비스이며 관계형 데이터베이스 워크로드에는 적합하지 않습니다.

