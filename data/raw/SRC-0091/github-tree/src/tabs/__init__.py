"""
Tab modules for Smart Network Service Application
"""

from .diag_tab import DiagTab
from .server_tab import ServerTab
from .client_tab import ClientTab
from .buffer_tab import BufferTab
from .draw_tab import DrawTab
from .sfc_tab import SFCTab

__all__ = [
    "DiagTab",
    "ServerTab",
    "ClientTab",
    "BufferTab",
    "DrawTab",
    "SFCTab",
]
