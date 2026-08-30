"""
Django 로깅 포맷터 모듈
로깅 포맷터 클래스들을 정의합니다.
"""

import logging

try:
    import sqlparse
except ImportError:
    sqlparse = None


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
            if sqlparse:
                formatted_sql = sqlparse.format(
                    record.sql, reindent=True, keyword_case="upper"
                )
            else:
                # sqlparse가 없으면 기본 SQL 출력
                formatted_sql = record.sql

            params = str(record.params) if record.params else "None"

            # 최종 포맷 구성 (SQL 쿼리를 별도 라인에 가독성 있게 표시)
            message = f"{message}\n\n{formatted_sql}\n\nParams: {params}\n"
            return message
        return super().format(record)
