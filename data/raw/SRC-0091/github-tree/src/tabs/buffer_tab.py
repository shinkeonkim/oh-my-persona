"""
Buffer/Socket Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable

from src.components import TCPClient
from src.utils import get_socket_buffer_size


class BufferTab:
    """Buffer/Socket Tab"""

    def __init__(
        self,
        parent: ttk.Frame,
        tcp_client: TCPClient,
        log_append: Callable[[tk.Text, str], None],
    ):
        """
        Initialize Buffer Tab

        Args:
            parent: Parent frame
            tcp_client: Shared TCP client instance
            log_append: Callback function to append logs to text widget
        """
        self.parent = parent
        self.tcp_client = tcp_client
        self._log_append = log_append

        self._build_ui()

    def _build_ui(self):
        """Build the UI components"""
        top = ttk.Frame(self.parent, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="클라 소켓 버퍼 조회", command=self._check_client_buffer).pack(
            side="left", padx=4
        )
        ttk.Button(top, text="임시 소켓 버퍼 조회", command=self._check_temp_buffer).pack(
            side="left", padx=4
        )

        self.output = scrolledtext.ScrolledText(self.parent, height=30)
        self.output.pack(fill="both", expand=True)

    def log(self, message: str):
        """Log a message to the output area"""
        self._log_append(self.output, message)

    def _check_client_buffer(self):
        """Check client socket buffer size"""
        if self.tcp_client.socket:
            result = get_socket_buffer_size(self.tcp_client.socket)
            self.log("[클라이언트 소켓]")
            self.log(result)
        else:
            self.log("[클라이언트 소켓] Not connected")

    def _check_temp_buffer(self):
        """Check temporary socket buffer size"""
        result = get_socket_buffer_size()
        self.log("[임시 소켓]")
        self.log(result)
