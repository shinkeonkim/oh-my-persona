"""
Network Drawing Board Tab
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Callable

from src.components import TCPServer, TCPClient


class DrawTab:
    """Network Drawing Board Tab"""

    def __init__(
        self,
        parent: ttk.Frame,
        tcp_server: TCPServer,
        tcp_client: TCPClient,
        after_callback: Callable,
    ):
        """
        Initialize Draw Tab

        Args:
            parent: Parent frame
            tcp_server: Shared TCP server instance
            tcp_client: Shared TCP client instance
            after_callback: Callback for scheduling tasks on main thread
        """
        self.parent = parent
        self.tcp_server = tcp_server
        self.tcp_client = tcp_client
        self.after_callback = after_callback

        self._last_xy = None
        self._drawing_from_network = False
        self._is_eraser_mode = False

        self._build_ui()

    def _build_ui(self):
        """Build the UI components"""
        info = ttk.Frame(self.parent, padding=8)
        info.pack(fill="x")
        ttk.Label(
            info, text="그림판 — 드래그로 선 그리기 (네트워크 브로드캐스트 지원)"
        ).pack(side="left")

        # Broadcast control
        self.var_broadcast = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            info, text="브로드캐스트", variable=self.var_broadcast
        ).pack(side="left", padx=10)

        ttk.Button(info, text="Clear", command=self._clear_canvas).pack(
            side="left", padx=4
        )

        # Tool mode selection frame
        tool_mode = ttk.Frame(self.parent, padding=8)
        tool_mode.pack(fill="x")

        ttk.Label(tool_mode, text="도구:").pack(side="left", padx=(0, 5))
        self.var_tool_mode = tk.StringVar(value="pen")
        ttk.Radiobutton(
            tool_mode, text="펜", variable=self.var_tool_mode, value="pen",
            command=self._on_tool_change
        ).pack(side="left", padx=2)
        ttk.Radiobutton(
            tool_mode, text="지우개", variable=self.var_tool_mode, value="eraser",
            command=self._on_tool_change
        ).pack(side="left", padx=2)

        # Drawing tools frame
        tools = ttk.Frame(self.parent, padding=8)
        tools.pack(fill="x")

        # Color selection
        ttk.Label(tools, text="색상:").pack(side="left", padx=(0, 5))
        self.var_color = tk.StringVar(value="#000000")

        # Preset colors with hex codes
        colors = [
            ("black", "#000000"),
            ("red", "#FF0000"),
            ("blue", "#0000FF"),
            ("green", "#00FF00"),
            ("yellow", "#FFFF00"),
            ("orange", "#FFA500"),
            ("purple", "#800080"),
        ]

        for name, hex_code in colors:
            frame = tk.Frame(tools)
            frame.pack(side="left", padx=2)

            # Color button using Canvas (works better on macOS)
            canvas_btn = tk.Canvas(
                frame,
                width=30,
                height=30,
                highlightthickness=1,
                highlightbackground="gray",
                cursor="hand2",
            )
            canvas_btn.pack()
            canvas_btn.create_rectangle(0, 0, 30, 30, fill=hex_code, outline="")
            canvas_btn.bind(
                "<Button-1>", lambda e, c=hex_code: self._select_color(c)
            )

            # Hex code label
            lbl = ttk.Label(frame, text=hex_code[1:], font=("Courier", 7))
            lbl.pack()

        # Custom color input
        ttk.Label(tools, text="커스텀:").pack(side="left", padx=(10, 2))
        self.entry_custom_color = ttk.Entry(tools, width=8, font=("Courier", 10))
        self.entry_custom_color.pack(side="left", padx=2)
        self.entry_custom_color.insert(0, "#000000")
        self.entry_custom_color.bind(
            "<Return>", lambda e: self._select_color(self.entry_custom_color.get())
        )

        ttk.Button(
            tools,
            text="적용",
            command=lambda: self._select_color(self.entry_custom_color.get()),
            width=4,
        ).pack(side="left", padx=2)

        # Color picker button
        ttk.Button(
            tools, text="선택", command=self._pick_color, width=4
        ).pack(side="left", padx=2)

        # Current color indicator
        self.current_color_display = tk.Label(
            tools,
            text="  현재  ",
            bg="#000000",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="solid",
            borderwidth=2,
        )
        self.current_color_display.pack(side="left", padx=(5, 0))

        # Width selection with slider
        ttk.Label(tools, text="두께:").pack(side="left", padx=(15, 5))
        self.var_pen_width = tk.IntVar(value=2)
        self.var_eraser_width = tk.IntVar(value=10)
        self.var_width = self.var_pen_width  # Default to pen width
        self.width_label = ttk.Label(tools, text="2", font=("Arial", 10, "bold"))
        self.width_label.pack(side="left", padx=(0, 5))
        self.width_slider = ttk.Scale(
            tools,
            from_=1,
            to=50,
            variable=self.var_width,
            orient="horizontal",
            length=120,
            command=self._on_width_change,
        )
        self.width_slider.pack(side="left", padx=2)

        self.canvas = tk.Canvas(self.parent, bg="white", height=480)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_move)

    def _on_tool_change(self):
        """Handle tool mode change between pen and eraser"""
        mode = self.var_tool_mode.get()
        self._is_eraser_mode = (mode == "eraser")

        if self._is_eraser_mode:
            # Switch to eraser mode
            self.var_width = self.var_eraser_width
            self.width_slider.config(variable=self.var_eraser_width)
            self.width_label.config(text=str(self.var_eraser_width.get()))
            # Disable color selection in eraser mode
            self.current_color_display.config(
                bg="white",
                fg="gray",
                text=" 지우개 "
            )
        else:
            # Switch to pen mode
            self.var_width = self.var_pen_width
            self.width_slider.config(variable=self.var_pen_width)
            self.width_label.config(text=str(self.var_pen_width.get()))
            # Re-enable color display
            color = self.var_color.get()
            self.current_color_display.config(bg=color, text="  현재  ")
            # Update text color based on brightness
            r, g, b = (
                int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16),
            )
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = "black" if brightness > 128 else "white"
            self.current_color_display.config(fg=text_color)

    def _on_width_change(self, value):
        """Handle width slider change"""
        width = int(float(value))
        self.width_label.config(text=str(width))
        if self._is_eraser_mode:
            self.var_eraser_width.set(width)
        else:
            self.var_pen_width.set(width)

    def _select_color(self, color: str):
        """Select a color and update the display"""
        # Validate hex color format
        if not color.startswith("#"):
            color = "#" + color

        # Basic validation
        if len(color) == 7:
            try:
                # Try to parse as hex
                int(color[1:], 16)
                self.var_color.set(color)
                self.current_color_display.config(bg=color)
                self.entry_custom_color.delete(0, tk.END)
                self.entry_custom_color.insert(0, color)

                # Set text color based on brightness
                r, g, b = (
                    int(color[1:3], 16),
                    int(color[3:5], 16),
                    int(color[5:7], 16),
                )
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                text_color = "black" if brightness > 128 else "white"
                self.current_color_display.config(fg=text_color)
            except ValueError:
                messagebox.showerror("색상 오류", f"올바른 색상 코드가 아닙니다: {color}")
        else:
            messagebox.showerror(
                "색상 오류", "색상 코드는 #RRGGBB 형식이어야 합니다 (예: #FF0000)"
            )

    def _pick_color(self):
        """Open color picker dialog"""
        current_color = self.var_color.get()
        color_result = colorchooser.askcolor(
            initialcolor=current_color, title="색상 선택"
        )

        if color_result[1]:
            self._select_color(color_result[1])

    def _on_press(self, event):
        """Handle mouse button press"""
        self._last_xy = (event.x, event.y)

    def _on_move(self, event):
        """Handle mouse move while drawing"""
        if not self._last_xy:
            return
        x1, y1 = self._last_xy
        x2, y2 = event.x, event.y

        if self._is_eraser_mode:
            color = "white"
            width = self.var_eraser_width.get()
        else:
            color = self.var_color.get()
            width = self.var_pen_width.get()

        # Draw locally with smooth rounded lines
        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            width=width,
            fill=color,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
        )

        # Send to server to broadcast
        if self.var_broadcast.get():
            draw_data = f"DRAW:{x1},{y1},{x2},{y2},{width},{color}\n"

            # Send via TCP server if running
            if self.tcp_server.running:
                self.tcp_server.broadcast(draw_data)
            # Send via TCP client if connected
            elif self.tcp_client.connected and self.tcp_client.socket:
                try:
                    self.tcp_client.socket.send(draw_data.encode("utf-8"))
                except:
                    pass

        self._last_xy = (x2, y2)

    def _clear_canvas(self):
        """Clear the canvas"""
        self.canvas.delete("all")

        # Broadcast clear command if enabled
        if self.var_broadcast.get():
            clear_data = "CLEAR:\n"

            # Send via TCP server if running
            if self.tcp_server.running:
                self.tcp_server.broadcast(clear_data)

            # Send via TCP client if connected
            elif self.tcp_client.connected and self.tcp_client.socket:
                try:
                    self.tcp_client.socket.send(clear_data.encode("utf-8"))
                except:
                    pass

    def handle_network_data(self, data: str):
        """Handle received drawing data from network"""
        try:
            for line in data.strip().split("\n"):
                if line.startswith("DRAW:"):
                    # Parse: DRAW:x1,y1,x2,y2,width,color
                    parts = line[5:].split(",")
                    if len(parts) >= 4:
                        x1, y1, x2, y2 = map(float, parts[:4])
                        width = int(parts[4]) if len(parts) > 4 else 2
                        color = parts[5] if len(parts) > 5 else "blue"

                        self.after_callback(
                            0,
                            lambda x1=x1, y1=y1, x2=x2, y2=y2, w=width, c=color: self.canvas.create_line(
                                x1,
                                y1,
                                x2,
                                y2,
                                width=w,
                                fill=c,
                                capstyle=tk.ROUND,
                                joinstyle=tk.ROUND,
                                smooth=True,
                            ),
                        )
                elif line.startswith("CLEAR:"):
                    # Clear canvas
                    self.after_callback(0, lambda: self.canvas.delete("all"))
        except Exception as e:
            pass  # Silently ignore parsing errors
