## Question

한 회사가 데이터베이스를 PostgreSQL용 Amazon RDS로 마이그레이션하고 있습니다. 이 회사는 애플리케이션을 Amazon EC2 인스턴스로 마이그레이션하고 있습니다. 이 회사는 장기 실행 워크로드에 대한 비용을 최적화하고자 합니다.
어떤 솔루션이 이 요구 사항을 가장 비용 효율적으로 충족할까요?

- [ ] A. Amazon RDS for PostgreSQL 워크로드에 온디맨드 인스턴스를 사용합니다. EC2 인스턴스에 대해 No Upfront 옵션이 있는 1년 Compute Savings Plan을 구매합니다.
- [ ] B. Amazon RDS for PostgreSQL 워크로드에 대해 1년 기간의 예약 인스턴스를 선불 없이 구매합니다. EC2 인스턴스에 대해 선불 없이 1년 EC2 Instance Savings Plan을 구매합니다.
- [ ] C. Amazon RDS for PostgreSQL 워크로드에 대한 부분 선불 옵션으로 1년 기간의 예약 인스턴스를 구매합니다. EC2 인스턴스에 대한 부분 선불 옵션으로 1년 EC2 Instance Savings Plan을 구매합니다.
- [ ] D. Amazon RDS for PostgreSQL 워크로드에 대한 All Upfront 옵션으로 3년 기간의 Reserved Instances를 구매합니다. EC2 인스턴스에 대한 All Upfront 옵션으로 3년 EC2 Instance Savings Plan을 구매합니다.

## Answer

정답: D

## Explanation

장기 실행 워크로드의 비용을 최적화하려면 가장 긴 약정 기간(3년)과 가장 높은 선결제 옵션(All Upfront)을 선택해야 최대 할인율을 받을 수 있습니다. RDS는 예약 인스턴스(RI)를, EC2는 EC2 Instance Savings Plan을 각각 3년 전액 선결제로 구매하면 온디맨드 대비 최대 60-72% 할인을 받을 수 있습니다.

오답 분석

A: RDS에 온디맨드 인스턴스를 사용하면 할인이 전혀 없어 비용이 가장 높습니다. 1년 Compute Savings Plan도 3년 약정보다 할인율이 낮습니다.

B: 1년 약정과 선결제 없음(No Upfront) 옵션은 3년 전액 선결제 대비 할인율이 현저히 낮습니다. 장기 실행 워크로드에는 더 긴 약정이 비용 효율적입니다.

C: 1년 약정과 부분 선결제(Partial Upfront) 옵션은 3년 전액 선결제보다 할인율이 낮아 장기적으로 비용이 더 높습니다.

