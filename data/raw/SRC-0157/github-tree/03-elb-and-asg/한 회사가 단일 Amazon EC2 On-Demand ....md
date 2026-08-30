## Question

한 회사가 단일 Amazon EC2 On-Demand 인스턴스에서 웹사이트 분석 애플리케이션을 호스팅합니다. 분석 애플리케이션은 매우 회복성이 뛰어나고 상태 비저장 모드로 실행되도록 설계되었습니다. 이 회사는 바쁜 시간에 애플리케이션이 성능 저하 징후를 보이고 5xx 오류가 표시된다는 것을 알아챘습니다. 이 회사는 애플리케이션을 원활하게 확장해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족할 솔루션은 무엇입니까?

- [ ] A. 웹 애플리케이션의 Amazon Machine Image(AMI)를 만듭니다. AMI를 사용하여 두 번째 EC2 On-Demand 인스턴스를 시작합니다. Application Load Balancer를 사용하여 두 EC2 인스턴스에 부하를 분산합니다.
- [ ] B. 웹 애플리케이션의 Amazon Machine Image(AMI)를 만듭니다. AMI를 사용하여 두 번째 EC2 On-Demand 인스턴스를 시작합니다. Amazon Route 53 가중 라우팅을 사용하여 두 EC2 인스턴스에 부하를 분산합니다.
- [ ] C. EC2 인스턴스를 중지하고 인스턴스 유형을 변경하기 위한 AWS Lambda 함수를 만듭니다. CPU 사용률이 75%를 넘을 때 Lambda 함수를 호출하기 위한 Amazon CloudWatch 알람을 만듭니다.
- [ ] D. 웹 애플리케이션의 Amazon Machine Image(AMI)를 만듭니다. AMI를 실행 템플릿에 적용합니다. 실행 템플릿을 포함하는 Auto Scaling 그룹을 만듭니다. Spot Fleet을 사용하도록 실행 템플릿을 구성합니다. Auto Scaling 그룹에 Application Load Balancer를 연결합니다.

## Answer

정답: D

## Explanation

AMI를 사용한 시작 템플릿, Auto Scaling 그룹, Spot Fleet, ALB를 결합하면 트래픽 증가에 따른 자동 수평 확장과 Spot 인스턴스를 통한 비용 최적화를 동시에 달성합니다. 애플리케이션이 상태 비저장(Stateless)이고 회복성이 뛰어나므로 Spot 인스턴스 중단에도 안전하게 대응할 수 있으며, ALB가 트래픽을 균등하게 분산합니다.

오답 분석

A: 두 대의 온디맨드 인스턴스로 고정하면 트래픽이 더 증가할 때 자동 확장이 불가능하며, 피크 시간에 여전히 5xx 오류가 발생할 수 있습니다.

B: Route 53 가중치 라우팅은 두 인스턴스 간 트래픽 비율을 조정하지만, 인스턴스 수를 자동으로 확장하는 기능이 없어 트래픽 급증 시 대응이 불가능합니다.

C: Lambda 함수로 EC2 인스턴스를 중지하고 더 큰 인스턴스 유형으로 변경하는 수직 확장 방식은 인스턴스 중지/시작 동안 다운타임이 발생하므로 원활한 확장이 아닙니다.

