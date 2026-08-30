## Question

회사에는 JSON 문서를 처리하고 그 결과를 온프레미스 SQL 데이터베이스에 출력하는 작은 Python 애플리케이션이 있습니다. 이 애플리케이션은 매일 수천 번 실행됩니다. 회사는 애플리케이션을 AWS 클라우드로 이동하려고 합니다. 이 회사는 확장성을 최대화하고 운영 오버헤드를 최소화하는 고가용성 솔루션이 필요합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. JSON 문서를 Amazon S3 버킷에 넣습니다. 여러 Amazon EC2 인스턴스에서 Python 코드를 실행하여 문서를 처리합니다. 결과를 Amazon Aurora DB 클러스터에 저장합니다.
- [ ] B. JSON 문서를 Amazon S3 버킷에 넣습니다. 문서가 S3 버킷에 도착하면 이를 처리하기 위해 Python 코드를 실행하는 AWS Lambda 함수를 생성합니다. 결과를 Amazon Aurora DB 클러스터에 저장합니다.
- [ ] C. JSON 문서를 Amazon Elastic Block Store (Amazon EBS) 볼륨에 넣습니다. EBS 다중 연결 기능을 사용하여 볼륨을 여러 Amazon EC2 인스턴스에 연결합니다. EC2 인스턴스에서 Python 코드를 실행하여 문서를 처리합니다. Amazon RDS DB 인스턴스에 결과를 저장합니다.
- [ ] D. JSON 문서를 Amazon Simple Queue Service (Amazon SQS) 대기열에 메시지로 배치합니다. Amazon EC2 시작 유형으로 구성된 Amazon Elastic Container Service (Amazon ECS) 클러스터에 Python 코드를 컨테이너로 배포합니다. 컨테이너를 사용하여 SQS 메시지를 처리합니다. Amazon RDS DB 인스턴스에 결과를 저장합니다.

## Answer

정답: B

## Explanation

S3 버킷에 JSON 문서를 저장하면 S3 이벤트 알림으로 Lambda 함수를 자동 트리거하여 문서 단위로 처리합니다. Lambda에서 Python 코드를 실행하고 결과를 Amazon Aurora(MySQL/PostgreSQL 호환 관계형 DB)에 저장합니다. S3 이벤트 트리거로 새 문서가 업로드될 때마다 자동 처리되므로 수천 건의 문서도 병렬로 빠르게 처리됩니다. Aurora는 on-premises SQL 데이터베이스의 관리형 대체재로, 고가용성과 자동 백업을 제공하며 완전 서버리스 아키텍처로 운영 오버헤드가 최소화됩니다.

오답 분석

A: 여러 EC2 인스턴스에서 Python 코드를 실행하면 EC2 인스턴스의 프로비저닝, 관리, 모니터링이 필요합니다. Lambda 서버리스 방식 대비 운영 오버헤드가 크고, Auto Scaling 구성도 추가로 필요합니다.

C: EBS Multi-Attach는 동일 AZ 내 여러 EC2 인스턴스에서 하나의 EBS 볼륨을 공유하는 기능입니다. 파일 단위 처리에는 S3가 더 적합하며, EC2 인스턴스 관리 오버헤드가 발생합니다.

D: SQS 큐에 JSON 문서를 메시지로 저장하고 ECS 컨테이너로 처리하면, ECS 태스크 관리와 컨테이너 이미지 관리 등 추가 운영 복잡성이 발생합니다. SQS 메시지 크기 제한(256KB)도 문제가 될 수 있습니다.

