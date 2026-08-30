## Question

한 회사는 높은 동시성 AWS Lambda 함수를 사용하여 마케팅 이벤트 중에 메시지 대기열에서 지속적으로 증가하는 메시지 수를 처리합니다. Lambda 함수는 CPU 집약적인 코드를 사용하여 메시지를 처리합니다. 회사는 컴퓨팅 비용을 줄이고 고객의 서비스 대기 시간을 유지하기를 원합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. Lambda 함수에 대해 예약된 동시성을 구성합니다. Lambda 함수에 할당된 메모리를 줄입니다.
- [ ] B. Lambda 함수에 대한 예약된 동시성을 구성합니다. AWS Compute Optimizer 권장 사항에 따라 메모리를 늘립니다.
- [ ] C. Lambda 함수에 대해 프로비저닝된 동시성을 구성합니다. Lambda 함수에 할당된 메모리를 줄입니다.
- [ ] D. Lambda 함수에 대해 프로비저닝된 동시성을 구성합니다. AWS Compute Optimizer 권장 사항에 따라 메모리를 늘립니다.

## Answer

정답: D

## Explanation

Provisioned concurrency는 Lambda 실행 환경을 사전 초기화하여 마케팅 이벤트 시 급증하는 메시지 처리에서 cold start를 완전히 제거합니다. AWS Compute Optimizer의 권장사항에 따라 메모리를 증가시키면 Lambda에 할당되는 CPU도 비례하여 증가하여 메시지 처리 성능이 향상됩니다(Lambda는 메모리 설정에 비례하여 CPU 파워를 할당). 이 조합으로 높은 동시성 환경에서 일관된 저지연 처리와 최적의 리소스 효율성을 동시에 달성합니다.

오답 분석

A: Reserved concurrency는 함수의 최대 동시 실행 수를 제한하는 설정으로 cold start를 방지하지 못합니다. 메모리 감소는 CPU 할당도 줄여 처리 성능이 저하되며, Compute Optimizer 권장과 반대입니다.

B: Reserved concurrency + 메모리 증가 조합에서 reserved concurrency는 동시성 상한을 설정할 뿐 실행 환경을 사전 초기화하지 않습니다. 높은 동시성에서 cold start가 여전히 발생합니다.

C: Provisioned concurrency + 메모리 감소 조합에서 cold start는 방지되지만, 메모리(CPU) 감소로 개별 메시지 처리 시간이 길어집니다. Compute Optimizer 권장과 반대 방향이며 성능이 저하됩니다.

