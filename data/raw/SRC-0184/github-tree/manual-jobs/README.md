# Manual Jobs Directory

이 디렉토리는 **수동으로만 실행해야 하는 Kubernetes Job**들을 포함합니다.

⚠️ **중요**: 이 디렉토리의 파일들은 ArgoCD 관리 대상이 아닙니다!

## 포함된 Job

### restore-job.yml
PostgreSQL 데이터베이스 복구 Job

**사용 시나리오:**
- 데이터 손실 발생 시
- 특정 시점으로 롤백 필요 시
- 프로덕션 데이터를 개발 환경으로 복사 시

**실행 방법:**
```bash
# 1. 사용 가능한 백업 파일 확인
aws s3 ls s3://palette-db-backup/postgres/pgdump/palettedb/daily/ | sort -r | head -5

# 2. restore-job.yml 파일에서 SOURCE_KEY 수정
# env.SOURCE_KEY 값을 복구할 파일 경로로 변경

# 3. Job 실행
kubectl apply -f production/manual-jobs/restore-job.yml

# 4. 진행 상황 모니터링
kubectl logs -f job/pg-restore-from-s3 -n palette-production

# 5. 완료 후 정리
kubectl delete job pg-restore-from-s3 -n palette-production
```

## ArgoCD와 분리된 이유

1. **의도하지 않은 실행 방지**: Kubernetes Job은 생성 즉시 실행됩니다
2. **수동 제어**: 데이터베이스 복구는 신중한 결정이 필요합니다
3. **파라미터 수정**: 매번 다른 백업 파일을 지정해야 합니다

## 주의사항

- 이 디렉토리의 파일들은 Git에 커밋되지만 ArgoCD에 의해 자동 배포되지 않습니다
- 실행 전 반드시 파라미터(SOURCE_KEY, RESTORE_DB 등)를 확인하세요
- Job 완료 후에는 수동으로 삭제해야 합니다
