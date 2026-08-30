## Question

한 회사가 Amazon DynamoDB 테이블에 방대한 양의 데이터를 보유하고 있습니다. 대량의 데이터가 매일 한 번씩 테이블에 추가됩니다. 이 회사는 DynamoDB에 있는 모든 기존 및 미래 데이터를 장기적으로 분석에 사용할 수 있는 솔루션을 원합니다.
어떤 솔루션이 운영 오버헤드를 최소화하면서 이러한 요구 사항을 충족합니까?

- [ ] A. DynamoDB 증분 내보내기를 Amazon S3로 구성합니다.
- [ ] B. Amazon DynamoDB Streams를 구성하여 Amazon S3에 레코드를 씁니다.
- [ ] C. Amazon EMR을 구성하여 DynamoDB 데이터를 Amazon S3에 복사합니다.
- [ ] D. Amazon EMR을 구성하여 DynamoDB 데이터를 Hadoop 분산 파일 시스템(HDFS)에 복사합니다.

## Answer

정답: A

## Explanation

DynamoDB 증분 내보내기(Incremental Export)는 이전 내보내기 이후 변경된 데이터만 자동으로 Amazon S3에 내보냅니다. 첫 번째 전체 내보내기로 기존 데이터를 포함하고, 이후 매일 증분 내보내기로 새 데이터를 추가합니다. 완전 관리형 기능으로 운영 오버헤드가 최소화되며, 테이블의 프로비저닝된 읽기 용량에 영향을 주지 않습니다.

오답 분석

B: DynamoDB Streams는 테이블 변경 사항만 캡처하며 기존에 저장된 데이터를 내보내지 않습니다. 또한 Streams에서 S3로 직접 쓰는 내장 기능이 없어 별도의 처리 로직이 필요합니다.

C: Amazon EMR을 사용하여 DynamoDB 데이터를 S3에 복사하려면 EMR 클러스터를 프로비저닝하고 관리해야 하므로 운영 오버헤드가 크며, DynamoDB의 읽기 용량을 소비합니다.

D: Amazon EMR + HDFS 조합은 클러스터 관리 오버헤드가 크고, HDFS는 S3보다 장기 데이터 분석 저장소로 비용 효율적이지 않으며 내구성도 낮습니다.

