import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class ColoredFormatter(logging.Formatter):
    """컬러풀한 로그 포맷터"""

    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        if hasattr(record, "correlation_id"):
            record.correlation_id = f"[{record.correlation_id}]"
        else:
            record.correlation_id = ""

        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"

        return super().format(record)


def get_logging_config():
    """환경별 로깅 설정을 반환"""

    # 로그 디렉토리 생성
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    # 기본 포맷
    verbose_format = "{asctime} | {levelname} | {correlation_id} | " "{name} | {module}.{funcName}:{lineno} | {message}"

    simple_format = "{asctime} | {levelname} | {correlation_id} | {message}"

    sql_format = "{asctime} | SQL | {correlation_id} | {sql}"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": verbose_format,
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": simple_format,
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "colored": {
                "()": ColoredFormatter,
                "format": verbose_format,
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "sql": {
                "format": sql_format,
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "filters": {
            "correlation_id": {
                "()": "django_guid.log_filters.CorrelationId",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
                "filters": ["correlation_id"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "django.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "verbose",
                "filters": ["correlation_id"],
            },
            "sql_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "sql.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 3,
                "formatter": "sql",
                "filters": ["correlation_id"],
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "error.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "verbose",
                "filters": ["correlation_id"],
                "level": "ERROR",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["sql_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["console", "file", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["console", "file", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "django_guid": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "user": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "api": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    }

    return config


# Django 설정에서 사용할 LOGGING 변수
LOGGING = get_logging_config()


# Django GUID 설정
DJANGO_GUID = {
    "GUID_HEADER_NAME": "Correlation-ID",
    "VALIDATE_GUID": True,
    "RETURN_HEADER": True,
    "EXPOSE_HEADER": True,
    "INTEGRATIONS": [],
    "IGNORE_URLS": [
        "/health/",
        "/favicon.ico",
    ],
    "UUID_LENGTH": 32,
}
