## Question

한 회사에서 Amazon EC2 인스턴스에서 실행할 새 웹 애플리케이션을 설계하고 있습니다. 애플리케이션은 백엔드 데이터 스토리지에 Amazon DynamoDB를 사용합니다. 애플리케이션 트래픽은 예측할 수 없습니다. 회사는 데이터베이스에 대한 애플리케이션 읽기 및 쓰기 처리량이 보통에서 높을 것으로 예상합니다. 회사는 애플리케이션 트래픽에 대응하여 확장해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 DynamoDB 테이블 구성은 무엇입니까?

- [ ] A. DynamoDB 표준 테이블 클래스를 사용하여 프로비저닝된 읽기 및 쓰기로 DynamoDB를 구성합니다. DynamoDB Auto Scaling을 정의된 최대 용량으로 설정합니다.
- [ ] B. DynamoDB Standard 테이블 클래스를 사용하여 온디맨드 모드에서 DynamoDB를 구성합니다.
- [ ] C. DynamoDB Standard Infrequent Access(DynamoDB Standard-IA) 테이블 클래스를 사용하여 프로비저닝된 읽기 및 쓰기로 DynamoDB를 구성합니다. DynamoDB Auto Scaling을 정의된 최대 용량으로 설정합니다.
- [ ] D. DynamoDB Standard Infrequent Access(DynamoDB Standard-IA) 테이블 클래스를 사용하여 온디맨드 모드에서 DynamoDB를 구성합니다.

## Answer

정답: B

## Explanation

DynamoDB Standard 테이블 클래스의 온디맨드 모드는 예측할 수 없는 트래픽 패턴에 최적입니다. 온디맨드 모드는 사전 용량 설정 없이 실제 읽기/쓰기 요청에 따라 자동 확장되며, 이전 피크 트래픽의 2배까지 즉시 수용합니다. Standard 테이블 클래스는 보통~높은 읽기/쓰기 처리량에 적합한 기본 클래스로, 읽기/쓰기 요청 비용이 Standard-IA보다 25% 저렴하여 자주 액세스하는 데이터에 비용 효율적입니다.

오답 분석

A: 프로비저닝 모드 + Auto Scaling은 예측 가능한 워크로드에 적합하지만, 예측할 수 없는 트래픽에서는 Auto Scaling 조정 지연(수 분)으로 인해 급격한 트래픽 급증 시 요청 제한이 발생할 수 있습니다. 최대 정의된 용량에 도달하면 그 이상으로 확장되지 않습니다.

C: DynamoDB Standard-IA 테이블 클래스는 스토리지 비용이 60% 저렴하지만 읽기/쓰기 요청 비용이 25% 더 높습니다. 보통~높은 읽기/쓰기 처리량이 예상되는 워크로드에서는 높은 요청 비용으로 인해 Standard 클래스보다 총 비용이 더 높아질 수 있습니다.

D: Standard-IA 온디맨드는 자주 액세스하지 않는 데이터에 적합합니다. 보통~높은 읽기/쓰기 처리량이 예상되므로 Standard-IA의 높은 요청 비용이 스토리지 절감보다 더 큰 비용을 발생시켜 비용 효율적이지 않습니다.

