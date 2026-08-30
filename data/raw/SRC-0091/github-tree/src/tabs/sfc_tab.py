"""
Ryu SFC Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Callable, Optional

from src.components import RyuClient


class SFCTab:
    """Ryu Service Function Chain Tab"""

    def __init__(
        self, parent: ttk.Frame, log_append: Callable[[tk.Text, str], None]
    ):
        """
        Initialize SFC Tab

        Args:
            parent: Parent frame
            log_append: Callback function to append logs to text widget
        """
        self.parent = parent
        self._log_append = log_append
        self.ryu_client: Optional[RyuClient] = None

        self._build_ui()

    def _build_ui(self):
        """Build the UI components"""
        top = ttk.Frame(self.parent, padding=8)
        top.pack(fill="x")

        self.var_host = tk.StringVar(value="127.0.0.1")
        self.var_port = tk.StringVar(value="8080")
        self.var_dpid = tk.StringVar(value="1")
        self.var_priority = tk.StringVar(value="100")

        self.var_h1 = tk.StringVar(value="1")
        self.var_fw = tk.StringVar(value="2")
        self.var_nat = tk.StringVar(value="3")
        self.var_h2 = tk.StringVar(value="4")

        ttk.Label(top, text="Ryu").grid(row=0, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.var_host, width=14).grid(row=0, column=1)
        ttk.Label(top, text=":").grid(row=0, column=2)
        ttk.Entry(top, textvariable=self.var_port, width=6).grid(
            row=0, column=3, padx=4
        )
        ttk.Label(top, text="DPID").grid(row=0, column=4, sticky="e")
        ttk.Entry(top, textvariable=self.var_dpid, width=6).grid(row=0, column=5)
        ttk.Label(top, text="prio").grid(row=0, column=6, sticky="e")
        ttk.Entry(top, textvariable=self.var_priority, width=6).grid(
            row=0, column=7
        )

        ports = ttk.Frame(self.parent, padding=8)
        ports.pack(fill="x")
        for i, (lab, var) in enumerate(
            [
                ("h1", self.var_h1),
                ("fw", self.var_fw),
                ("nat", self.var_nat),
                ("h2", self.var_h2),
            ]
        ):
            ttk.Label(ports, text=lab).grid(row=0, column=i * 2)
            ttk.Entry(ports, textvariable=var, width=6).grid(
                row=0, column=i * 2 + 1, padx=4
            )

        btns = ttk.Frame(self.parent, padding=8)
        btns.pack(fill="x")
        ttk.Button(btns, text="SFC 설치", command=self._install_sfc).pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="바이패스", command=self._install_bypass).pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="플로우 조회", command=self._dump_flows).pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="플로우 삭제", command=self._clear_flows).pack(
            side="left", padx=4
        )

        self.output = scrolledtext.ScrolledText(self.parent, height=24)
        self.output.pack(fill="both", expand=True, padx=8, pady=8)

    def log(self, message: str):
        """Log a message to the output area"""
        self._log_append(self.output, message)

    def _get_ryu_client(self) -> RyuClient:
        """Get or create RyuClient instance"""
        host = self.var_host.get()
        port = int(self.var_port.get())
        if (
            self.ryu_client is None
            or self.ryu_client.host != host
            or self.ryu_client.port != port
        ):
            self.ryu_client = RyuClient(host, port)
            self.ryu_client.set_log_callback(self.log)
        return self.ryu_client

    def _install_sfc(self):
        """Install Service Function Chain"""

        def task():
            client = self._get_ryu_client()
            dpid = int(self.var_dpid.get())
            priority = int(self.var_priority.get())
            h1 = int(self.var_h1.get())
            fw = int(self.var_fw.get())
            nat = int(self.var_nat.get())
            h2 = int(self.var_h2.get())
            client.install_sfc(dpid, priority, h1, fw, nat, h2)

        threading.Thread(target=task, daemon=True).start()

    def _install_bypass(self):
        """Install bypass flows"""

        def task():
            client = self._get_ryu_client()
            dpid = int(self.var_dpid.get())
            priority = int(self.var_priority.get())
            h1 = int(self.var_h1.get())
            h2 = int(self.var_h2.get())
            client.install_bypass(dpid, priority, h1, h2)

        threading.Thread(target=task, daemon=True).start()

    def _dump_flows(self):
        """Dump all flows for a datapath"""

        def task():
            client = self._get_ryu_client()
            dpid = int(self.var_dpid.get())
            flows = client.dump_flows(dpid)
            if flows:
                self.log(f"\n=== Flows for DPID {dpid} ===")
                for flow in flows:
                    self.log(f"Priority: {flow.get('priority', 'N/A')}")
                    self.log(f"  Match: {flow.get('match', {})}")
                    self.log(f"  Actions: {flow.get('actions', [])}")
                    self.log("")

        threading.Thread(target=task, daemon=True).start()

    def _clear_flows(self):
        """Clear all flows for a datapath"""

        def task():
            client = self._get_ryu_client()
            dpid = int(self.var_dpid.get())
            client.clear_flows(dpid)

        threading.Thread(target=task, daemon=True).start()
