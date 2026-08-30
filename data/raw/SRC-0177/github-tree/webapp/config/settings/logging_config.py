"""Django 로깅 설정 모듈
환경별 로깅 설정을 제공합니다.
"""

import logging
import os


# Django 앱 초기화 여부를 확인하는 함수
def is_django_initialized():
    try:
        from django.apps import apps

        return apps.apps_ready
    except Exception:
        return False


def create_simple_logging_config():
    """
    여러 환경에서 공통적으로 사용할 수 있는 간단한 로그 설정
    유틸리티 프로세스(Celery, Flower 등)에서 사용하기 적합합니다.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(levelname)s [%(asctime)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }


def get_logging_config(base_dir, debug=False, environment="dev"):
    """
    로깅 설정을 반환합니다.

    Args:
        base_dir: 프로젝트 베이스 디렉토리
        debug: DEBUG 모드 여부
        environment: 환경 (dev, test, prod 등)

    Returns:
        dict: Django 로깅 설정 딕셔너리
    """
    # 로그 디렉토리가 없으면 생성
    log_dir = f"{base_dir}/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 필요한 패키지들 확인
    try:
        import sqlparse

        has_sqlparse = True
    except ImportError:
        has_sqlparse = False

    try:
        import colorlog  # noqa: F401

        has_colorlog = True
    except ImportError:
        has_colorlog = False

    # SQL 포맷터 정의
    class SQLFormatter(logging.Formatter):
        """
        SQL 쿼리에 대한 사용자 정의 포맷터
        SQL 쿼리를 가독성 있게 표시합니다.
        """

        def format(self, record):
            # SQL 쿼리인 경우 포맷팅 적용
            if hasattr(record, "sql") and record.sql:
                # 기본 정보 포맷팅
                message = super().format(record)

                # SQL과 파라미터를 별도 라인으로 표시
                if has_sqlparse:
                    formatted_sql = sqlparse.format(
                        record.sql, reindent=True, keyword_case="upper"
                    )
                else:
                    # sqlparse가 없으면 기본 SQL 출력
                    formatted_sql = record.sql

                params = (
                    str(record.params)
                    if hasattr(record, "params") and record.params
                    else "None"
                )

                # 최종 포맷 구성 (SQL 쿼리를 별도 라인에 가독성 있게 표시)
                message = f"{message}\n\n{formatted_sql}\n\nParams: {params}\n"
                return message
            return super().format(record)

    # 기본 로그 레벨 설정 (DEBUG 모드에 따라 다름)
    default_level = "DEBUG" if debug else "INFO"
    sql_level = "DEBUG" if debug else "WARNING"  # 비 디버그 모드에서는 느린 쿼리만 로깅

    # 포맷터 설정
    formatters = {
        "verbose": {
            "format": "%(levelname)s [%(asctime)s] [%(correlation_id)s] %(name)s: %(message)s"
        },
        "simple": {"format": "%(levelname)s [%(asctime)s] %(name)s: %(message)s"},
        "sql": {
            "()": SQLFormatter,
            "format": "\n%(levelname)s [%(asctime)s] [%(correlation_id)s] %(name)s\n",
        },
    }

    # colorlog 패키지가 있으면 컬러 포맷터 추가
    if has_colorlog:
        formatters["colored"] = {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s %(white)s[%(asctime)s] %(blue)s[%(correlation_id)s] %(cyan)s%(name)s: %(message)s",  # noqa: E501
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "green",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        }
    else:
        # colorlog가 없으면 일반 포맷터로 대체
        formatters["colored"] = formatters["verbose"]

    # 로깅 설정
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored" if has_colorlog and debug else "simple",
                "filters": ["correlation_id"],
            },
            "console_sql": {
                "class": "logging.StreamHandler",
                "formatter": "sql",
                "filters": ["correlation_id"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/django-{environment}.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "verbose",
                "filters": ["correlation_id"],
            },
            "file_sql": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/django-sql-{environment}.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "sql",
                "filters": ["correlation_id"],
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/django-error-{environment}.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "verbose",
                "filters": ["correlation_id"],
                "level": "ERROR",
            },
        },
        "filters": {
            "correlation_id": {"()": "django_guid.log_filters.CorrelationId"},
            "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        },
        "formatters": formatters,
    }

    # 기본 로거 설정
    base_loggers = {
        # Django 관련 로거
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console_sql", "file_sql"] if debug else ["file_sql"],
            "level": sql_level,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file", "file_error"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        # 라이브러리 로거
        "nplusone": {
            "handlers": ["console", "file"],
            "level": "WARNING" if not debug else "INFO",
            "propagate": False,
        },
        # 루트 로거
        "": {  # Root logger
            "handlers": ["console", "file", "file_error"],
            "level": default_level,
        },
    }

    # 앱 로거는 Django가 초기화된 경우에만 추가
    try:
        # 이미 초기화된 경우에만 앱 로거 추가
        if "DJANGO_SETTINGS_MODULE" in os.environ and is_django_initialized():
            # 앱 로거 - 사용자 정의 앱
            app_loggers = {
                "user": {
                    "handlers": ["console", "file", "file_error"],
                    "level": default_level,
                    "propagate": False,
                },
                "bookmark": {
                    "handlers": ["console", "file", "file_error"],
                    "level": default_level,
                    "propagate": False,
                },
                "meme": {
                    "handlers": ["console", "file", "file_error"],
                    "level": default_level,
                    "propagate": False,
                },
                "file_manager": {
                    "handlers": ["console", "file", "file_error"],
                    "level": default_level,
                    "propagate": False,
                },
                "tag": {
                    "handlers": ["console", "file", "file_error"],
                    "level": default_level,
                    "propagate": False,
                },
                "api": {
                    "handlers": ["console", "file", "file_error"],
                    "level": default_level,
                    "propagate": False,
                },
            }
            # 기본 로거에 앱 로거 추가
            base_loggers.update(app_loggers)
    except Exception:
        # 초기화되지 않았거나 오류 발생 시 무시
        pass

    # 최종 로깅 설정에 로거 추가
    logging_config["loggers"] = base_loggers

    return logging_config
