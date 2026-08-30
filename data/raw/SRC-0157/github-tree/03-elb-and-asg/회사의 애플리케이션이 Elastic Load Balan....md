## Question

회사의 애플리케이션이 Elastic Load Balancing(ELB) 로드 밸런서 뒤의 Auto Scaling 그룹 내의 Amazon EC2 인스턴스에서 실행되고 있습니다. 애플리케이션 기록을 토대로 회사에서는 매년 휴일 동안 트래픽이 급증할 것으로 예상합니다. 솔루션 아키텍트는 Auto Scaling 그룹이 애플리케이션 사용자에 대한 성능 영향을 최소화하기 위해 용량을 사전에 늘리도록 하는 전략을 설계해야 합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. CPU 사용률이 90%를 초과하면 EC2 인스턴스를 확장하기 위해 Amazon CloudWatch 경보를 생성합니다.
- [ ] B. 예상되는 최고 수요 기간 이전에 Auto Scaling 그룹을 확장하기 위해 반복 예약 작업을 생성합니다.
- [ ] C. 피크 수요 기간 동안 Auto Scaling 그룹의 최소 및 최대 EC2 인스턴스 수를 늘립니다.
- [ ] D. 이벤트가 있을 때 Auto Scaling:EC2_INSTANCE_LAUNCH 알림을 보내도록 Amazon Simple Notification Service(Amazon SNS) 알림을 구성합니다.

## Answer

정답: B

## Explanation

반복 예약 작업(Recurring Scheduled Action)을 사용하면 매년 예상되는 휴일 피크 수요 기간 이전에 Auto Scaling 그룹을 사전에(proactively) 확장할 수 있습니다. cron 표현식으로 매년 같은 기간에 반복되도록 설정하면, 피크 트래픽이 발생하기 전에 충분한 인스턴스가 미리 준비되어 사용자 성능 영향을 최소화합니다. 예약 작업은 Auto Scaling 그룹의 최소, 최대, 원하는 용량을 지정된 시간에 자동으로 변경하므로 수동 개입이 필요 없습니다.

오답 분석

A: CPU 사용률 90% CloudWatch 경보는 완전히 반응적(reactive) 조정입니다. CPU가 이미 90%에 도달한 후에야 확장이 시작되므로, 인스턴스가 추가되기 전에 사용자들이 이미 성능 저하를 경험합니다. '사전에(proactively) 용량을 늘려야 한다'는 요구 사항에 부합하지 않습니다.

C: 피크 수요 기간 동안 최소 및 최대 인스턴스 수를 수동으로 늘리는 것은 운영자가 직접 콘솔/CLI로 변경해야 합니다. 자동화되지 않아 실수, 지연, 누락이 발생할 수 있으며, 매년 반복되는 이벤트에 수동 대응은 운영 리스크가 있습니다.

D: SNS 알림은 Auto Scaling:EC2_INSTANCE_LAUNCH 이벤트가 발생할 때 알림만 보내며, Auto Scaling 그룹의 용량을 사전에 늘리는 능동적 조치가 아닙니다. 정보 제공용 모니터링 도구일 뿐 사전 확장 기능이 없습니다.

