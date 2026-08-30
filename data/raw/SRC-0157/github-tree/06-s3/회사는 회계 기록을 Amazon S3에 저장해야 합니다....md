## Question

회사는 회계 기록을 Amazon S3에 저장해야 합니다. 기록은 1년 동안 즉시 액세스할 수 있어야 하며 추가 9년 동안 보관해야 합니다. 관리 사용자 및 루트 사용자를 포함하여 회사의 그 누구도 전체 10년 기간 동안 레코드를 삭제할 수 없습니다. 기록은 최대한 탄력적으로 저장해야 합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 전체 10년 동안 S3 Glacier에 레코드를 저장합니다. 액세스 제어 정책을 사용하여 10년 동안 레코드 삭제를 거부합니다.
- [ ] B. S3 Intelligent-Tiering을 사용하여 레코드를 저장합니다. IAM 정책을 사용하여 레코드 삭제를 거부합니다. 10년 후 삭제를 허용하도록 IAM 정책을 변경합니다.
- [ ] C. S3 수명 주기 정책을 사용하여 1년 후 레코드를 S3 Standard에서 S3 Glacier Deep Archive로 전환합니다. 10년 동안 규정 준수 모드에서 S3 객체 잠금을 사용합니다.
- [ ] D. S3 수명 주기 정책을 사용하여 1년 후 레코드를 S3 Standard에서 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 전환합니다. 10년 동안 거버넌스 모드에서 S3 객체 잠금을 사용합니다.

## Answer

정답: C

## Explanation

S3 수명 주기 정책으로 1년 후 S3 Standard에서 S3 Glacier Deep Archive로 전환하면 비용을 크게 절감하면서 장기 보관 요구 사항을 충족합니다. S3 Glacier Deep Archive는 GB당 약 $0.00099로 가장 저렴한 스토리지입니다. S3 객체 잠금의 규정 준수(Compliance) 모드를 10년으로 설정하면 보존 기간 동안 루트 사용자를 포함한 어떤 사용자도 객체를 삭제하거나 덮어쓸 수 없으며, 보존 기간을 단축하는 것도 불가능합니다. 이는 WORM(Write Once Read Many) 모델을 구현하여 규정 준수 요구사항을 충족합니다. S3 Standard와 Glacier Deep Archive 모두 최소 3개 AZ에 데이터를 자동 복제하여 99.999999999%의 내구성으로 '최대 탄력성'을 보장합니다.

오답 분석

A: S3 Glacier에 전체 10년간 저장하면 처음 1년간 즉시 접근이 불가능합니다(Glacier Flexible Retrieval의 긴급 검색도 1-5분 소요). 또한 액세스 제어 정책(ACL)이나 버킷 정책은 IAM 권한을 가진 관리자나 루트 사용자에 의해 변경될 수 있으므로, 객체 잠금의 Compliance 모드처럼 변경 불가능한(immutable) 보호를 제공하지 못합니다.

B: S3 Intelligent-Tiering은 비용 최적화에 유용하지만, IAM 정책은 IAM 관리자나 루트 사용자에 의해 언제든 변경될 수 있으므로 삭제 방지를 10년간 보장하지 못합니다. '루트 사용자를 포함하여 누구도 삭제할 수 없다'는 요구사항에는 S3 객체 잠금 Compliance 모드만 충족합니다.

D: S3 One Zone-IA는 단일 가용 영역에만 데이터를 저장하여 AZ 장애 시 데이터 손실 위험이 있으므로 '최대 탄력성(maximum resiliency)' 요구 사항을 충족하지 못합니다. 거버넌스(Governance) 모드는 s3:BypassGovernanceRetention 권한이 있는 사용자가 잠금을 우회하여 객체를 삭제할 수 있어 '관리 사용자 및 루트 사용자를 포함한 누구도 삭제할 수 없다'는 요구사항에 위배됩니다.

