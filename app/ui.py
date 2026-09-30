"""
Main UI module for Barcode Generator.
Split-pane layout with resizable input/control panel on the left and barcode grid on the right.
"""

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from app.validator import validate
from app.barcode_generator import generate_code128c
from app.qr_generator import generate_qrcode


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Barcode Generator - Code 128C & QR Code")
        self.geometry("1280x820")
        self.minsize(800, 550)
        ctk.set_appearance_mode("light")

        # --- State Variables ---
        self.current_mode = "Code 128C"
        self.scale_factor = 1.0
        self.grid_cols_setting = "Tự động"
        self.color_palette_name = "Cổ điển"

        self.color_palettes = {
            "Cổ điển": {"fg": "#000000", "bg": "#FFFFFF"},
            "Navy": {"fg": "#1E3A8A", "bg": "#FFFFFF"},
            "Đỏ Đô": {"fg": "#991B1B", "bg": "#FFFFFF"},
            "Xanh Lá": {"fg": "#065F46", "bg": "#FFFFFF"},
            "Tím": {"fg": "#581C87", "bg": "#FFFFFF"},
        }

        self._last_entries = []
        self._cached_results = []
        self._card_images = []

        # --- Build UI Layout ---
        self._build_main_layout()

        # Keyboard shortcuts
        self.bind("<Control-Return>", lambda e: self._trigger_generation())
        self.bind("<Control-KP_Enter>", lambda e: self._trigger_generation())

        # Window resize event for grid layout
        self.bind("<Configure>", self._on_window_configure)

    # ================================================================
    #  LAYOUT CONSTRUCTION
    # ================================================================
    def _build_main_layout(self):
        """Create split PanedWindow layout (Left Pane = Input & Controls, Right Pane = Grid)."""
        # PanedWindow splitter allows dragging sash to resize left vs right side
        self.paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg="#CBD5E1",
            bd=0,
            sashrelief="flat",
        )
        self.paned.pack(fill="both", expand=True)

        # Left Pane (Control & Input Panel)
        self.left_pane = ctk.CTkFrame(self.paned, fg_color="#F8FAFC", corner_radius=0)
        self.paned.add(self.left_pane, minsize=320, width=400)

        # Right Pane (Result Grid Panel)
        self.right_pane = ctk.CTkFrame(self.paned, fg_color="#FFFFFF", corner_radius=0)
        self.paned.add(self.right_pane, minsize=450)

        # Populate left & right panes
        self._build_left_pane()
        self._build_right_pane()

    # ================================================================
    #  LEFT PANE (INPUT & CONTROLS)
    # ================================================================
    def _build_left_pane(self):
        # Header title
        header_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            header_frame,
            text="Barcode Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0F172A",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Tạo mã vạch Code 128C & QR Code",
            font=ctk.CTkFont(size=12),
            text_color="#64748B",
        ).pack(anchor="w")

        # --- Section 1: Mode Selector ---
        mode_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        mode_frame.pack(fill="x", padx=16, pady=(8, 8))

        ctk.CTkLabel(
            mode_frame,
            text="Loại mã:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#334155",
        ).pack(anchor="w", pady=(0, 4))

        self.mode_selector = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Code 128C", "QR Code"],
            command=self._on_mode_change,
            font=ctk.CTkFont(size=12, weight="bold"),
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
        )
        self.mode_selector.set("Code 128C")
        self.mode_selector.pack(fill="x")

        # --- Section 2: Input Textarea ---
        input_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        input_frame.pack(fill="x", padx=16, pady=(8, 4))

        ctk.CTkLabel(
            input_frame,
            text="Nhập danh sách mã (mỗi mã 1 dòng):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#334155",
        ).pack(anchor="w", pady=(0, 4))

        self.textbox = ctk.CTkTextbox(
            input_frame,
            height=160,
            font=ctk.CTkFont(family="Consolas", size=13),
            border_width=1,
            border_color="#CBD5E1",
            fg_color="#FFFFFF",
        )
        self.textbox.pack(fill="x")

        # Helper & count label row
        info_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        info_row.pack(fill="x", pady=(4, 0))

        self.helper_label = ctk.CTkLabel(
            info_row,
            text="Chỉ chứa số, số lượng chữ số chẵn",
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
        )
        self.helper_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            info_row,
            text="Số lượng: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#475569",
        )
        self.count_label.pack(side="right")

        # Keypress listener only updates line count (no auto-generate)
        self.textbox.bind("<KeyRelease>", self._update_line_count)
        self.textbox.bind("<ButtonRelease>", self._update_line_count)

        # --- Section 3: Generate Button ---
        btn_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(8, 12))

        self.btn_generate = ctk.CTkButton(
            btn_frame,
            text="🚀 Tạo Mã  (Ctrl+Enter)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            corner_radius=8,
            command=self._trigger_generation,
        )
        self.btn_generate.pack(fill="x")

        # Separator line
        ctk.CTkFrame(self.left_pane, height=1, fg_color="#E2E8F0").pack(
            fill="x", padx=16, pady=4
        )

        # --- Section 4: Display Configuration Controls ---
        config_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        config_frame.pack(fill="x", padx=16, pady=(8, 12))

        ctk.CTkLabel(
            config_frame,
            text="⚙️ CẤU HÌNH HIỂN THỊ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#475569",
        ).pack(anchor="w", pady=(0, 8))

        # 4A: Kích thước mã (Zoom scale)
        ctk.CTkLabel(
            config_frame,
            text="Kích thước mã:",
            font=ctk.CTkFont(size=12),
            text_color="#334155",
        ).pack(anchor="w", pady=(4, 2))

        self.size_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["75%", "100%", "130%", "160%"],
            command=self._on_size_change,
            font=ctk.CTkFont(size=11),
        )
        self.size_selector.set("100%")
        self.size_selector.pack(fill="x", pady=(0, 8))

        # 4B: Số cột hiển thị (Grid columns)
        ctk.CTkLabel(
            config_frame,
            text="Số mã trên 1 dòng (Số cột):",
            font=ctk.CTkFont(size=12),
            text_color="#334155",
        ).pack(anchor="w", pady=(4, 2))

        self.cols_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["Tự động", "1 Cột", "2 Cột", "3 Cột"],
            command=self._on_cols_change,
            font=ctk.CTkFont(size=11),
        )
        self.cols_selector.set("Tự động")
        self.cols_selector.pack(fill="x", pady=(0, 8))

        # 4C: Màu sắc mã vạch / QR
        ctk.CTkLabel(
            config_frame,
            text="Màu sắc mã:",
            font=ctk.CTkFont(size=12),
            text_color="#334155",
        ).pack(anchor="w", pady=(4, 2))

        self.color_selector = ctk.CTkOptionMenu(
            config_frame,
            values=list(self.color_palettes.keys()),
            command=self._on_color_change,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color="#0F172A",
            button_color="#1E293B",
            button_hover_color="#334155",
        )
        self.color_selector.set("Cổ điển")
        self.color_selector.pack(fill="x", pady=(0, 8))

    # ================================================================
    #  RIGHT PANE (RESULT GRID)
    # ================================================================
    def _build_right_pane(self):
        # Stats bar container
        stats_container = ctk.CTkFrame(self.right_pane, fg_color="#F8FAFC", height=40)
        stats_container.pack(fill="x", side="top", padx=12, pady=(12, 0))

        self.stats_label = ctk.CTkLabel(
            stats_container,
            text="Nhập dữ liệu và nhấn 'Tạo Mã' để bắt đầu",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#475569",
        )
        self.stats_label.pack(side="left", padx=12, pady=6)

        # Empty State frame
        self.empty_frame = ctk.CTkFrame(self.right_pane, fg_color="transparent")
        self.empty_frame.pack(fill="both", expand=True, pady=80)

        ctk.CTkLabel(
            self.empty_frame,
            text="📋",
            font=ctk.CTkFont(size=48),
        ).pack()

        ctk.CTkLabel(
            self.empty_frame,
            text="Chưa có mã nào được tạo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#64748B",
        ).pack(pady=(8, 4))

        ctk.CTkLabel(
            self.empty_frame,
            text="Dán danh sách mã vào ô bên trái và bấm nút 'Tạo Mã'",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8",
        ).pack()

        # Scrollable grid frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.right_pane,
            fg_color="transparent",
        )
        # Hidden by default until data is rendered

    # ================================================================
    #  EVENT HANDLERS & CONTROL CALLBACKS
    # ================================================================
    def _update_line_count(self, event=None):
        """Update live line counter without triggering code generation."""
        raw_text = self.textbox.get("1.0", "end-1c")
        lines = [line for line in raw_text.split("\n") if line.strip()]
        self.count_label.configure(text=f"Số lượng: {len(lines)}")

    def _on_mode_change(self, value):
        self.current_mode = value
        if value == "Code 128C":
            self.helper_label.configure(text="Chỉ chứa số, số lượng chữ số chẵn")
        else:
            self.helper_label.configure(text="Chấp nhận mọi văn bản / URL")

        # If data was already generated, re-trigger code generation for new mode
        if self._last_entries:
            self._trigger_generation()

    def _on_size_change(self, value):
        scale_map = {"75%": 0.75, "100%": 1.0, "130%": 1.3, "160%": 1.6}
        self.scale_factor = scale_map.get(value, 1.0)

        # Re-render grid using cached results
        if self._cached_results:
            self._render_grid(self._cached_results)

    def _on_cols_change(self, value):
        self.grid_cols_setting = value

        # Re-render grid using cached results
        if self._cached_results:
            self._render_grid(self._cached_results)

    def _on_color_change(self, value):
        self.color_palette_name = value

        # Color changes require re-generating image pixels
        if self._last_entries:
            self._trigger_generation()

    # ================================================================
    #  GENERATION LOGIC
    # ================================================================
    def _trigger_generation(self):
        """Read input textbox, validate, generate images, render grid."""
        raw_text = self.textbox.get("1.0", "end-1c")

        # Extract non-empty lines
        lines = raw_text.split("\n")
        entries = [line.strip() for line in lines if line.strip()]

        self._last_entries = entries
        self.count_label.configure(text=f"Số lượng: {len(entries)}")

        if not entries:
            self._show_empty_state()
            return

        # Get color palette
        palette = self.color_palettes.get(
            self.color_palette_name, {"fg": "#000000", "bg": "#FFFFFF"}
        )
        fg_color = palette["fg"]
        bg_color = palette["bg"]

        results = []
        valid_count = 0
        error_count = 0

        for original_text in entries:
            is_valid, error_msg = validate(original_text, self.current_mode)

            if is_valid:
                # Generate barcode or QR code with selected colors
                if self.current_mode == "Code 128C":
                    img = generate_code128c(
                        original_text, fg_color=fg_color, bg_color=bg_color
                    )
                else:
                    img = generate_qrcode(
                        original_text, fill_color=fg_color, back_color=bg_color
                    )

                if img is not None:
                    valid_count += 1
                    results.append({
                        "text": original_text,
                        "image": img,
                        "is_error": False,
                        "error_msg": error_msg,
                    })
                else:
                    error_count += 1
                    results.append({
                        "text": original_text,
                        "image": None,
                        "is_error": True,
                        "error_msg": "Lỗi tạo hình ảnh. Vui lòng thử lại.",
                    })
            else:
                error_count += 1
                results.append({
                    "text": original_text,
                    "image": None,
                    "is_error": True,
                    "error_msg": error_msg,
                })

        self._cached_results = results
        self._update_stats(len(results), valid_count, error_count)
        self._render_grid(results)

    def _show_empty_state(self):
        self.stats_label.configure(text="Nhập dữ liệu và nhấn 'Tạo Mã' để bắt đầu")
        self.scroll_frame.pack_forget()
        self.empty_frame.pack(fill="both", expand=True, pady=80)
        self._cached_results.clear()

    def _update_stats(self, total, valid, errors):
        parts = [f"Chế độ: {self.current_mode}", f"Tổng: {total} mã", f"✓ {valid} hợp lệ"]
        if errors > 0:
            parts.append(f"⚠ {errors} lỗi")
        self.stats_label.configure(text="   |   ".join(parts))

    # ================================================================
    #  GRID RENDERING & CARD CREATION
    # ================================================================
    def _render_grid(self, results):
        """Render all barcode/QR cards into grid."""
        self.empty_frame.pack_forget()
        self.scroll_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Clear old widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._card_images.clear()

        # Determine column count
        num_cols = self._get_column_count()
        self._last_cols = num_cols

        # Place cards in grid
        for idx, item in enumerate(results):
            row = idx // num_cols
            col = idx % num_cols

            card = self._create_card(self.scroll_frame, item)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="n")

        # Expand columns evenly
        for c in range(num_cols):
            self.scroll_frame.grid_columnconfigure(c, weight=1)

    def _get_column_count(self):
        """Get column count based on setting or right pane width."""
        if self.grid_cols_setting == "1 Cột":
            return 1
        elif self.grid_cols_setting == "2 Cột":
            return 2
        elif self.grid_cols_setting == "3 Cột":
            return 3
        else:
            # Auto responsive mode based on right pane width
            width = self.right_pane.winfo_width()
            if width >= 900:
                return 3
            elif width >= 600:
                return 2
            else:
                return 1

    def _create_card(self, parent, item):
        """Create an individual card widget."""
        text = item["text"]
        image = item["image"]
        is_error = item["is_error"]
        error_msg = item["error_msg"]

        # Base card width adjusted by scale factor
        card_width = int(300 * self.scale_factor)

        if is_error:
            card = ctk.CTkFrame(
                parent,
                corner_radius=10,
                border_width=1,
                border_color="#F59E0B",
                fg_color="#FEF3C7",
                width=card_width,
            )

            ctk.CTkLabel(
                card,
                text="⚠ Không hợp lệ",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#B45309",
            ).pack(padx=14, pady=(10, 2), anchor="w")

            ctk.CTkLabel(
                card,
                text=text,
                font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                text_color="#1F2937",
            ).pack(padx=14, pady=2)

            ctk.CTkLabel(
                card,
                text=error_msg,
                font=ctk.CTkFont(size=11),
                text_color="#92400E",
                wraplength=max(card_width - 30, 150),
                justify="left",
            ).pack(padx=14, pady=(0, 10), anchor="w")

        else:
            card = ctk.CTkFrame(
                parent,
                corner_radius=10,
                border_width=1,
                border_color="#E2E8F0",
                fg_color="#FFFFFF",
                width=card_width,
            )

            if image is not None:
                # Calculate scaled image dimensions
                if self.current_mode == "Code 128C":
                    target_w = max(int(260 * self.scale_factor), 140)
                    ratio = target_w / image.width
                    target_h = max(int(image.height * ratio), 50)
                    display_img = image.resize((target_w, target_h), Image.NEAREST)
                else:
                    target_size = max(int(190 * self.scale_factor), 100)
                    display_img = image.resize((target_size, target_size), Image.NEAREST)

                ctk_img = ctk.CTkImage(
                    light_image=display_img,
                    dark_image=display_img,
                    size=(display_img.width, display_img.height),
                )
                self._card_images.append(ctk_img)

                # Render barcode/QR image
                ctk.CTkLabel(card, image=ctk_img, text="").pack(
                    padx=14, pady=(12, 4)
                )

            # Text label below barcode
            disp_text = text if len(text) <= 38 else text[:35] + "..."
            ctk.CTkLabel(
                card,
                text=disp_text,
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                text_color="#1E293B",
            ).pack(padx=14, pady=(2, 8))

        return card

    # ================================================================
    #  RESIZE LISTENER
    # ================================================================
    def _on_window_configure(self, event=None):
        """Auto re-layout grid on window resize if column count changes."""
        # ONLY handle main window configure events, ignore child widget configure events
        if event and event.widget != self:
            return

        if self.grid_cols_setting == "Tự động" and self._cached_results:
            new_cols = self._get_column_count()
            if getattr(self, "_last_cols", None) != new_cols:
                self._render_grid(self._cached_results)

