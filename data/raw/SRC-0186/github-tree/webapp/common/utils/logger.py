"""
표준화된 로깅 유틸리티

이 모듈은 프로젝트 전체에서 일관된 로깅을 위해 사용됩니다.
"""

import functools
import logging
import time
from typing import Optional

from common.utils.request import get_client_ip


class StandardLogger:
  """표준화된 로거 클래스"""

  def __init__(self, name: str):
    self.logger = logging.getLogger(name)

  def debug(self, message: str, **kwargs):
    """디버그 로그 (개발/디버깅용)"""
    self._log(logging.DEBUG, message, **kwargs)

  def info(self, message: str, **kwargs):
    """정보 로그 (일반적인 정보)"""
    self._log(logging.INFO, message, **kwargs)

  def warning(self, message: str, **kwargs):
    """경고 로그 (주의가 필요한 상황)"""
    self._log(logging.WARNING, message, **kwargs)

  def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
    """에러 로그 (에러 발생)"""
    self._log(logging.ERROR, message, exception=exception, **kwargs)

  def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
    """치명적 에러 로그 (시스템 중단 수준)"""
    self._log(logging.CRITICAL, message, exception=exception, **kwargs)

  def _log(self, level: int, message: str, exception: Optional[Exception] = None, **kwargs):
    """내부 로그 메서드"""
    # 추가 컨텍스트 정보가 있으면 메시지에 포함
    if kwargs:
      context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
      message = f"{message} | {context}"

    # 예외 정보가 있으면 exc_info=True로 로깅
    if exception:
      self.logger.log(level, message, exc_info=True)
    else:
      self.logger.log(level, message)


def get_logger(name: str) -> StandardLogger:
  """
    표준화된 로거 인스턴스를 반환합니다.

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        StandardLogger: 표준화된 로거 인스턴스

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("User created", user_id=123)
        >>> logger.error("Database error", exception=e, table="users")
    """
  return StandardLogger(name)


def log_execution_time(logger: StandardLogger, operation_name: str = None):
  """
    함수 실행 시간을 로깅하는 데코레이터

    Args:
        logger: 로거 인스턴스
        operation_name: 작업 이름 (기본값: 함수명)

    Example:
        >>> @log_execution_time(logger, "user_creation")
        >>> def create_user(data):
        >>>     # 함수 내용
        >>>     pass
    """

  def decorator(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      operation = operation_name or func.__name__
      start_time = time.time()

      logger.info(f"Starting {operation}")

      try:
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"Completed {operation}", execution_time=f"{execution_time:.3f}s")
        return result
      except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
          f"Failed {operation}",
          exception=e,
          execution_time=f"{execution_time:.3f}s",
        )
        raise

    return wrapper

  return decorator


def log_api_call(logger: StandardLogger, endpoint: str = None):
  """
    API 호출을 로깅하는 데코레이터

    Args:
        logger: 로거 인스턴스
        endpoint: API 엔드포인트 (기본값: 함수명)

    Example:
        >>> @log_api_call(logger, "POST /api/users/")
        >>> def create_user(request):
        >>>     # API 로직
        >>>     pass
    """

  def decorator(func):

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
      api_endpoint = endpoint or f"{request.method} {request.path}"
      user_id = getattr(request.user, "id", None) if hasattr(request, "user") else None

      logger.info(
        "API call started",
        endpoint=api_endpoint,
        user_id=user_id,
        ip_address=get_client_ip(request),
      )

      try:
        result = func(self, request, *args, **kwargs)
        logger.info("API call completed", endpoint=api_endpoint, user_id=user_id)
        return result
      except Exception as e:
        logger.error(
          "API call failed",
          exception=e,
          endpoint=api_endpoint,
          user_id=user_id,
        )
        raise

    return wrapper

  return decorator


def log_database_operation(logger: StandardLogger, operation: str = None):
  """
    데이터베이스 작업을 로깅하는 데코레이터

    Args:
        logger: 로거 인스턴스
        operation: 작업 유형 (기본값: 함수명)

    Example:
        >>> @log_database_operation(logger, "user_query")
        >>> def get_user_by_id(user_id):
        >>>     # DB 쿼리
        >>>     pass
    """

  def decorator(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      db_operation = operation or func.__name__

      logger.debug("Database operation started", operation=db_operation)

      try:
        result = func(*args, **kwargs)
        logger.debug("Database operation completed", operation=db_operation)
        return result
      except Exception as e:
        logger.error("Database operation failed", exception=e, operation=db_operation)
        raise

    return wrapper

  return decorator


# 편의를 위한 모듈 레벨 함수들
def get_module_logger(module_name: str) -> StandardLogger:
  """모듈명으로 로거를 생성합니다."""
  return get_logger(module_name)


def get_class_logger(cls) -> StandardLogger:
  """클래스명으로 로거를 생성합니다."""
  return get_logger(f"{cls.__module__}.{cls.__name__}")


# 로깅 가이드라인 상수
class LogLevels:
  """로그 레벨 가이드라인"""

  DEBUG = "개발/디버깅용 상세 정보"
  INFO = "일반적인 정보 (사용자 액션, 시스템 상태)"
  WARNING = "주의가 필요한 상황 (성능 이슈, 예상치 못한 상황)"
  ERROR = "에러 발생 (기능 동작 실패)"
  CRITICAL = "치명적 에러 (시스템 중단 수준)"


class LogMessages:
  """표준화된 로그 메시지 템플릿"""

  # API 관련
  API_START = "API call started"
  API_SUCCESS = "API call completed successfully"
  API_ERROR = "API call failed"

  # 데이터베이스 관련
  DB_QUERY_START = "Database query started"
  DB_QUERY_SUCCESS = "Database query completed"
  DB_QUERY_ERROR = "Database query failed"

  # 비즈니스 로직 관련
  BUSINESS_START = "Business operation started"
  BUSINESS_SUCCESS = "Business operation completed"
  BUSINESS_ERROR = "Business operation failed"

  # 외부 서비스 관련
  EXTERNAL_SERVICE_START = "External service call started"
  EXTERNAL_SERVICE_SUCCESS = "External service call completed"
  EXTERNAL_SERVICE_ERROR = "External service call failed"
