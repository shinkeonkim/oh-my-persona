"""
TCP Server Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable

from src.components import TCPServer


class ServerTab:
    """TCP Server Tab"""

    def __init__(
        self,
        parent: ttk.Frame,
        tcp_server: TCPServer,
        log_append: Callable[[tk.Text, str], None],
    ):
        """
        Initialize Server Tab

        Args:
            parent: Parent frame
            tcp_server: Shared TCP server instance
            log_append: Callback function to append logs to text widget
        """
        self.parent = parent
        self.tcp_server = tcp_server
        self._log_append = log_append

        self._build_ui()

        # Set log callback
        self.tcp_server.set_log_callback(self.log)

    def _build_ui(self):
        """Build the UI components"""
        top = ttk.Frame(self.parent, padding=8)
        top.pack(fill="x")
        self.var_port = tk.StringVar(value="9000")
        ttk.Label(top, text="포트").pack(side="left")
        ttk.Entry(top, textvariable=self.var_port, width=6).pack(side="left", padx=4)

        self.var_broadcast = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top, text="그림판 브로드캐스트", variable=self.var_broadcast
        ).pack(side="left", padx=6)

        ttk.Button(top, text="서버 시작", command=self._start_server).pack(
            side="left", padx=4
        )
        ttk.Button(top, text="서버 정지", command=self._stop_server).pack(
            side="left", padx=4
        )

        stat = ttk.Frame(self.parent, padding=8)
        stat.pack(fill="x")
        self.lbl_clients = ttk.Label(stat, text="접속: 0")
        self.lbl_clients.pack(side="left")
        self.lbl_counter = ttk.Label(stat, text="카운터: 0")
        self.lbl_counter.pack(side="left", padx=12)
        ttk.Button(stat, text="상태 갱신", command=self._update_status).pack(
            side="left"
        )

        self.output = scrolledtext.ScrolledText(self.parent, height=28)
        self.output.pack(fill="both", expand=True)

    def log(self, message: str):
        """Log a message to the output area"""
        self._log_append(self.output, message)

    def _start_server(self):
        """Start the TCP server"""
        port = int(self.var_port.get())
        enable_broadcast = self.var_broadcast.get()
        self.tcp_server.port = port
        self.tcp_server.enable_broadcast = enable_broadcast
        self.tcp_server.start()

    def _stop_server(self):
        """Stop the TCP server"""
        self.tcp_server.stop()

    def _update_status(self):
        """Update server status display"""
        status = self.tcp_server.get_status()
        self.lbl_clients.config(text=f"접속: {status['clients']}")
        self.lbl_counter.config(text=f"카운터: {status['counter']}")
        self.log(
            f"[서버] 상태 - Running: {status['running']}, Clients: {status['clients']}, Counter: {status['counter']}"
        )
