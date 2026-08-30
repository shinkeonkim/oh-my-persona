## Question

회사의 데이터 플랫폼은 Amazon Aurora MySQL 데이터베이스를 사용합니다. 데이터베이스에는 다양한 가용 영역에 걸쳐 여러 읽기 전용 복제본과 여러 DB 인스턴스가 있습니다. 사용자들은 최근 데이터베이스에서 연결이 너무 많다는 오류를 보고했습니다. 회사에서는 읽기 전용 복제본이 기본 작성자로 승격될 때 장애 조치 시간을 20% 단축하려고 합니다.
이 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 다중 AZ 클러스터 배포를 통해 Aurora에서 Amazon RDS로 전환합니다.
- [ ] B. Aurora 데이터베이스 앞에 Amazon RDS 프록시를 사용합니다.
- [ ] C. 읽기 연결을 위해 DynamoDB Accelerator(DAX)를 사용하여 Amazon DynamoDB로 전환합니다.
- [ ] D. 재배치 기능이 있는 Amazon Redshift로 전환합니다.

## Answer

정답: B

## Explanation

Amazon RDS Proxy는 Aurora MySQL 데이터베이스 앞에 배치하여 두 가지 문제를 동시에 해결합니다. 첫째, 연결 풀링을 통해 '연결이 너무 많다'는 오류를 해결하고, 둘째, 장애 조치 시 RDS Proxy가 새로운 기본 인스턴스로의 연결을 자동으로 관리하여 장애 조치 시간을 크게 단축합니다. AWS 문서에 따르면 RDS Proxy는 장애 조치 시 애플리케이션 연결을 유지하면서 대기 인스턴스로 자동 전환합니다.

오답 분석

A: Amazon RDS Multi-AZ 클러스터 배포로 전환하면 Aurora의 공유 스토리지 아키텍처와 같은 이점을 잃게 됩니다. 또한 연결 관리 문제를 해결하지 못하며 Aurora에서 RDS로의 전환은 성능 저하를 초래할 수 있습니다.

C: Amazon DynamoDB로 전환하면 기존 관계형 데이터 모델과 쿼리를 완전히 재설계해야 하며, DAX는 DynamoDB 전용 캐시 솔루션이므로 Aurora와 함께 사용할 수 없습니다.

D: Amazon Redshift는 데이터 웨어하우스 솔루션으로, OLTP 워크로드에 적합하지 않으며 연결 관리 문제나 장애 조치 시간 단축과는 관련이 없습니다.

