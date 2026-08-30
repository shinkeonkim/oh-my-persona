"""
TCP Client Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable

from src.components import TCPClient, TransmissionMode


class ClientTab:
    """TCP Client Tab"""

    def __init__(
        self,
        parent: ttk.Frame,
        tcp_client: TCPClient,
        log_append: Callable[[tk.Text, str], None],
    ):
        """
        Initialize Client Tab

        Args:
            parent: Parent frame
            tcp_client: Shared TCP client instance
            log_append: Callback function to append logs to text widget
        """
        self.parent = parent
        self.tcp_client = tcp_client
        self._log_append = log_append

        self._build_ui()

        # Set log callback
        self.tcp_client.set_log_callback(self.log)

    def _build_ui(self):
        """Build the UI components"""
        top = ttk.Frame(self.parent, padding=8)
        top.pack(fill="x")
        self.var_host = tk.StringVar(value="127.0.0.1")
        self.var_port = tk.StringVar(value="9000")

        ttk.Label(top, text="호스트").pack(side="left")
        ttk.Entry(top, textvariable=self.var_host, width=16).pack(side="left", padx=4)
        ttk.Label(top, text="포트").pack(side="left")
        ttk.Entry(top, textvariable=self.var_port, width=6).pack(side="left", padx=4)
        ttk.Button(top, text="접속", command=self._connect).pack(side="left", padx=4)
        ttk.Button(top, text="해제", command=self._disconnect).pack(side="left", padx=4)

        opt = ttk.Frame(self.parent, padding=8)
        opt.pack(fill="x")
        self.var_mode = tk.StringVar(value="VAR")
        ttk.Radiobutton(
            opt, text="VAR(\\n)", variable=self.var_mode, value="VAR"
        ).pack(side="left")
        ttk.Radiobutton(
            opt, text="FIXED(32B)", variable=self.var_mode, value="FIXED"
        ).pack(side="left", padx=6)
        ttk.Radiobutton(
            opt, text="MIX(4B len+data)", variable=self.var_mode, value="MIX"
        ).pack(side="left", padx=6)

        self.var_after_close = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt, text="전송 후 종료", variable=self.var_after_close).pack(
            side="left", padx=8
        )

        msg = ttk.Frame(self.parent, padding=8)
        msg.pack(fill="x")
        self.var_msg = tk.StringVar(value="hello")
        ttk.Entry(msg, textvariable=self.var_msg, width=60).pack(side="left")
        ttk.Button(msg, text="전송", command=self._send).pack(side="left", padx=6)

        self.output = scrolledtext.ScrolledText(self.parent, height=28)
        self.output.pack(fill="both", expand=True)

    def log(self, message: str):
        """Log a message to the output area"""
        self._log_append(self.output, message)

    def set_data_callback(self, callback: Callable[[str], None]):
        """Set data callback for TCP client"""
        self.tcp_client.set_data_callback(callback)

    def _connect(self):
        """Connect to TCP server"""
        host = self.var_host.get()
        port = int(self.var_port.get())
        self.tcp_client.connect(host, port)

    def _disconnect(self):
        """Disconnect from TCP server"""
        self.tcp_client.disconnect()

    def _send(self):
        """Send message to TCP server"""
        message = self.var_msg.get()
        mode_str = self.var_mode.get()
        mode = TransmissionMode[mode_str]
        close_after = self.var_after_close.get()
        self.tcp_client.send(message, mode, close_after)
