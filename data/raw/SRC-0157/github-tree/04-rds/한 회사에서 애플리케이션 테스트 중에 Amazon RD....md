## Question

한 회사에서 애플리케이션 테스트 중에 Amazon RDS for MySQL DB 인스턴스를 사용했습니다. 테스트 주기가 끝날 때 DB 인스턴스를 종료하기 전에 솔루션 설계자는 두 개의 백업을 생성했습니다. 솔루션 설계자는 데이터베이스 덤프를 생성하기 위해 mysqldump 유틸리티를 사용하여 첫 번째 백업을 생성했습니다. 솔루션 설계자는 RDS 종료 시 최종 DB 스냅샷 옵션을 활성화하여 두 번째 백업을 생성했습니다.
회사는 이제 새로운 테스트 주기를 계획하고 있으며 가장 최근 백업에서 새 DB 인스턴스를 생성하려고 합니다. 이 회사는 DB 인스턴스를 호스팅하기 위해 Amazon Aurora의 MySQL 호환 에디션을 선택했습니다.
어떤 솔루션이 새 DB 인스턴스를 생성합니까? (두 가지를 선택하세요.)

- [ ] A. RDS 스냅샷을 Aurora로 직접 가져옵니다.
- [ ] B. RDS 스냅샷을 Amazon S3에 업로드합니다. 그런 다음 RDS 스냅샷을 Aurora로 가져옵니다.
- [ ] C. 데이터베이스 덤프를 Amazon S3에 업로드합니다. 그런 다음 데이터베이스 덤프를 Aurora로 가져옵니다.
- [ ] D. AWS Database Migration Service(AWS DMS)를 사용하여 RDS 스냅샷을 Aurora로 가져옵니다.
- [ ] E. 데이터베이스 덤프를 Amazon S3에 업로드합니다. 그런 다음 AWS Database Migration Service(AWS DMS)를 사용하여 데이터베이스 덤프를 Aurora로 가져옵니다.

## Answer

정답: A, C

## Explanation

(A) RDS MySQL 스냅샷을 Aurora MySQL로 직접 가져올 수 있습니다. AWS 콘솔에서 RDS 스냅샷을 선택하고 'Aurora 읽기 복제본 복원' 또는 'DB 클러스터로 마이그레이션' 옵션을 사용하면 됩니다. (C) mysqldump로 생성한 데이터베이스 덤프를 Amazon S3에 업로드한 후, Aurora MySQL의 S3에서 데이터 가져오기 기능을 사용하여 데이터를 로드할 수 있습니다. 이 두 방법 모두 MySQL 호환 Aurora에서 공식적으로 지원하는 마이그레이션 방법입니다.

오답 분석

B: RDS 스냅샷은 이미 AWS 내부에 저장되어 있으므로 Amazon S3에 별도로 업로드할 필요가 없습니다. RDS 스냅샷은 S3에 업로드하는 형태가 아니라 직접 Aurora로 가져올 수 있습니다.

D: AWS DMS는 데이터베이스 마이그레이션 서비스이지만, RDS 스냅샷을 직접 가져오는 것이 아니라 실행 중인 소스 데이터베이스에서 대상 데이터베이스로 데이터를 복제합니다. 이미 종료된 DB 인스턴스의 스냅샷에는 적합하지 않습니다.

E: AWS DMS는 S3의 데이터베이스 덤프 파일을 직접 소스로 사용하는 데 최적화되어 있지 않습니다. Aurora의 네이티브 S3 가져오기 기능이 더 간단하고 효율적입니다.

