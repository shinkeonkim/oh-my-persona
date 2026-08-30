## Question

회사는 AWS에서 인프라를 실행하고 문서 관리 애플리케이션에 대해 700,000명의 등록된 사용자 기반을 가지고 있습니다. 회사는 대용량 .pdf 파일을 .jpg 이미지 파일로 변환하는 제품을 만들려고 합니다. .pdf 파일의 평균 크기는 5MB입니다. 회사는 원본 파일과 변환된 파일을 보관해야 합니다. 솔루션 설계자는 시간이 지남에 따라 빠르게 증가할 수요를 수용할 수 있는 확장 가능한 솔루션을 설계해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. .pdf 파일을 Amazon S3에 저장합니다. 파일을 .jpg 형식으로 변환하고 Amazon S3에 다시 저장하는 AWS Lambda 함수를 호출하도록 S3 PUT 이벤트를 구성합니다.
- [ ] B. .pdf 파일을 Amazon DynamoDB에 저장합니다. DynamoDB Streams 기능을 사용하여 AWS Lambda 함수를 호출하여 파일을 .jpg 형식으로 변환하고 다시 DynamoDB에 저장합니다.
- [ ] C. Amazon EC2 인스턴스, Amazon Elastic Block Store(Amazon EBS) 스토리지 및 Auto Scaling 그룹을 포함하는 AWS Elastic Beanstalk 애플리케이션에 .pdf 파일을 업로드합니다. EC2 인스턴스의 프로그램을 사용하여 파일을 .jpg 형식으로 변환합니다. .pdf 파일과 .jpg 파일을 EBS 스토어에 저장합니다.
- [ ] D. Amazon EC2 인스턴스, Amazon Elastic File System(Amazon EFS) 스토리지 및 Auto Scaling 그룹이 포함된 AWS Elastic Beanstalk 애플리케이션에 .pdf 파일을 업로드합니다. EC2 인스턴스의 프로그램을 사용하여 파일을 .jpg 형식으로 변환합니다. .pdf 파일과 .jpg 파일을 EBS 스토어에 저장합니다.

## Answer

정답: A

## Explanation

Amazon S3에 PDF 파일을 저장하고 S3 PUT 이벤트로 AWS Lambda 함수를 트리거하여 JPG로 변환한 후 다시 S3에 저장하는 구조입니다. Lambda는 서버리스로 700,000명 사용자의 동시 업로드에도 자동 확장되며, 사용한 만큼만 비용이 발생합니다. S3는 무제한 저장 용량으로 원본 PDF와 변환된 JPG 파일 모두 안정적으로 보관할 수 있으며, 5MB 평균 크기의 파일 처리에 Lambda의 메모리와 실행 시간이 충분합니다.

오답 분석

B: Amazon DynamoDB의 항목 크기 제한은 400KB이므로 평균 5MB의 PDF 파일을 직접 저장할 수 없습니다. DynamoDB는 구조화된 키-값 데이터에 최적화된 데이터베이스이지 파일 스토리지가 아닙니다. DynamoDB Streams를 통한 Lambda 트리거는 가능하지만 근본적으로 저장소 제한 문제가 있습니다.

C: Elastic Beanstalk + EC2 + EBS 조합은 인스턴스 관리, EBS 볼륨 용량 관리 등 운영 복잡성이 있습니다. EBS는 단일 인스턴스에 연결되므로 수평 확장 시 스토리지 공유가 어렵고, 급증하는 수요에 대한 확장성이 S3 + Lambda 대비 제한적이며 비용 효율성도 낮습니다.

D: EFS 스토리지를 언급하면서 EBS 스토어에 저장한다고 설명이 혼재되어 일관성이 없습니다. 또한 Elastic Beanstalk + EC2 기반 솔루션은 서버리스 대비 관리 복잡성과 비용이 증가하며, 빠르게 성장하는 수요를 수용하기 위한 확장 설계가 필요합니다.

