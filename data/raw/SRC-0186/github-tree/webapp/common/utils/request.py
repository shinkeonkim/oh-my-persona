"""
Request 관련 유틸리티 함수
"""


def get_client_ip(request):
  """
    클라이언트의 실제 IP 주소를 추출합니다.

    Traefik → Nginx → Django 구조에서 실제 클라이언트 IP를 추출합니다.
    X-Forwarded-For 헤더의 첫 번째 IP (실제 클라이언트 IP)를 반환합니다.

    Args:
        request: Django HttpRequest 객체

    Returns:
        str: 클라이언트 IP 주소
    """
  # X-Forwarded-For 헤더에서 실제 클라이언트 IP 추출
  # 형식: "client_ip, proxy1_ip, proxy2_ip, ..."
  # Traefik이 실제 클라이언트 IP를 첫 번째로 추가
  x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
  if x_forwarded_for:
    # 첫 번째 IP가 실제 클라이언트 IP
    ip = x_forwarded_for.split(",")[0].strip()
    return ip

  # X-Forwarded-For가 없으면 REMOTE_ADDR 사용 (직접 연결)
  ip = request.META.get("REMOTE_ADDR")
  return ip


def get_all_forwarded_ips(request):
  """
    X-Forwarded-For 헤더의 모든 IP 주소를 리스트로 반환합니다.

    Args:
        request: Django HttpRequest 객체

    Returns:
        list: 모든 프록시 체인의 IP 주소 리스트 [client_ip, proxy1_ip, proxy2_ip, ...]
              X-Forwarded-For가 없으면 REMOTE_ADDR만 포함된 리스트 반환
    """
  x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
  if x_forwarded_for:
    return [ip.strip() for ip in x_forwarded_for.split(",")]

  remote_addr = request.META.get("REMOTE_ADDR")
  return [remote_addr] if remote_addr else []
