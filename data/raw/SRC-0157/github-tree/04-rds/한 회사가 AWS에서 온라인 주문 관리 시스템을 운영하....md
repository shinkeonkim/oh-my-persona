## Question

한 회사가 AWS에서 온라인 주문 관리 시스템을 운영하고 있습니다. 이 회사는 지난 5년간의 주문 및 재고 데이터를 Amazon Aurora MySQL 데이터베이스에 저장합니다. 5년 후 재고 데이터를 삭제합니다. 이 회사는 데이터 보관 비용을 최적화하려고 합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. AWS Glue 크롤러를 생성하여 Amazon S3로 데이터를 내보냅니다. AWS Lambda 함수를 생성하여 데이터를 압축합니다.
- [ ] B. Aurora 데이터베이스에서 SELECT INTO OUTFILE S3 쿼리를 사용하여 데이터를 Amazon S3로 내보냅니다. S3 버킷에 S3 수명 주기 규칙을 구성합니다.
- [ ] C. AWS Glue DataBrew 작업을 생성하여 Aurora에서 Amazon S3로 데이터를 마이그레이션합니다. S3 버킷에 S3 수명 주기 규칙을 구성합니다.
- [ ] D. AWS Schema Conversion Tool(AWS SCT)을 사용하여 Aurora에서 Amazon S3로 데이터를 복제합니다. S3 Standard-Infrequent Access(S3 Standard-IA) 스토리지 클래스를 사용합니다.

## Answer

정답: B

## Explanation

Aurora의 SELECT INTO OUTFILE S3 쿼리를 사용하면 데이터베이스에서 직접 Amazon S3로 데이터를 효율적으로 내보낼 수 있습니다. S3 수명 주기 규칙을 구성하면 오래된 데이터를 S3 Glacier 등 저비용 스토리지 클래스로 자동 전환하거나 5년 후 자동 삭제하여 보관 비용을 최적화합니다.

오답 분석

A: AWS Glue 크롤러는 데이터 카탈로그 작성용 서비스이며, 데이터베이스에서 S3로 데이터를 내보내는 기능이 아닙니다. Lambda로 압축하는 것도 추가 복잡성을 유발합니다.

C: AWS Glue DataBrew는 데이터 정제/변환 도구로, 데이터 마이그레이션 목적에는 과도하며 비용이 높습니다.

D: AWS SCT는 데이터베이스 스키마 변환 도구이며, 데이터를 S3로 복제하는 기능이 아닙니다.

