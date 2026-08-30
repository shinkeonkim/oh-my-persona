#!/usr/bin/env python3
"""
NICE API 기관 토큰(ACCESS_TOKEN) 발급 스크립트
이 스크립트는 서버에서 구동하지 않고 독립적으로 실행됩니다.
발급받은 토큰은 환경변수(.env)에 추가하여 사용합니다.

사용법:
    python generate_nice_access_token.py

요구사항:
    - NICE API 홈페이지에서 Client ID, Client Secret 발급 필요
    - 서버 IP를 NICE API 홈페이지에 등록해야 함
"""

import base64
import sys

import requests

# =============================================================================
# 설정값 입력 (NICE API 홈페이지에서 발급받은 값으로 변경)
# =============================================================================
CLIENT_ID = ""  # NICE API APP 등록 시 발급받은 Client ID
CLIENT_SECRET = ""  # NICE API APP 등록 시 발급받은 Client Secret

# NICE API 토큰 발급 URL
TOKEN_URL = "https://svc.niceapi.co.kr:22001/digital/niceid/oauth/oauth/token"


def generate_access_token(client_id: str, client_secret: str) -> dict:
    """
    NICE API 기관 토큰 발급

    Args:
        client_id: NICE API Client ID
        client_secret: NICE API Client Secret

    Returns:
        dict: 토큰 정보 (access_token, expires_in 등)

    Raises:
        Exception: API 호출 실패 시
    """
    # Authorization 헤더를 위한 Basic Auth 생성
    access_auth = f"{client_id}:{client_secret}"
    access_base64_auth = base64.b64encode(access_auth.encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {access_base64_auth}",
    }

    data = {"grant_type": "client_credentials", "scope": "default"}

    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        data_header = response_data.get("dataHeader", {})
        data_body = response_data.get("dataBody", {})

        # 게이트웨이 결과 코드 확인
        gw_rslt_cd = data_header.get("GW_RSLT_CD")
        if gw_rslt_cd != "1200":
            raise Exception(
                f"API 호출 실패: GW_RSLT_CD={gw_rslt_cd}, "
                f"GW_RSLT_MSG={data_header.get('GW_RSLT_MSG', 'Unknown error')}"
            )

        print("response_data: ", response_data)

        return {
            "access_token": data_body.get("access_token"),
            "expires_in": data_body.get("expires_in"),
            "token_type": data_body.get("token_type"),
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP 요청 오류: {str(e)}")
    except Exception as e:
        raise Exception(f"토큰 발급 오류: {str(e)}")


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("NICE API 기관 토큰(ACCESS_TOKEN) 발급 스크립트")
    print("=" * 80)
    print()

    # 설정값 확인
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ 오류: CLIENT_ID와 CLIENT_SECRET을 설정해주세요.")
        print()
        print("스크립트 파일을 열어서 다음 변수를 수정하세요:")
        print("  - CLIENT_ID: NICE API에서 발급받은 Client ID")
        print("  - CLIENT_SECRET: NICE API에서 발급받은 Client Secret")
        print()
        sys.exit(1)

    print(f"Client ID: {CLIENT_ID}")
    print(f"Client Secret: {'*' * len(CLIENT_SECRET)}")
    print()

    try:
        print("토큰 발급 요청 중...")
        token_info = generate_access_token(CLIENT_ID, CLIENT_SECRET)

        print("✅ 토큰 발급 성공!")
        print()
        print("-" * 80)
        print("발급된 토큰 정보:")
        print("-" * 80)
        print(f"Access Token: {token_info['access_token']}")
        print(f"Expires In: {token_info['expires_in']}초 ({token_info['expires_in'] // 3600}시간)")
        print(f"Token Type: {token_info['token_type']}")
        print("-" * 80)
        print()
        print("📝 다음 단계:")
        print("1. 위의 Access Token 값을 복사하세요.")
        print("2. .env 파일을 열고 다음 변수를 추가/수정하세요:")
        print(f"   NICE_ACCESS_TOKEN={token_info['access_token']}")
        print()
        print("⚠️  주의: 이 토큰은 일정 시간 후 만료됩니다.")
        print(f"   만료 시간: 약 {token_info['expires_in'] // 3600}시간 후")
        print()

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print()
        print("문제 해결 방법:")
        print("1. CLIENT_ID와 CLIENT_SECRET이 올바른지 확인하세요.")
        print("2. 서버 IP가 NICE API 홈페이지에 등록되어 있는지 확인하세요.")
        print("3. 네트워크 연결 상태를 확인하세요.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
