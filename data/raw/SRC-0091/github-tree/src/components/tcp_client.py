"""
TCP Client with multiple transmission modes
"""

import socket
import struct
import threading
from typing import Callable, Optional
from enum import Enum


class TransmissionMode(Enum):
    """전송 모드"""

    VAR = "VAR"  # 동적 길이 (개행문자 구분)
    FIXED = "FIXED"  # 고정 32 바이트
    MIX = "MIX"  # 4바이트 길이 접두사 + 페이로드


class TCPClient:
    """여러 전송 모드를 지원하는 TCP 클라이언트"""

    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.recv_thread: Optional[threading.Thread] = None
        self.running = False
        self.log_callback: Optional[Callable[[str], None]] = None
        self.data_callback: Optional[Callable[[str], None]] = None

    def set_log_callback(self, callback: Callable[[str], None]):
        """로그 콜백 함수 설정"""
        self.log_callback = callback

    def set_data_callback(self, callback: Callable[[str], None]):
        """데이터 수신 콜백 함수 설정"""
        self.data_callback = callback

    def log(self, message: str):
        """콜백을 통한 로그 메시지 출력"""
        if self.log_callback:
            self.log_callback(message)

    def connect(self, host: str, port: int):
        """서버에 연결"""
        if self.connected:
            self.log("[클라이언트] 이미 연결됨")
            return

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self.running = True

            # 수신 스레드 시작
            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.recv_thread.start()

            self.log(f"[클라이언트] Connected to {host}:{port}")
        except Exception as e:
            self.log(f"[클라이언트] Connection failed: {e}")
            self.connected = False

    def disconnect(self, after_send: bool = False):
        """서버와 연결 종료"""
        if not self.connected:
            return

        self.running = False
        self.connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        # 현재 스레드가 수신 스레드가 아니면 조인
        if self.recv_thread and self.recv_thread.is_alive():
            if threading.current_thread() != self.recv_thread:
                self.recv_thread.join(timeout=2.0)

        close_reason = "after send" if after_send else "requested"
        self.log(f"[클라이언트] Disconnected ({close_reason})")

    def send(self, message: str, mode: TransmissionMode, close_after: bool = False):
        """지정된 모드로 메시지 전송"""
        if not self.connected:
            self.log("[클라이언트] Not connected")
            return

        try:
            if mode == TransmissionMode.VAR:
                self._send_var(message)
            elif mode == TransmissionMode.FIXED:
                self._send_fixed(message)
            elif mode == TransmissionMode.MIX:
                self._send_mix(message)

            self.log(f"[클라이언트] Sent ({mode.value}): {message}")

            if close_after:
                self.disconnect(after_send=True)

        except Exception as e:
            self.log(f"[클라이언트] Send error: {e}")

    def _send_var(self, message: str):
        """newline 구분자 사용 동적 길이 메시지 전송"""
        data = message.encode("utf-8")
        if not data.endswith(b"\n"):
            data += b"\n"
        self.socket.send(data)

    def _send_fixed(self, message: str):
        """고정 32바이트 메시지 전송"""
        data = message.encode("utf-8")
        if len(data) > 32:
            data = data[:32]
        else:
            data = data.ljust(32, b"\x00")
        self.socket.send(data)

    def _send_mix(self, message: str):
        """4바이트 길이 접두사 + 페이로드 메시지 전송"""
        data = message.encode("utf-8")
        length = len(data)
        length_prefix = struct.pack("!I", length)
        self.socket.send(length_prefix + data)

    def _recv_loop(self):
        """수신 루프"""
        try:
            self.socket.settimeout(1.0)
            while self.running and self.connected:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break

                    decoded = data.decode('utf-8', errors='ignore')
                    self.log(f"[클라이언트] Received: {decoded}")

                    # 데이터 콜백 호출 (드로잉 보드 동기화용)
                    if self.data_callback:
                        self.data_callback(decoded)

                except socket.timeout:
                    continue
        except Exception as e:
            if self.running:
                self.log(f"[클라이언트] Receive error: {e}")
        finally:
            if self.connected:
                self.disconnect()
