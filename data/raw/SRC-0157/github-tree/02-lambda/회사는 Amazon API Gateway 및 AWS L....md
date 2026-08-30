## Question

회사는 Amazon API Gateway 및 AWS Lambda를 사용하여 AWS에서 내부 서버리스 애플리케이션을 호스팅합니다. 회사 직원들은 매일 애플리케이션을 사용하기 시작할 때 대기 시간이 길어지는 문제를 보고합니다. 회사는 대기 시간을 줄이고 싶어합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. API Gateway 조절 한도를 늘립니다.
- [ ] B. 직원이 매일 애플리케이션을 사용하기 전에 Lambda 프로비저닝 동시성을 높이기 위해 예약된 조정을 설정합니다.
- [ ] C. Amazon CloudWatch 경보를 생성하여 매일 시작 시 경보 대상으로 Lambda 함수를 시작합니다.
- [ ] D. Lambda 함수 메모리를 늘립니다.

## Answer

정답: B

## Explanation

Lambda의 scheduled scaling을 설정하여 직원 업무 시작 전에 provisioned concurrency를 사전 증가시키면 cold start 지연시간을 선제적으로 방지할 수 있습니다. 예를 들어 업무 시작 30분 전에 provisioned concurrency를 높은 값으로 설정하면, 직원들이 접속할 때 이미 사전 초기화된 실행 환경이 준비되어 있어 일관된 밀리초 응답을 제공합니다. Application Auto Scaling의 예약 조정 정책으로 시간대별 concurrency를 자동 관리할 수 있습니다.

오답 분석

A: API Gateway 스로틀링 제한을 증가시키는 것은 API 요청 처리량을 늘리는 것이지, Lambda cold start로 인한 지연시간과는 무관합니다. 스로틀링은 요청 속도 제한이지 응답 속도 개선이 아닙니다.

C: CloudWatch 알람으로 Lambda를 트리거하는 방식은 반응적(reactive) 대응입니다. 업무 시작 시 이미 높은 지연이 발생한 후에야 알람이 트리거되므로, 초기 cold start 지연을 방지할 수 없습니다.

D: Lambda 함수 메모리를 증가시키면 CPU 할당도 비례하여 증가하여 실행 성능은 개선되지만, cold start 지연시간은 해결되지 않습니다. 초기화 과정(라이브러리 로딩, 연결 설정)의 시간은 메모리 크기와 직접적인 관계가 없습니다.

