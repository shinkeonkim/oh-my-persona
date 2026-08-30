## Question

한 회사는 Application Load Balancer 뒤에 있는 Amazon EC2 인스턴스에서 고가용성 웹 애플리케이션을 실행합니다. 회사는 Amazon CloudWatch 지표를 사용합니다.
웹 애플리케이션에 대한 트래픽이 증가함에 따라 일부 EC2 인스턴스는 많은 미해결 요청으로 인해 과부하가 발생합니다. CloudWatch 지표는 처리된 요청 수와 일부 EC2 인스턴스로부터 응답을 수신하는 시간이 모두 다른 EC2 인스턴스에 비해 높다는 것을 보여줍니다. 회사는 이미 과부하된 EC2 인스턴스에 새 요청이 전달되는 것을 원하지 않습니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. RequestCountPerTarget 및 ActiveConnectionCount CloudWatch 지표를 기반으로 라운드 로빈 라우팅 알고리즘을 사용합니다.
- [ ] B. RequestCountPerTarget 및 ActiveConnectionCount CloudWatch 지표를 기반으로 최소 미해결 요청 알고리즘을 사용합니다.
- [ ] C. RequestCount 및 TargetResponseTime CloudWatch 지표를 기반으로 라운드 로빈 라우팅 알고리즘을 사용합니다.
- [ ] D. RequestCount 및 TargetResponseTime CloudWatch 지표를 기반으로 최소 미해결 요청 알고리즘을 사용합니다.

## Answer

정답: B

## Explanation

Application Load Balancer(ALB)의 Least Outstanding Requests(최소 미처리 요청) 라우팅 알고리즘은 현재 처리 중인 미해결 요청이 가장 적은 대상 인스턴스에 새 요청을 라우팅합니다. RequestCountPerTarget 메트릭은 각 대상 인스턴스가 받은 요청 수를, ActiveConnectionCount 메트릭은 현재 활성 연결 수를 나타내며, 이 지표들이 인스턴스의 실시간 부하 상태를 직접적으로 반영합니다. 이 알고리즘을 사용하면 이미 과부하된 인스턴스에는 새 요청을 보내지 않고, 여유가 있는 인스턴스로 트래픽을 분배하여 부하를 균등하게 유지할 수 있습니다.

오답 분석

A: Round Robin 라우팅 알고리즘은 요청을 순서대로 순환하며 균등하게 분배합니다. 인스턴스의 현재 부하 상태(대기 요청 수, 활성 연결 수)를 고려하지 않으므로, 이미 과부하된 인스턴스에도 계속 요청이 전송될 수 있어 문제를 해결하지 못합니다.

C: RequestCount와 TargetResponseTime은 과거의 총 요청 수와 평균 응답 시간을 나타내는 지표입니다. 현재 실시간 대기 요청 수를 직접적으로 반영하지 못하며, Round Robin 방식은 부하와 무관하게 균등 분배하므로 과부하 인스턴스 회피가 불가능합니다.

D: Least Outstanding Requests 알고리즘 자체는 적합하지만, RequestCount와 TargetResponseTime 지표 조합은 '현재 대기 중인 요청 수'를 직접적으로 나타내지 않습니다. TargetResponseTime은 이미 완료된 요청의 응답 시간이며, RequestCountPerTarget과 ActiveConnectionCount가 실시간 부하 상태를 더 정확하게 반영합니다.

