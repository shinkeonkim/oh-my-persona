## Question

회사에서 5개의 Amazon EC2 인스턴스에 애플리케이션을 배포합니다. ALB(Application Load Balancer)는 대상 그룹을 사용하여 인스턴스에 트래픽을 분산합니다. 각 인스턴스의 평균 CPU 사용량은 대부분 10% 미만이며 때때로 65%까지 급증합니다.
솔루션 설계자는 애플리케이션의 확장성을 자동화하는 솔루션을 구현해야 합니다. 솔루션은 아키텍처의 비용을 최적화하고 급증이 발생할 때 애플리케이션에 충분한 CPU 리소스가 있는지 확인해야 합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. CPUUtilization 지표가 20% 미만일 때 ALARM 상태로 들어가는 Amazon CloudWatch 경보를 생성합니다. ALB 대상 그룹의 EC2 인스턴스 중 하나를 종료하기 위해 CloudWatch 경보가 호출하는 AWS Lambda 함수를 생성합니다.
- [ ] B. EC2 Auto Scaling 그룹을 생성합니다. 기존 ALB를 로드 밸런서로 선택하고 기존 대상 그룹을 대상 그룹으로 선택합니다. ASGAverageCPUUtilization 지표를 기반으로 하는 대상 추적 조정 정책을 설정합니다. 최소 인스턴스를 2로, 원하는 용량을 3으로, 최대 인스턴스를 6으로, 목표 값을 50%로 설정합니다. Auto Scaling 그룹에 EC2 인스턴스를 추가합니다.
- [ ] C. EC2 Auto Scaling 그룹을 생성합니다. 기존 ALB를 로드 밸런서로 선택하고 기존 대상 그룹을 대상 그룹으로 선택합니다. 최소 인스턴스를 2로, 원하는 용량을 3으로, 최대 인스턴스를 6으로 설정합니다. Auto Scaling 그룹에 EC2 인스턴스를 추가합니다.
- [ ] D. 두 개의 Amazon CloudWatch 경보를 생성합니다. 평균 CPUUtilization 지표가 20% 미만일 때 ALARM 상태로 들어가도록 첫 번째 CloudWatch 경보를 구성합니다. 평균 CPUUtilization 지표가 50%를 초과하면 ALARM 상태로 들어가도록 두 번째 CloudWatch 경보를 구성합니다. 이메일 메시지를 보내기 위해 Amazon Simple Notification Service(Amazon SNS) 주제에 게시하도록 경보를 구성합니다. 메시지를 받은 후 로그인하여 실행 중인 EC2 인스턴스 수를 줄이거나 늘립니다.

## Answer

정답: B

## Explanation

EC2 Auto Scaling 그룹을 생성하고 ASGAverageCPUUtilization 지표를 기반으로 대상 추적 조정 정책(Target Tracking Scaling Policy)을 설정하면, CPU 사용률이 목표값(50%)을 유지하도록 인스턴스 수가 자동으로 조정됩니다. 최소 2개에서 최대 6개 인스턴스로 설정하여 유휴 시에는 인스턴스를 줄여 비용을 최적화하고, CPU 급증(65%) 시에는 자동으로 인스턴스를 추가하여 충분한 CPU 리소스를 확보합니다. 목표 값 50%로 설정하면 급증이 발생해도 여유 CPU가 있어 안정적입니다.

오답 분석

A: CloudWatch 경보로 Lambda를 호출하여 인스턴스를 종료하는 방식은 축소(scale-in)만 가능하며, 트래픽 급증 시 자동 확장(scale-out) 기능이 없습니다. 또한 Auto Scaling 그룹의 내장 기능을 활용하지 않고 별도의 Lambda 로직을 구현해야 하므로 불필요하게 복잡합니다.

C: Auto Scaling 그룹을 생성하되 조정 정책 없이 고정된 인스턴스 수(원하는 용량 3개)만 설정하면, CPU 사용률 변화에 자동으로 대응할 수 없습니다. 급증 시 인스턴스가 추가되지 않고, 유휴 시에도 축소되지 않아 비용 최적화가 불가능합니다.

D: CloudWatch 경보를 생성하여 SNS 이메일을 보내고 관리자가 수동으로 인스턴스 수를 조정하는 것은 자동화된 확장성 요구 사항을 전혀 충족하지 않습니다. 관리자의 수동 개입이 필요하며, 야간이나 주말에 신속한 대응이 어렵습니다.

