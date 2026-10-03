"""
Main UI module for Barcode Generator.
Red & White Modern Edition layout with split resizable PanedWindow.
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
        self.title("Barcode Generator - Red & White Edition")
        self.geometry("1280x840")
        self.minsize(820, 580)
        ctk.set_appearance_mode("light")

        # --- State Variables ---
        self.current_mode = "Code 128C"
        self.scale_factor = 1.0
        self.grid_cols_setting = "Tự động"
        self.color_palette_name = "Cổ điển"

        # Color Palettes
        self.color_palettes = {
            "Cổ điển": {"fg": "#000000", "bg": "#FFFFFF"},
            "Đỏ Rực Rỡ": {"fg": "#DC2626", "bg": "#FFFFFF"},
            "Navy Đậm": {"fg": "#1E3A8A", "bg": "#FFFFFF"},
            "Xanh Emerald": {"fg": "#047857", "bg": "#FFFFFF"},
            "Tím Violet": {"fg": "#6D28D9", "bg": "#FFFFFF"},
        }

        self._last_entries = []
        self._cached_results = []
        self._card_images = []
        self._last_cols = None

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
        self.paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg="#FECDD3",  # Soft Red Sash Divider
            bd=0,
            sashrelief="flat",
        )
        self.paned.pack(fill="both", expand=True)

        # Left Pane (Control & Input Panel - Crisp White)
        self.left_pane = ctk.CTkFrame(self.paned, fg_color="#FFFFFF", corner_radius=0)
        self.paned.add(self.left_pane, minsize=330, width=420)

        # Right Pane (Result Grid Panel - Soft Warm White Background)
        self.right_pane = ctk.CTkFrame(self.paned, fg_color="#FFF1F2", corner_radius=0)
        self.paned.add(self.right_pane, minsize=460)

        # Populate left & right panes
        self._build_left_pane()
        self._build_right_pane()

    # ================================================================
    #  LEFT PANE (RED & WHITE MODERN STYLE)
    # ================================================================
    def _build_left_pane(self):
        # --- Header Section ---
        header_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        header_frame.pack(fill="x", padx=18, pady=(16, 6))

        # Red & White Edition Badge
        badge = ctk.CTkFrame(header_frame, fg_color="#FEE2E2", corner_radius=6)
        badge.pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            badge,
            text="✨ RED & WHITE EDITION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#991B1B",
        ).pack(padx=8, pady=2)

        ctk.CTkLabel(
            header_frame,
            text="Barcode Generator",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Tạo mã vạch Code 128C & QR Code nét cao",
            font=ctk.CTkFont(size=12),
            text_color="#DC2626",
        ).pack(anchor="w")

        # --- Section 1: Mode Selector ---
        mode_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        mode_frame.pack(fill="x", padx=18, pady=(10, 6))

        ctk.CTkLabel(
            mode_frame,
            text="🎯 Chọn loại mã:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(0, 4))

        self.mode_selector = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Code 128C", "QR Code"],
            command=self._on_mode_change,
            font=ctk.CTkFont(size=12, weight="bold"),
            selected_color="#DC2626",
            selected_hover_color="#B91C1C",
            unselected_color="#F1F5F9",
            unselected_hover_color="#E2E8F0",
            text_color="#0F172A",
        )
        self.mode_selector.set("Code 128C")
        self.mode_selector.pack(fill="x")

        # --- Section 2: Input Textarea + Balanced Refresh Button ---
        input_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        input_frame.pack(fill="x", padx=18, pady=(8, 4))

        # Title row with Refresh button
        input_title_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_title_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            input_title_row,
            text="📝 Danh sách mã (1 mã / dòng):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#991B1B",
        ).pack(side="left")

        # Balanced Refresh Button
        self.btn_clear = ctk.CTkButton(
            input_title_row,
            text="🔄 Refresh",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#FEF2F2",
            text_color="#DC2626",
            hover_color="#FEE2E2",
            border_color="#FCA5A5",
            border_width=1,
            width=95,
            height=28,
            corner_radius=6,
            command=self._clear_input,
        )
        self.btn_clear.pack(side="right")

        self.textbox = ctk.CTkTextbox(
            input_frame,
            height=150,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            border_width=1.5,
            border_color="#FCA5A5",
            fg_color="#FFFFFF",
            corner_radius=8,
        )
        self.textbox.pack(fill="x")

        # Helper & line counter row
        info_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        info_row.pack(fill="x", pady=(4, 0))

        self.helper_label = ctk.CTkLabel(
            info_row,
            text="Chỉ chứa số, số lượng chữ số chẵn",
            font=ctk.CTkFont(size=11),
            text_color="#DC2626",
        )
        self.helper_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            info_row,
            text="Số lượng: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        )
        self.count_label.pack(side="right")

        # Keypress listener for line count
        self.textbox.bind("<KeyRelease>", self._update_line_count)
        self.textbox.bind("<ButtonRelease>", self._update_line_count)

        # --- Section 3: Primary Generate Button (Bright Crimson Red) ---
        btn_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        btn_frame.pack(fill="x", padx=18, pady=(8, 10))

        self.btn_generate = ctk.CTkButton(
            btn_frame,
            text="🚀 TẠO MÃ  (Ctrl+Enter)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            corner_radius=10,
            command=self._trigger_generation,
        )
        self.btn_generate.pack(fill="x")

        # Separator line
        ctk.CTkFrame(self.left_pane, height=1.5, fg_color="#FECDD3").pack(
            fill="x", padx=18, pady=4
        )

        # --- Section 4: Display Configuration Controls (High Contrast Fonts & Text) ---
        config_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        config_frame.pack(fill="x", padx=18, pady=(6, 12))

        ctk.CTkLabel(
            config_frame,
            text="⚙️ CẤU HÌNH HIỂN THỊ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(0, 6))

        # 4A: Kích thước mã (Zoom scale) - High Contrast Unselected Text
        ctk.CTkLabel(
            config_frame,
            text="Kích thước mã:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(2, 2))

        self.size_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["75%", "100%", "130%", "160%"],
            command=self._on_size_change,
            font=ctk.CTkFont(size=11, weight="bold"),
            selected_color="#DC2626",
            selected_hover_color="#B91C1C",
            unselected_color="#F1F5F9",
            unselected_hover_color="#E2E8F0",
            text_color="#0F172A",
        )
        self.size_selector.set("100%")
        self.size_selector.pack(fill="x", pady=(0, 8))

        # 4B: Số cột hiển thị (Grid columns) - High Contrast Unselected Text
        ctk.CTkLabel(
            config_frame,
            text="Số mã trên 1 dòng (Số cột):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(2, 2))

        self.cols_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["Tự động", "1 Cột", "2 Cột", "3 Cột"],
            command=self._on_cols_change,
            font=ctk.CTkFont(size=11, weight="bold"),
            selected_color="#DC2626",
            selected_hover_color="#B91C1C",
            unselected_color="#F1F5F9",
            unselected_hover_color="#E2E8F0",
            text_color="#0F172A",
        )
        self.cols_selector.set("Tự động")
        self.cols_selector.pack(fill="x", pady=(0, 8))

        # 4C: Màu sắc mã vạch / QR
        ctk.CTkLabel(
            config_frame,
            text="Màu sắc mã:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(2, 2))

        self.color_selector = ctk.CTkOptionMenu(
            config_frame,
            values=list(self.color_palettes.keys()),
            command=self._on_color_change,
            font=ctk.CTkFont(size=12, weight="bold"),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color="#991B1B",
            button_color="#7F1D1D",
            button_hover_color="#B91C1C",
            text_color="#FFFFFF",
        )
        self.color_selector.set("Cổ điển")
        self.color_selector.pack(fill="x", pady=(0, 8))

    # ================================================================
    #  RIGHT PANE (RESULT GRID - RED & WHITE STYLE)
    # ================================================================
    def _build_right_pane(self):
        # Stats bar container with clean red accent border
        stats_container = ctk.CTkFrame(
            self.right_pane, fg_color="#FFFFFF", corner_radius=10, border_width=1.5, border_color="#FECDD3"
        )
        stats_container.pack(fill="x", side="top", padx=14, pady=(14, 4))

        self.stats_label = ctk.CTkLabel(
            stats_container,
            text="✨ Nhập dữ liệu và nhấn 'Tạo Mã' để bắt đầu",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#991B1B",
        )
        self.stats_label.pack(side="left", padx=14, pady=8)

        # Empty State frame
        self.empty_frame = ctk.CTkFrame(self.right_pane, fg_color="transparent")
        self.empty_frame.pack(fill="both", expand=True, pady=100)

        ctk.CTkLabel(
            self.empty_frame,
            text="🎨",
            font=ctk.CTkFont(size=56),
        ).pack()

        ctk.CTkLabel(
            self.empty_frame,
            text="Chưa Có Mã Nào Được Tạo",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#991B1B",
        ).pack(pady=(10, 4))

        ctk.CTkLabel(
            self.empty_frame,
            text="Dán danh sách mã vào khung bên trái và nhấn nút '🚀 TẠO MÃ'",
            font=ctk.CTkFont(size=13),
            text_color="#DC2626",
        ).pack()

        # Scrollable grid frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.right_pane,
            fg_color="transparent",
        )

    # ================================================================
    #  EVENT HANDLERS & CONTROL CALLBACKS
    # ================================================================
    def _clear_input(self):
        """Clear textbox, reset count, and restore empty state."""
        self.textbox.delete("1.0", "end")
        self._last_entries.clear()
        self._update_line_count()
        self._show_empty_state()

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

        if self._last_entries:
            self._trigger_generation()

    def _on_size_change(self, value):
        scale_map = {"75%": 0.75, "100%": 1.0, "130%": 1.3, "160%": 1.6}
        self.scale_factor = scale_map.get(value, 1.0)

        if self._cached_results:
            self._render_grid(self._cached_results)

    def _on_cols_change(self, value):
        self.grid_cols_setting = value

        if self._cached_results:
            self._render_grid(self._cached_results)

    def _on_color_change(self, value):
        self.color_palette_name = value

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
        self.stats_label.configure(text="✨ Nhập dữ liệu và nhấn 'Tạo Mã' để bắt đầu")
        self.scroll_frame.pack_forget()
        self.empty_frame.pack(fill="both", expand=True, pady=100)
        self._cached_results.clear()

    def _update_stats(self, total, valid, errors):
        parts = [f"Chế độ: {self.current_mode}", f"Tổng: {total} mã", f"✓ {valid} hợp lệ"]
        if errors > 0:
            parts.append(f"⚠ {errors} lỗi")
        self.stats_label.configure(text="   |   ".join(parts))

    # ================================================================
    #  GRID RENDERING & PERFECT CENTER CARD CREATION
    # ================================================================
    def _render_grid(self, results):
        """Render all barcode/QR cards into grid with perfect centering."""
        self.empty_frame.pack_forget()
        self.scroll_frame.pack(fill="both", expand=True, padx=12, pady=10)

        # Clear old widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._card_images.clear()

        # Determine column count
        num_cols = self._get_column_count()
        self._last_cols = num_cols

        # Configure column weights: set weight=1 for active columns, weight=0 for unused columns
        for c in range(6):
            if c < num_cols:
                self.scroll_frame.grid_columnconfigure(c, weight=1)
            else:
                self.scroll_frame.grid_columnconfigure(c, weight=0)

        # Place cards centered in grid cells
        for idx, item in enumerate(results):
            row = idx // num_cols
            col = idx % num_cols

            card = self._create_card(self.scroll_frame, item)
            # Center card in grid cell without stretch
            card.grid(row=row, column=col, padx=10, pady=10)


    def _get_column_count(self):
        """Get column count based on setting or right pane width."""
        if self.grid_cols_setting == "1 Cột":
            return 1
        elif self.grid_cols_setting == "2 Cột":
            return 2
        elif self.grid_cols_setting == "3 Cột":
            return 3
        else:
            width = self.right_pane.winfo_width()
            if width >= 920:
                return 3
            elif width >= 620:
                return 2
            else:
                return 1

    def _create_card(self, parent, item):
        """Create an individual card widget with 100% PERFECT CENTER alignment."""
        text = item["text"]
        image = item["image"]
        is_error = item["is_error"]
        error_msg = item["error_msg"]

        # Base card width adjusted by scale factor
        card_width = int(310 * self.scale_factor)

        if is_error:
            card = ctk.CTkFrame(
                parent,
                corner_radius=12,
                border_width=1.5,
                border_color="#F59E0B",
                fg_color="#FEF3C7",
                width=card_width,
            )

            ctk.CTkLabel(
                card,
                text="⚠ Không hợp lệ",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#B45309",
                anchor="center",
            ).pack(padx=14, pady=(12, 2), fill="x")

            ctk.CTkLabel(
                card,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#1F2937",
                anchor="center",
            ).pack(padx=14, pady=2, fill="x")

            ctk.CTkLabel(
                card,
                text=error_msg,
                font=ctk.CTkFont(size=11),
                text_color="#92400E",
                wraplength=max(card_width - 30, 160),
                justify="center",
                anchor="center",
            ).pack(padx=14, pady=(0, 12), fill="x")

        else:
            card = ctk.CTkFrame(
                parent,
                corner_radius=12,
                border_width=1.5,
                border_color="#FCA5A5",
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

                # Render barcode/QR image inside transparent centered container
                img_container = ctk.CTkFrame(card, fg_color="transparent")
                img_container.pack(fill="x", padx=14, pady=(14, 6))

                ctk.CTkLabel(
                    img_container, image=ctk_img, text="", anchor="center"
                ).pack(anchor="center")

            # Centered Text label below barcode
            disp_text = text if len(text) <= 38 else text[:35] + "..."
            ctk.CTkLabel(
                card,
                text=disp_text,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#991B1B",
                anchor="center",
            ).pack(padx=14, pady=(2, 12), fill="x")

        return card

    # ================================================================
    #  RESIZE LISTENER
    # ================================================================
    def _on_window_configure(self, event=None):
        """Auto re-layout grid on window resize if column count changes."""
        if event and event.widget != self:
            return

        if self.grid_cols_setting == "Tự động" and self._cached_results:
            new_cols = self._get_column_count()
            if getattr(self, "_last_cols", None) != new_cols:
                self._render_grid(self._cached_results)
