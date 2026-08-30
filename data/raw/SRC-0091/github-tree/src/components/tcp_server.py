"""
TCP Server with multi-threading support
"""

import socket
import threading
from typing import Callable, Optional


class TCPServer:
    """멀티스레드 TCP 서버"""

    def __init__(self, port: int = 9000, enable_broadcast: bool = True):
        self.port = port
        self.enable_broadcast = enable_broadcast
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.accept_thread: Optional[threading.Thread] = None
        self.client_threads = []
        self.clients = []
        self.client_counter = 0
        self.counter_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.log_callback: Optional[Callable[[str], None]] = None

    def set_log_callback(self, callback: Callable[[str], None]):
        """로그 콜백 함수 설정"""
        self.log_callback = callback

    def log(self, message: str):
        """콜백을 통한 로그 메시지 출력"""
        if self.log_callback:
            self.log_callback(message)

    def start(self):
        """TCP 서버 시작"""
        if self.running:
            self.log("[서버] 이미 실행 중")
            return

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # 주기적 확인용 타임아웃

            self.running = True
            self.stop_event.clear()

            # 수락 스레드 시작
            self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.accept_thread.start()

            self.log(f"[서버] Started on port {self.port}")
        except Exception as e:
            self.log(f"[서버] Error starting server: {e}")
            self.running = False

    def stop(self):
        """TCP 서버 중지"""
        if not self.running:
            return

        self.log("[서버] 중지 중...")
        self.running = False
        self.stop_event.set()

        # 모든 클라이언트 소켓 닫기
        for client_sock, _ in list(self.clients):
            try:
                client_sock.close()
            except:
                pass

        # 서버 소켓 닫기
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # 스레드 대기
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(timeout=2.0)

        for thread in self.client_threads:
            if thread.is_alive():
                thread.join(timeout=2.0)

        self.clients.clear()
        self.client_threads.clear()
        self.log("[서버] Stopped")

    def _accept_loop(self):
        """수신 대기 루프"""
        while self.running and not self.stop_event.is_set():
            try:
                client_socket, client_address = self.server_socket.accept()
                self.log(f"[서버] Client connected: {client_address}")

                # 카운터 증가 (임계 구역)
                with self.counter_lock:
                    self.client_counter += 1

                # 클라이언트 목록에 추가
                self.clients.append((client_socket, client_address))

                # Start client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True,
                )
                client_thread.start()
                self.client_threads.append(client_thread)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.log(f"[서버] Accept error: {e}")
                break

    def _handle_client(self, client_socket: socket.socket, client_address):
        """개별 클라이언트 연결 처리"""
        try:
            while self.running and not self.stop_event.is_set():
                data = client_socket.recv(4096)
                if not data:
                    break

                self.log(f"[서버] Received from {client_address}: {len(data)} bytes")

                # Echo back or broadcast
                if self.enable_broadcast:
                    self._broadcast(data, client_socket)
                else:
                    client_socket.send(data)

        except Exception as e:
            self.log(f"[서버] Client {client_address} error: {e}")
        finally:
            client_socket.close()
            self.clients = [(s, a) for s, a in self.clients if s != client_socket]
            self.log(f"[서버] Client disconnected: {client_address}")

    def _broadcast(self, data: bytes, sender_socket: socket.socket):
        """Broadcast data to all clients except sender"""
        for client_sock, client_addr in list(self.clients):
            if client_sock != sender_socket:
                try:
                    client_sock.send(data)
                except:
                    pass

    def broadcast(self, message: str):
        """모든 연결된 클라이언트에게 메시지 브로드캐스트 (공용 메서드)"""
        if not self.running:
            return

        data = message.encode("utf-8")
        for client_sock, client_addr in list(self.clients):
            try:
                client_sock.send(data)
            except Exception as e:
                self.log(f"[서버] Broadcast error to {client_addr}: {e}")

    def get_status(self) -> dict:
        """서버 상태 가져오기"""
        return {
            "running": self.running,
            "clients": len(self.clients),
            "counter": self.client_counter,
            "port": self.port,
        }
