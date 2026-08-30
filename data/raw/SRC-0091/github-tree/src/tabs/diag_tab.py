"""
Network Diagnostics Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Callable

from src.utils import (
    get_ip_config,
    get_netstat_filtered,
    check_port_open,
    demo_byte_order,
    demo_inet_pton_ipv4,
    demo_inet_pton_ipv6,
    dns_lookup,
    reverse_dns_lookup,
)


class DiagTab:
    """Network Diagnostics Tab"""

    def __init__(self, parent: ttk.Frame, log_append: Callable[[tk.Text, str], None]):
        """
        Initialize Diagnostics Tab

        Args:
            parent: Parent frame
            log_append: Callback function to append logs to text widget
        """
        self.parent = parent
        self._log_append = log_append

        self._build_ui()

    def _build_ui(self):
        """Build the UI components"""
        left = ttk.Frame(self.parent, padding=8)
        left.pack(side="left", fill="y")
        right = ttk.Frame(self.parent, padding=8)
        right.pack(side="right", fill="both", expand=True)

        # IP Configuration
        ttk.Label(left, text="IP 구성 / netstat / 포트 검사").pack(anchor="w")
        ttk.Button(left, text="IP 구성 확인", command=self._do_ipconfig).pack(
            fill="x", pady=2
        )

        # Netstat
        self.var_netstat = tk.StringVar(value="9000")
        row = ttk.Frame(left)
        row.pack(fill="x", pady=2)
        ttk.Entry(row, textvariable=self.var_netstat, width=10).pack(side="left")
        ttk.Button(row, text="netstat 필터", command=self._do_netstat).pack(
            side="left", padx=4
        )

        # Port check
        row2 = ttk.Frame(left)
        row2.pack(fill="x", pady=(6, 2))
        self.var_host = tk.StringVar(value="127.0.0.1")
        self.var_port = tk.StringVar(value="9000")
        ttk.Entry(row2, textvariable=self.var_host, width=14).pack(side="left")
        ttk.Entry(row2, textvariable=self.var_port, width=6).pack(side="left", padx=4)
        ttk.Button(row2, text="포트 오픈 검사", command=self._do_check_port).pack(
            side="left", padx=4
        )

        ttk.Separator(left).pack(fill="x", pady=8)

        # Byte order / Address conversion
        ttk.Label(left, text="바이트/주소 변환").pack(anchor="w")
        ttk.Button(left, text="hton/ntoh 데모", command=self._do_hton).pack(
            fill="x", pady=2
        )

        self.var_ipv4 = tk.StringVar(value="8.8.8.8")
        self.var_ipv6 = tk.StringVar(value="2001:4860:4860::8888")

        row3 = ttk.Frame(left)
        row3.pack(fill="x", pady=2)
        ttk.Entry(row3, textvariable=self.var_ipv4, width=18).pack(side="left")
        ttk.Button(row3, text="inet_pton/ntop(IPv4)", command=self._do_inet4).pack(
            side="left", padx=4
        )

        row4 = ttk.Frame(left)
        row4.pack(fill="x", pady=2)
        ttk.Entry(row4, textvariable=self.var_ipv6, width=26).pack(side="left")
        ttk.Button(row4, text="inet_pton/ntop(IPv6)", command=self._do_inet6).pack(
            side="left", padx=4
        )

        ttk.Separator(left).pack(fill="x", pady=8)

        # DNS
        ttk.Label(left, text="DNS/이름 변환").pack(anchor="w")
        self.var_dns = tk.StringVar(value="example.com")
        self.var_rev = tk.StringVar(value="8.8.8.8")

        row5 = ttk.Frame(left)
        row5.pack(fill="x", pady=2)
        ttk.Entry(row5, textvariable=self.var_dns, width=18).pack(side="left")
        ttk.Button(row5, text="DNS 조회", command=self._do_dns).pack(
            side="left", padx=4
        )

        row6 = ttk.Frame(left)
        row6.pack(fill="x", pady=2)
        ttk.Entry(row6, textvariable=self.var_rev, width=18).pack(side="left")
        ttk.Button(row6, text="역방향 조회", command=self._do_reverse).pack(
            side="left", padx=4
        )

        # Output area
        self.output = scrolledtext.ScrolledText(right, height=30)
        self.output.pack(fill="both", expand=True)

    def log(self, message: str):
        """Log a message to the output area"""
        self._log_append(self.output, message)

    def _do_ipconfig(self):
        def task():
            result = get_ip_config()
            self.log(result)

        threading.Thread(target=task, daemon=True).start()

    def _do_netstat(self):
        def task():
            port = self.var_netstat.get()
            result = get_netstat_filtered(port)
            self.log(f"=== netstat filtered by {port} ===")
            self.log(result)

        threading.Thread(target=task, daemon=True).start()

    def _do_check_port(self):
        def task():
            host = self.var_host.get()
            port = int(self.var_port.get())
            is_open, message = check_port_open(host, port)
            self.log(message)

        threading.Thread(target=task, daemon=True).start()

    def _do_hton(self):
        result = demo_byte_order()
        self.log("=== Byte Order Demo ===")
        self.log(result)

    def _do_inet4(self):
        addr = self.var_ipv4.get()
        result = demo_inet_pton_ipv4(addr)
        self.log("=== IPv4 Conversion ===")
        self.log(result)

    def _do_inet6(self):
        addr = self.var_ipv6.get()
        result = demo_inet_pton_ipv6(addr)
        self.log("=== IPv6 Conversion ===")
        self.log(result)

    def _do_dns(self):
        def task():
            hostname = self.var_dns.get()
            result = dns_lookup(hostname)
            self.log(result)

        threading.Thread(target=task, daemon=True).start()

    def _do_reverse(self):
        def task():
            ip = self.var_rev.get()
            result = reverse_dns_lookup(ip)
            self.log(result)

        threading.Thread(target=task, daemon=True).start()
