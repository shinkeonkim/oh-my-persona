## Question

전자상거래 회사는 AWS 클라우드에서 분석 애플리케이션을 호스팅합니다. 이 애플리케이션은 매월 약 300MB의 데이터를 생성합니다. 데이터는 JSON 형식으로 저장됩니다. 회사는 데이터 백업을 위한 재해 복구 솔루션을 평가하고 있습니다. 데이터는 필요한 경우 밀리초 단위로 액세스할 수 있어야 하며 데이터는 30일 동안 보관되어야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. Amazon OpenSearch Service(Amazon Elasticsearch Service)
- [ ] B. Amazon S3 Glacier
- [ ] C. Amazon S3 Standard
- [ ] D. PostgreSQL용 Amazon RDS

## Answer

정답: C

## Explanation

매월 약 300MB의 소규모 데이터로, 밀리초 단위의 즉시 접근이 필요하고 30일만 보관하면 되는 요구 사항에 Amazon S3 Standard가 가장 적합합니다. S3 Standard는 밀리초 단위의 첫 바이트 액세스 지연 시간을 제공하며, 99.999999999%의 내구성과 99.99%의 가용성을 보장합니다. 월 300MB의 데이터량에서 S3 Standard의 비용은 거의 무시할 수 있을 만큼 저렴하여 가장 비용 효율적인 재해 복구 솔루션입니다.

오답 분석

A: Amazon OpenSearch Service는 검색 및 분석 엔진으로 전용 클러스터를 프로비저닝해야 하며, 단순 데이터 백업 용도에는 월 수백 달러의 과도한 인프라 비용과 운영 복잡성을 초래합니다.

B: S3 Glacier는 아카이브 스토리지로 밀리초 단위의 즉시 접근이 불가능합니다. Glacier Flexible Retrieval의 긴급 검색도 최소 1-5분이 소요되며, 표준 검색은 3-5시간이 필요합니다.

D: Amazon RDS for PostgreSQL은 관계형 데이터베이스 서비스로 인스턴스 운영 비용이 발생하며, JSON 파일 백업 저장 용도에는 과도한 비용과 관리 부담이 발생합니다.

