#!/usr/bin/env python3
"""
Smart Network Service AD Project - Main Application
스마트네트워크서비스 AD 프로젝트 메인 애플리케이션
"""

import tkinter as tk
from tkinter import ttk

from src.components import TCPServer, TCPClient

from src.tabs import DiagTab, ServerTab, ClientTab, BufferTab, DrawTab, SFCTab


class SmartNetworkApp(tk.Tk):
  """Smart Network Service Application"""

  def __init__(self):
    super().__init__()
    self.title("스마트 네트워크 서비스 — AD 프로젝트")
    self.geometry("1100x720")

    self.tcp_server = TCPServer()
    self.tcp_client = TCPClient()

    nb = ttk.Notebook(self)
    nb.pack(fill="both", expand=True)

    pg_diag = ttk.Frame(nb)
    pg_server = ttk.Frame(nb)
    pg_client = ttk.Frame(nb)
    pg_buf = ttk.Frame(nb)
    pg_draw = ttk.Frame(nb)
    pg_sfc = ttk.Frame(nb)

    nb.add(pg_diag, text="네트워크 진단")
    nb.add(pg_server, text="TCP 서버")
    nb.add(pg_client, text="TCP 클라이언트")
    nb.add(pg_buf, text="버퍼/소켓")
    nb.add(pg_draw, text="네트워크 그림판")
    nb.add(pg_sfc, text="Ryu SFC")

    self.diag_tab = DiagTab(pg_diag, self._log_append)
    self.server_tab = ServerTab(pg_server, self.tcp_server, self._log_append)
    self.client_tab = ClientTab(pg_client, self.tcp_client, self._log_append)
    self.buffer_tab = BufferTab(pg_buf, self.tcp_client, self._log_append)
    self.draw_tab = DrawTab(pg_draw, self.tcp_server, self.tcp_client, self.after)
    self.sfc_tab = SFCTab(pg_sfc, self._log_append)

    self.client_tab.set_data_callback(self.draw_tab.handle_network_data)

  def _log_append(self, widget: tk.Text, text: str):
    widget.insert("end", text + "\n")
    widget.see("end")


def main():
    """Main entry point"""
    app = SmartNetworkApp()
    app.mainloop()


if __name__ == "__main__":
    main()
