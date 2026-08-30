## Question

머신러닝(ML) 팀이 Amazon S3 버킷에 있는 데이터를 사용하는 애플리케이션을 구축하고 있습니다. ML 팀은 AWS에서 모델 학습 워크플로를 위한 스토리지 솔루션이 필요합니다. ML 팀은 학습 데이터세트에 대한 빈번한 액세스를 지원하는 고성능 스토리지가 필요합니다. 스토리지 솔루션은 Amazon S3와 기본적으로 통합되어야 합니다.
운영 오버헤드를 최소화하면서 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. Amazon Elastic Block Store(Amazon EBS) 볼륨을 사용하여 고성능 스토리지를 제공합니다. AWS DataSync를 사용하여 S3 버킷에서 EBS 볼륨으로 데이터를 마이그레이션합니다.
- [ ] B. Amazon EC2 ML 인스턴스를 사용하여 고성능 스토리지를 제공합니다. Amazon EBS 볼륨에 학습 데이터를 저장합니다. S3 Copy API를 사용하여 S3 버킷에서 EBS 볼륨으로 데이터를 복사합니다.
- [ ] C. Amazon FSx for Lustre를 사용하여 고성능 스토리지를 제공합니다. Amazon S3 Standard 스토리지에 학습 데이터세트를 저장합니다.
- [ ] D. Amazon EMR을 사용하여 고성능 스토리지를 제공합니다. Amazon S3 Glacier Instant Retrieval 스토리지에 훈련 데이터 세트를 저장합니다.

## Answer

정답: C

## Explanation

Amazon FSx for Lustre는 고성능 파일 시스템으로 ML 학습 워크로드에 최적화되어 있으며, Amazon S3와 네이티브하게 통합됩니다. S3 Standard에 저장된 학습 데이터셋을 FSx for Lustre에 자동으로 연결하여 고성능 접근이 가능하며, 운영 오버헤드가 최소화됩니다.

오답 분석

A: EBS 볼륨은 단일 인스턴스에 연결되어 여러 인스턴스 간 공유가 불가능하며, DataSync를 사용한 데이터 마이그레이션은 S3 네이티브 통합이 아닙니다.

B: EC2 ML 인스턴스와 EBS 조합은 S3와 네이티브 통합이 아니며, S3 Copy API로 데이터를 복사하는 것은 운영 오버헤드가 큽니다.

D: Amazon EMR은 빅데이터 처리 프레임워크이며, S3 Glacier Instant Retrieval은 자주 접근하는 학습 데이터에 추가 비용이 발생합니다.

