## Question

회사는 Amazon EC2 인스턴스와 AWS Lambda 함수를 사용하여 애플리케이션을 실행합니다. 이 회사는 AWS 계정에 퍼블릭 서브넷과 프라이빗 서브넷이 있는 VPC가 있습니다. EC2 인스턴스는 VPC 중 하나의 프라이빗 서브넷에서 실행됩니다. 애플리케이션이 작동하려면 Lambda 함수가 EC2 인스턴스에 대한 직접적인 네트워크 액세스가 필요합니다.
애플리케이션은 최소 1년 동안 실행됩니다. 회사는 해당 시간 동안 애플리케이션이 사용하는 Lambda 함수의 수가 증가할 것으로 예상합니다. 회사는 모든 애플리케이션 리소스에 대한 절감 효과를 극대화하고 서비스 간의 네트워크 대기 시간을 낮게 유지하려고 합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. EC2 Instance Savings Plan을 구매합니다. Lambda 함수의 지속 시간, 메모리 사용량 및 호출 수를 최적화합니다. EC2 인스턴스가 포함된 프라이빗 서브넷에 Lambda 함수를 연결합니다.
- [ ] B. EC2 Instance Savings Plan을 구매합니다. Lambda 함수의 기간 및 메모리 사용량, 호출 수 및 전송되는 데이터 양을 최적화합니다. EC2 인스턴스가 실행되는 동일한 VPC의 퍼블릭 서브넷에 Lambda 함수를 연결합니다.
- [ ] C. Compute Savings Plan을 구매합니다. Lambda 함수의 기간 및 메모리 사용량, 호출 수 및 전송되는 데이터 양을 최적화합니다. EC2 인스턴스가 포함된 프라이빗 서브넷에 Lambda 함수를 연결합니다.
- [ ] D. Compute Savings Plan을 구매합니다. Lambda 함수의 기간 및 메모리 사용량, 호출 수 및 전송되는 데이터 양을 최적화합니다. Lambda 서비스 VPC에 Lambda 함수를 유지합니다.

## Answer

정답: C

## Explanation

Compute Savings Plan은 EC2 인스턴스, AWS Lambda, AWS Fargate를 포함한 모든 AWS 컴퓨팅 서비스에 적용되므로, Lambda 함수의 수가 증가할 것으로 예상되는 이 시나리오에서 EC2와 Lambda 모두의 비용을 절감하여 절감 효과를 극대화할 수 있습니다. Lambda 함수를 EC2 인스턴스가 있는 프라이빗 서브넷에 연결(VPC Lambda)하면 Lambda ENI(Elastic Network Interface)를 통해 EC2 인스턴스에 직접 네트워크 액세스가 가능하며, 동일 VPC 내 통신이므로 네트워크 지연 시간이 최소화됩니다.

오답 분석

A: EC2 Instance Savings Plan은 특정 인스턴스 패밀리와 리전에 대한 EC2 인스턴스 사용량에만 적용되고, Lambda 함수에는 적용되지 않습니다. Lambda 함수 수가 증가할 예정이므로 Lambda 비용도 절감할 수 있는 Compute Savings Plan이 필요합니다. 또한 Lambda 최적화 요소에 전송 데이터 양이 누락되어 있어 불완전합니다.

B: EC2 Instance Savings Plan은 Lambda에 적용되지 않아 전체 리소스 비용 절감에 한계가 있습니다. 또한 Lambda를 퍼블릭 서브넷에 연결하면 보안 모범 사례에 어긋나며, 프라이빗 서브넷의 EC2 인스턴스와 통신하기 위해 불필요한 네트워크 경로가 추가되어 최적의 구성이 아닙니다.

D: Lambda 함수를 Lambda 서비스 VPC(기본 VPC)에 유지하면, VPC 외부에서 실행되므로 프라이빗 서브넷의 EC2 인스턴스에 직접 네트워크 액세스가 불가능합니다. Lambda가 VPC 내 프라이빗 리소스에 접근하려면 반드시 해당 VPC의 서브넷에 연결(VPC 구성)해야 합니다.

