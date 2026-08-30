## Question

회사에서 온프레미스 데이터 세트의 보조 사본으로 Amazon S3를 사용하려고 합니다. 회사는 이 복사본에 액세스할 필요가 거의 없습니다. 스토리지 솔루션의 비용은 최소화되어야 합니다.
이러한 요구 사항을 충족하는 스토리지 솔루션은 무엇입니까?

- [ ] A. S3 Standard
- [ ] B. S3 Intelligent-Tiering
- [ ] C. S3 Standard-Infrequent Access(S3 Standard-IA)
- [ ] D. S3 One Zone-Infrequent Access(S3 One Zone-IA)

## Answer

정답: D

## Explanation

S3 One Zone-IA는 단일 가용 영역에만 데이터를 저장하여 S3 Standard-IA 대비 약 20% 저렴한 스토리지 비용을 제공합니다. 이 데이터는 온프레미스 데이터의 보조 사본(secondary copy)이므로 원본이 온프레미스에 보존되어 있어, AZ 장애로 인한 S3 데이터 손실 시에도 원본에서 다시 복구할 수 있습니다. 거의 액세스하지 않는 데이터에 대해 비용을 최소화해야 하므로, S3 One Zone-IA가 가장 적합한 선택입니다.

오답 분석

A: S3 Standard는 자주 액세스하는 데이터에 최적화된 스토리지 클래스로, GB당 비용이 $0.023이며 거의 액세스하지 않는 보조 사본에는 불필요하게 비용이 높습니다.

B: S3 Intelligent-Tiering은 액세스 패턴이 불확실한 경우에 유용하지만, 이미 '거의 액세스하지 않는다'고 명시되어 있으므로 객체당 모니터링 요금($0.0025/1000 객체)이 불필요한 비용입니다.

C: S3 Standard-IA는 다중 AZ에 데이터를 복제하여 높은 가용성을 제공하지만, 보조 사본이므로 다중 AZ 복원력이 필수가 아니어서 S3 One Zone-IA보다 약 20% 비용이 높습니다.

