## Question

회사에서 여러 AWS 계정에 대한 로깅 솔루션을 구축하려고 합니다. 회사는 현재 모든 계정의 로그를 중앙 집중식 계정에 저장합니다. 회사는 VPC 흐름 로그와 AWS CloudTrail 로그를 저장하기 위해 중앙 집중식 계정에 Amazon S3 버킷을 생성했습니다. 모든 로그는 빈번한 분석을 위해 30일 동안 가용성이 높아야 하며, 백업 목적으로 추가 60일 동안 유지되고 생성 후 90일 후에 삭제되어야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. 생성 후 30일이 지나면 객체를 S3 Standard 스토리지 클래스로 전환합니다. 90일 후에 객체를 삭제하도록 Amazon S3에 지시하는 만료 작업을 작성합니다.
- [ ] B. 생성 후 30일이 지나면 객체를 S3 Standard-Infrequent Access(S3 Standard-IA) 스토리지 클래스로 전환합니다. 90일 후에 모든 객체를 S3 Glacier Flexible Retrieval 스토리지 클래스로 이동합니다. 90일 후에 객체를 삭제하도록 Amazon S3에 지시하는 만료 작업을 작성합니다.
- [ ] C. 생성 후 30일이 지나면 객체를 S3 Glacier Flexible Retrieval 스토리지 클래스로 전환합니다. 90일 후에 객체를 삭제하도록 Amazon S3에 지시하는 만료 작업을 작성합니다.
- [ ] D. 생성 후 30일이 지나면 객체를 S3 One Zone-Infrequent Access(S3 One Zone-IA) 스토리지 클래스로 전환합니다. 90일 후에 모든 객체를 S3 Glacier Flexible Retrieval 스토리지 클래스로 이동합니다. 90일 후에 객체를 삭제하도록 Amazon S3에 지시하는 만료 작업을 작성합니다.

## Answer

정답: C

## Explanation

30일간 빈번한 분석을 위해 높은 가용성이 필요하므로 S3 Standard에 저장하고, 30일 후 S3 Glacier Flexible Retrieval로 전환하면 백업 목적의 60일 동안 비용을 절감합니다. 90일 후 만료 작업으로 객체를 삭제합니다. 이 구성이 가장 비용 효율적입니다.

오답 분석

A: S3 Standard 스토리지 클래스로의 전환은 이미 Standard에 있는 데이터에 대해 의미가 없으며, 30일 이후 비용 절감 효과가 없습니다.

B: S3 Standard-IA로 전환 후 다시 Glacier로 전환하는 것은 불필요한 2단계 전환이며, 90일 후 삭제해야 하는데 Glacier로 이동하면서 동시에 삭제 만료를 설정하는 것은 모순적입니다.

D: S3 One Zone-IA로 전환 후 Glacier로 이동하는 것은 B와 동일한 문제가 있으며, One Zone-IA는 로그의 고가용성 요구 사항에 적합하지 않습니다.

