## Question

회사는 PostgreSQL DB 인스턴스용 Amazon RDS에서 중요 데이터베이스를 실행합니다. 이 회사는 가동 중지 시간과 데이터 손실을 최소화하면서 Amazon Aurora PostgreSQL로 마이그레이션하려고 합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. RDS for PostgreSQL DB 인스턴스의 DB 스냅샷을 생성하여 새로운 Aurora PostgreSQL DB 클러스터를 채웁니다.
- [ ] B. RDS for PostgreSQL DB 인스턴스의 Aurora 읽기 전용 복제본을 생성합니다. Aurora 읽기 복제본을 새로운 Aurora PostgreSQL DB 클러스터로 승격합니다.
- [ ] C. Amazon S3에서 데이터 가져오기를 사용하여 데이터베이스를 Aurora PostgreSQL DB 클러스터로 마이그레이션합니다.
- [ ] D. pg_dump 유틸리티를 사용하여 PostgreSQL용 RDS 데이터베이스를 백업합니다. 새 Aurora PostgreSQL DB 클러스터로 백업을 복원합니다.

## Answer

정답: B

## Explanation

RDS for PostgreSQL에서 Aurora PostgreSQL로 마이그레이션할 때, Aurora 읽기 전용 복제본을 생성하는 방법이 최소 다운타임으로 마이그레이션하는 가장 효율적인 방법입니다. RDS PostgreSQL DB 인스턴스에서 Aurora 읽기 복제본을 직접 생성할 수 있으며, 복제가 완료된 후 Aurora 복제본을 독립적인 Aurora PostgreSQL DB 클러스터로 승격하면 됩니다. 이 과정에서 복제가 지속되므로 데이터 손실이 최소화되고, 승격 시에만 짧은 다운타임이 발생합니다.

오답 분석

A: DB 스냅샷에서 새 Aurora 클러스터를 생성하면 스냅샷 생성 이후의 데이터가 손실될 수 있으며, 스냅샷 복원 중 다운타임이 더 길어집니다.

C: Amazon S3에서 데이터 가져오기는 추가적인 데이터 내보내기/가져오기 단계가 필요하여 운영 오버헤드가 더 크고 다운타임도 길어집니다.

D: pg_dump 유틸리티를 사용한 백업/복원은 수동 프로세스로 운영 오버헤드가 크며, 대량 데이터의 경우 시간이 오래 걸려 다운타임과 데이터 손실 위험이 증가합니다.

