## Question

솔루션 설계자는 Amazon S3를 사용하여 새로운 디지털 미디어 애플리케이션의 스토리지 아키텍처를 설계하고 있습니다. 미디어 파일은 가용 영역 손실에 대한 복원력이 있어야 합니다. 일부 파일은 자주 액세스되는 반면 다른 파일은 예측할 수 없는 패턴으로 거의 액세스되지 않습니다. 솔루션 설계자는 미디어 파일을 저장하고 검색하는 비용을 최소화해야 합니다.
이러한 요구 사항을 충족하는 스토리지 옵션은 무엇입니까?

- [ ] A. S3 Standard
- [ ] B. S3 Intelligent-Tiering
- [ ] C. S3 Standard-Infrequent Access(S3 Standard-IA)
- [ ] D. S3 One Zone-Infrequent Access(S3 One Zone-IA)

## Answer

정답: B

## Explanation

S3 Intelligent-Tiering은 액세스 패턴이 예측 불가능한 데이터에 최적화된 스토리지 클래스입니다. 자주 액세스하는 데이터는 자동으로 Frequent Access 계층(S3 Standard 동일 비용)에, 30일간 액세스하지 않은 데이터는 Infrequent Access 계층(S3 Standard-IA 수준 비용)으로, 90일간 액세스하지 않은 데이터는 Archive Instant Access 계층(S3 Glacier Instant Retrieval 수준 비용)으로 자동 이동됩니다. 모든 계층에서 밀리초 단위의 즉시 접근이 가능합니다. 또한 여러 AZ에 데이터를 저장하여 AZ 손실에 대한 복원력을 제공하며, 검색 비용이 없어(모니터링 비용 $0.0025/1000개 객체만 부과) 예측 불가능한 액세스 패턴에서 비용을 자동 최적화합니다.

오답 분석

A: S3 Standard은 모든 데이터에 GB당 $0.023의 동일한 비용을 적용하므로, 거의 액세스하지 않는 파일에 대해서도 높은 스토리지 비용이 발생하여 비용 최적화가 어렵습니다.

C: S3 Standard-IA는 자주 액세스하지 않는 데이터에 적합하지만, 일부 파일은 자주 액세스되므로 GB당 검색 비용($0.01/GB)이 빈번히 부과되어 오히려 비용이 증가할 수 있습니다. 액세스 패턴이 예측 불가능한 경우 Intelligent-Tiering이 검색 비용 없이 자동으로 최적 계층을 선택하므로 더 적합합니다.

D: S3 One Zone-IA는 단일 가용 영역에만 데이터를 저장하므로 'AZ 손실에 대한 복원력(resilient to the loss of an Availability Zone)' 요구 사항을 충족하지 못합니다. AZ 장애 시 데이터에 접근할 수 없거나 영구적으로 손실될 수 있습니다.

