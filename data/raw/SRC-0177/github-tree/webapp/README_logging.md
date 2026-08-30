# Django 로깅 가이드

이 프로젝트에서는 향상된 로깅 시스템을 구현하여 환경별로 가독성 높은 로그를 제공합니다.

## 로깅 설정 특징

1. **환경별 설정**: DEBUG 플래그에 따라 로그 수준이 자동으로 조절됩니다
   - 개발 환경(DEBUG=True): 상세한 디버그 로그 및 SQL 쿼리 출력
   - 운영 환경(DEBUG=False): 중요 로그와 오류만 출력

2. **가독성 향상**:
   - **색상화된 콘솔 로그**: 심각도에 따라 다른 색상으로 로그 표시 (colorlog 사용)
   - **SQL 쿼리 가독성 향상**: SQL 쿼리를 자동으로 포맷팅하여 가독성 높게 표시 (sqlparse 사용)

3. **효율적인 로그 관리**:
   - **로그 분리**: 일반 로그, SQL 로그, 오류 로그를 별도 파일로 분리
   - **로그 회전**: 파일 크기에 따라 로그 파일이 자동으로 회전됨
   - **앱별 로거**: 각 Django 앱마다 별도의 로거 설정

### 로그 확인 방법

1. **콘솔 로그**: 서버 실행 시 콘솔에 자동으로 표시됩니다.
2. **파일 로그**: 다음 위치에 로그 파일이 생성됩니다:
   - 일반 로그: `webapp/logs/django-<environment>.log`
   - SQL 로그: `webapp/logs/django-sql-<environment>.log`
   - 오류 로그: `webapp/logs/django-error-<environment>.log`

### 커스텀 로그 작성

코드에서 다음과 같이 로거를 사용할 수 있습니다:

```python
import logging

# 앱 이름을 기반으로 로거 가져오기
# 'user', 'meme', 'bookmark', 'file_manager', 'tag', 'api' 등
logger = logging.getLogger('user')  # 또는 해당 앱 이름

# 로그 레벨에 따라 로깅
logger.debug("상세 디버그 정보")
logger.info("정보성 메시지")
logger.warning("경고 메시지")
logger.error("오류 메시지")
logger.critical("심각한 오류 메시지")
```

## 환경별 로그 레벨

### 개발 환경 (DEBUG=True)
- 앱 로거: DEBUG 레벨부터 출력
- SQL 쿼리: 모든 쿼리 출력 (DEBUG 레벨)
- 루트 로거: INFO 레벨부터 출력

### 운영 환경 (DEBUG=False)
- 앱 로거: INFO 레벨부터 출력
- SQL 쿼리: WARNING 레벨부터 출력 (느린 쿼리만)
- 루트 로거: INFO 레벨부터 출력

## 로그 설정 커스터마이징

`logging_config.py` 파일을 수정하여 로그 설정을 커스터마이징할 수 있습니다.
이 파일은 모든 환경 설정 파일에서 공유됩니다.
