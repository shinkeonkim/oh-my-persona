# 운영 가이드

## 상태 확인

- Web liveness/readiness: `/`
- API liveness: `/healthz`
- API readiness + DB: `/readyz`
- Prometheus: `/api/metrics`
- OpenAPI: `/api/docs`

API는 구조화된 Fastify/Pino 로그를 stdout으로 출력하며 Promtail/Loki가 수집한다.

## 사용자 승인

가입자는 `pending`으로 생성된다. 관리자 JWT로 다음 API를 사용한다.

```text
GET   /api/admin/users/pending
PATCH /api/admin/users/{id}/approve
PATCH /api/admin/users/{id}/reject
```

초기 관리자는 `create-admin` CLI로 idempotent하게 생성된다.
승인된 사용자는 기존 `pending` 세션을 로그아웃하고 다시 로그인해야 한다. API는 JWT 역할과
현재 DB 역할이 다르면 401을 반환하며, 새 로그인부터 `reader` 권한을 부여한다.

### 관리자 부트스트랩

환경 변수 4개를 설정한 뒤 CLI를 실행한다. 이미 존재하는 이메일이면 upsert된다.

| 환경 변수 | 설명 | 예시 |
|---|---|---|
| `DATABASE_URL` | PostgreSQL 접속 URL | `postgresql://user:pass@localhost:5432/aws_study` |
| `ADMIN_EMAIL` | 관리자 이메일 | `admin@example.com` |
| `ADMIN_PASSWORD` | 관리자 비밀번호 (12자 이상) | `super-secret-pw!` |
| `ADMIN_DISPLAY_NAME` | 표시 이름 (2–40자) | `Site Admin` |

```bash
# 저장소 루트에서 실행 (개발/운영 DB 공통)
export DATABASE_URL='postgresql://user:pass@localhost:5432/aws_study'
export ADMIN_EMAIL='admin@example.com'
export ADMIN_PASSWORD='replace-with-a-strong-password'
export ADMIN_DISPLAY_NAME='Site Admin'
bun run --filter '@aws-study/api' create-admin

# 셸 환경을 남기지 않는 일회성 실행
DATABASE_URL='postgresql://user:pass@localhost:5432/aws_study' \
ADMIN_EMAIL='admin@example.com' \
ADMIN_PASSWORD='replace-with-a-strong-password' \
ADMIN_DISPLAY_NAME='Site Admin' \
bun run --filter '@aws-study/api' create-admin
```

성공하면 정규화된 이메일과 함께 `Admin account is ready`가 출력된다. 같은 이메일로 다시
실행하면 새 계정을 중복 생성하지 않고 표시 이름, 비밀번호, 관리자 권한을 갱신한다.

`Invalid input: expected string, received undefined`가 나오면 위 네 환경 변수 중 하나가
현재 셸에 없다. 특히 `ADMIN_DISPLAY_NAME`을 포함했는지 확인하고 네 값을 모두 같은 셸에서
다시 설정한 뒤 실행한다. 비밀번호는 12자 이상, 표시 이름은 2–40자여야 한다.

배포 환경에서는 migration Job의 `ADMIN_*` 시크릿으로 동일 CLI가 실행된다.

## 컨텐츠 갱신

컨텐츠 submodule SHA를 갱신한 PR이 merge되면 images workflow가 새 API 이미지를 만든다. 홈랩
values의 API tag를 새 SHA로 바꾸면 migration Job이 마이그레이션과 컨텐츠 upsert를 실행한다.
원본 감소에 따른 자동 삭제는 하지 않는다. 삭제는 별도 데이터 검토 후 명시적 migration으로 한다.

## 백업

CNPG Cluster 데이터는 Longhorn volume에 저장된다. 공개 전 홈랩의 CNPG backup 대상에
`aws-study-postgres`를 추가하고 복구 테스트를 한 번 수행한다. 사용자 진도와 계정은 DB에만 있으므로
이미지 재배포로 복구되지 않는다.

## 롤백

1. 홈랩 values의 web/api tag를 직전 정상 SHA로 되돌리는 PR을 만든다.
2. ArgoCD sync 후 `/healthz`, `/readyz`, 로그인, 공개 AIF를 확인한다.
3. DB migration이 비호환이면 이미지 롤백만 하지 말고 대응 down migration 또는 backup 복구를 준비한다.

## 알림 권장 조건

- API readiness 5분 실패
- HTTP 5xx 비율 5분간 2% 초과
- Pod restart 증가
- PostgreSQL replica unavailable
- PVC 사용량 80% 초과
- 인증 실패율 급증
