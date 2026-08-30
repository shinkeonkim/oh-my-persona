"""
네트워크 진단 및 변환을 위한 유틸리티 함수들
"""

import socket
import struct
import subprocess
import platform
from typing import Optional, Tuple


def get_ip_config() -> str:
  """ifconfig 또는 ipconfig를 사용하여 IP 구성 정보를 가져옵니다."""
  system = platform.system()
  try:
    if system == "Windows":
      result = subprocess.run(
        ["ipconfig"], capture_output=True, text=True, timeout=5
      )
    else:
      result = subprocess.run(
        ["ifconfig"], capture_output=True, text=True, timeout=5
      )
    return result.stdout
  except Exception as e:
    return f"Error: {str(e)}"


def get_netstat_filtered(port: str) -> str:
  """포트로 필터링된 netstat 출력 가져오기"""
  system = platform.system()
  try:
    if system == "Windows":
      result = subprocess.run(
        ["netstat", "-a", "-n", "-p", "tcp"],
        capture_output=True,
        text=True,
        timeout=5,
      )
      lines = result.stdout.split("\n")
      filtered = [line for line in lines if port in line]
      return "\n".join(filtered)
    else:
      result = subprocess.run(
        ["netstat", "-an"],  # or ss -tan
        capture_output=True,
        text=True,
        timeout=5,
      )
      lines = result.stdout.split("\n")
      filtered = [line for line in lines if port in line]
      return "\n".join(filtered)
  except Exception as e:
    return f"Error: {str(e)}"


def check_port_open(host: str, port: int, timeout: float = 2.0) -> Tuple[bool, str]:
  """호스트의 포트가 열려 있는지 확인합니다"""
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()

    if result == 0:
      return True, f"Port {port} on {host} is OPEN"
    else:
      return False, f"Port {port} on {host} is CLOSED"
  except socket.gaierror:
    return False, f"Hostname {host} could not be resolved"
  except socket.error as e:
    return False, f"Connection error: {str(e)}"


def demo_byte_order() -> str:
  """htonl, htons, ntohl, ntohs를 시연합니다"""
  output = []

  # 16-bit examples
  host_short = 0x1234
  net_short = socket.htons(host_short)
  output.append(f"16-bit Host to Network:")
  output.append(f"  htons(0x{host_short:04x}) = 0x{net_short:04x}")
  output.append(f"  ntohs(0x{net_short:04x}) = 0x{socket.ntohs(net_short):04x}")

  # 32-bit examples
  host_long = 0x12345678
  net_long = socket.htonl(host_long)
  output.append(f"\n32-bit Host to Network:")
  output.append(f"  htonl(0x{host_long:08x}) = 0x{net_long:08x}")
  output.append(f"  ntohl(0x{net_long:08x}) = 0x{socket.ntohl(net_long):08x}")

  return "\n".join(output)


def demo_inet_pton_ipv4(addr: str) -> str:
  """IPv4에 대한 inet_pton 및 inet_ntop 시연"""
  try:
    packed = socket.inet_pton(socket.AF_INET, addr)
    output = [f"IPv4 Address: {addr}"]
    output.append(
      f"inet_pton (binary): {' '.join(f'{b:02x}' for b in packed)}"
    )

    unpacked = socket.inet_ntop(socket.AF_INET, packed)
    output.append(f"inet_ntop (string): {unpacked}")

    as_int = struct.unpack("!I", packed)[0]
    output.append(f"As integer: {as_int} (0x{as_int:08x})")

    return "\n".join(output)
  except Exception as e:
    return f"Error: {str(e)}"


def demo_inet_pton_ipv6(addr: str) -> str:
  """IPv6에 대한 inet_pton 및 inet_ntop 시연"""
  try:
    packed = socket.inet_pton(socket.AF_INET6, addr)
    output = [f"IPv6 Address: {addr}"]
    output.append(
        f"inet_pton (binary): {' '.join(f'{b:02x}' for b in packed)}"
    )

    unpacked = socket.inet_ntop(socket.AF_INET6, packed)
    output.append(f"inet_ntop (string): {unpacked}")

    return "\n".join(output)
  except Exception as e:
    return f"Error: {str(e)}"


def dns_lookup(hostname: str) -> str:
  """DNS 조회 수행"""
  try:
    addr_info = socket.getaddrinfo(hostname, None)
    output = [f"DNS Lookup for: {hostname}\n"]

    for family, socktype, proto, canonname, sockaddr in addr_info:
      family_name = "IPv4" if family == socket.AF_INET else "IPv6"
      output.append(f"  {family_name}: {sockaddr[0]}")

    try:
      ipv4 = socket.gethostbyname(hostname)
      output.append(f"\ngethostbyname: {ipv4}")
    except:
      pass

    return "\n".join(output)
  except Exception as e:
    return f"Error: {str(e)}"


def reverse_dns_lookup(ip_addr: str) -> str:
  """역방향 DNS 조회 수행"""
  try:
    hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip_addr)
    output = [f"Reverse DNS for: {ip_addr}"]
    output.append(f"Hostname: {hostname}")
    if aliaslist:
      output.append(f"Aliases: {', '.join(aliaslist)}")
    if ipaddrlist:
      output.append(f"IP Addresses: {', '.join(ipaddrlist)}")
    return "\n".join(output)
  except socket.herror as e:
    return f"Error: {str(e)}"
  except Exception as e:
    return f"Error: {str(e)}"


def get_socket_buffer_size(sock: Optional[socket.socket] = None) -> str:
  """소켓 버퍼 크기 가져오기 (SO_SNDBUF 및 SO_RCVBUF)"""
  try:
    close_after = False
    if sock is None:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      close_after = True

    send_buf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    recv_buf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

    if close_after:
      sock.close()

    output = [
      f"Socket Buffer Sizes:",
      f"  SO_SNDBUF (Send Buffer): {send_buf} bytes",
      f"  SO_RCVBUF (Receive Buffer): {recv_buf} bytes",
    ]
    return "\n".join(output)
  except Exception as e:
    return f"Error: {str(e)}"
