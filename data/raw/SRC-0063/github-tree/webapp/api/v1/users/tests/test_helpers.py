"""테스트용 헬퍼 함수"""


def get_error_details(response_data):
    """
    커스텀 에러 핸들러의 응답 구조를 처리하는 헬퍼 함수

    커스텀 에러 핸들러: {'status': 'FAIL', 'details': {...}}
    일반 DRF: {...}
    """
    return response_data.get("details", response_data)
