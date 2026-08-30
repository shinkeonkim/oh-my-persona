# Celery와 Flower 로깅 설정 가이드

이 문서는 Celery와 Flower에서 발생하는 로깅 문제 해결 방법을 설명합니다.

## 문제 상황

Celery와 Flower와 같은 워커 프로세스에서는 Django 설정이 불러와지기 전에 로깅 설정이 필요할 수 있습니다. 문제는 특히 다음과 같은 에러로 나타납니다:

```
ValueError: Cannot resolve 'logging_config.SQLFormatter': No module named 'logging_config'
```

## 해결 방법

1. **단순화된 로깅 설정 사용**:
   - Celery 워커가 시작할 때 간단한 로깅 설정을 먼저 적용합니다.
   - `create_simple_logging_config()` 함수는 모든 외부 의존성 없이 동작하는 기본 로깅 설정을 제공합니다.

2. **Django 로딩 전 로깅 초기화**:
   - `celery.py` 파일에서 Django가 완전히 로드되기 전에 로깅 설정을 초기화합니다.
   - 이로써 Django 로깅 설정의 의존성 문제를 방지합니다.

3. **SQLFormatter를 직접 전달**:
   - 로깅 설정에서 문자열 경로 대신 직접 클래스 인스턴스를 전달하여 임포트 문제를 방지합니다.

## 로깅 의존성 관리

1. **조건부 기능 활성화**:
   - `sqlparse`와 `colorlog` 패키지가 없는 경우에도 기본 기능이 동작하도록 설계되었습니다.
   - 패키지 존재 여부를 확인하고 기능을 조건부로 활성화합니다.

2. **독립적인 설정 구조**:
   - 유틸리티 프로세스용 간단한 로깅 설정과 Django 앱용 상세 로깅 설정이 분리되어 있습니다.

## 추가 설정 팁

1. **로그 디렉토리 설정**:
   - 모든 로그 파일은 프로젝트 루트의 `logs` 디렉토리에 저장됩니다.
   - 디렉토리가 없으면 자동으로 생성됩니다.

2. **환경별 로그 수준**:
   - 개발 환경: 자세한 로그 및 SQL 쿼리가 표시됩니다.
   - 프로덕션 환경: 중요한 메시지와 오류만 표시됩니다.

## 커스텀 로깅 사용법

Celery 태스크에서 로깅을 사용하려면:

```python
import logging
logger = logging.getLogger(__name__)

@app.task
def my_task():
    logger.info("태스크 시작")
    try:
        # 작업 수행
        logger.debug("작업 세부 정보")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
    logger.info("태스크 완료")
```
