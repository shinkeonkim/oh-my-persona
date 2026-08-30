## Question

한 회사가 Amazon EC2 인스턴스에서 모놀리식 웹 애플리케이션을 호스팅합니다. 애플리케이션 사용자는 최근 특정 시간에 성능이 좋지 않다고 보고했습니다. Amazon CloudWatch 메트릭을 분석한 결과 성능이 좋지 않은 기간 동안 CPU 사용률이 100%인 것으로 나타났습니다. 이 회사는 이 성능 문제를 해결하고 애플리케이션 가용성을 개선하고자 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족할 수 있는 단계 조합은 무엇입니까? (두 가지를 선택하세요.)

- [ ] A. AWS Compute Optimizer를 사용하여 수직 확장에 적합한 인스턴스 유형에 대한 권장 사항을 얻습니다.
- [ ] B. 웹 서버에서 Amazon Machine Image(AMI)를 만듭니다. 새 시작 템플릿에서 AMI를 참조합니다.
- [ ] C. 수직적으로 확장하기 위해 Auto Scaling 그룹과 Application Load Balancer를 만듭니다.
- [ ] D. AWS Compute Optimizer를 사용하여 수평적으로 확장할 인스턴스 유형에 대한 권장 사항을 얻습니다.
- [ ] E. 수평적 확장을 위해 Auto Scaling 그룹과 Application Load Balancer를 만듭니다.

## Answer

정답: B, E

## Explanation

B(웹 서버에서 AMI를 생성하여 시작 템플릿에 참조)로 현재 애플리케이션의 복제본을 자동 배포할 준비를 하고, E(Auto Scaling 그룹과 Application Load Balancer를 사용한 수평 확장)로 CPU 사용률이 높아지면 자동으로 인스턴스를 추가하여 부하를 분산합니다. 수평 확장은 단일 인스턴스의 한계를 극복하고 가용성도 동시에 향상시킵니다.

오답 분석

A: AWS Compute Optimizer는 적절한 인스턴스 유형을 추천하여 수직 확장에 도움이 되지만, 수직 확장은 인스턴스 크기 변경 시 다운타임이 발생하고 단일 장애 지점이 유지되어 가용성 개선이 제한적입니다.

C: Auto Scaling 그룹과 ALB는 '수평 확장'에 사용되는 기술이며, '수직 확장'(인스턴스 크기 증가)에 사용된다는 설명은 정확하지 않습니다.

D: Compute Optimizer는 인스턴스 유형 최적화(수직 확장) 권장을 제공하는 도구이며, '수평적 확장'을 위한 인스턴스 유형을 추천하는 기능은 아닙니다.

