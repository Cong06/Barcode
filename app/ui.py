"""
Main UI module for Barcode Generator.
Red & White Modern Edition layout with split resizable PanedWindow.
"""

import re
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from app.validator import validate
import re
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from app.validator import validate
from app.barcode_generator import generate_code128
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
        self.show_text_setting = True  # Default: Show text under barcode ("Có")

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

        # --- Spotlight State Variables ---
        self._spotlight_index = -1
        self._spotlight_valid_items = []
        self.lightbox_overlay = None
        self._is_closing_spotlight = False
        self._resize_timer = None

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
        header_frame.pack(fill="x", padx=16, pady=(10, 2))

        # Red & White Edition Badge
        badge = ctk.CTkFrame(header_frame, fg_color="#FEE2E2", corner_radius=6)
        badge.pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            badge,
            text="✨ RED & WHITE EDITION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#991B1B",
        ).pack(padx=8, pady=2)

        ctk.CTkLabel(
            header_frame,
            text="Barcode Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Tạo mã vạch Code 128 (Auto, A, B, C) & QR Code nét cao",
            font=ctk.CTkFont(size=11),
            text_color="#DC2626",
        ).pack(anchor="w")

        # --- Section 1: Mode Selector (Dropdown Box) ---
        mode_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        mode_frame.pack(fill="x", padx=16, pady=(4, 4))

        ctk.CTkLabel(
            mode_frame,
            text="🎯 Chọn loại mã:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(0, 2))

        self.mode_selector = ctk.CTkOptionMenu(
            mode_frame,
            values=["Code 128", "Code 128A", "Code 128B", "Code 128C", "QR Code"],
            command=self._on_mode_change,
            font=ctk.CTkFont(size=12, weight="bold"),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color="#DC2626",
            button_color="#B91C1C",
            button_hover_color="#991B1B",
            text_color="#FFFFFF",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#0F172A",
            dropdown_hover_color="#FEE2E2",
            height=32,
            corner_radius=6,
        )
        self.mode_selector.set("Code 128C")
        self.mode_selector.pack(fill="x")

        # --- Section 2: Input Textarea + Balanced Refresh Button ---
        input_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        input_frame.pack(fill="x", padx=16, pady=(4, 2))

        # Title row with Refresh button
        input_title_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_title_row.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            input_title_row,
            text="📝 Danh sách mã:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#991B1B",
        ).pack(side="left")

        # Balanced Refresh Button
        self.btn_clear = ctk.CTkButton(
            input_title_row,
            text="🔄 Refresh",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#FEF2F2",
            text_color="#DC2626",
            hover_color="#FEE2E2",
            border_color="#FCA5A5",
            border_width=1,
            width=85,
            height=24,
            corner_radius=6,
            command=self._clear_input,
        )
        self.btn_clear.pack(side="right")

        self.textbox = ctk.CTkTextbox(
            input_frame,
            height=110,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            border_width=1.5,
            border_color="#FCA5A5",
            fg_color="#FFFFFF",
            corner_radius=8,
        )
        self.textbox.pack(fill="x")

        # Helper & line counter row
        info_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        info_row.pack(fill="x", pady=(2, 0))

        self.helper_label = ctk.CTkLabel(
            info_row,
            text="Chỉ chứa số, số lượng chữ số chẵn",
            font=ctk.CTkFont(size=10),
            text_color="#DC2626",
        )
        self.helper_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            info_row,
            text="Số lượng: 0",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#991B1B",
        )
        self.count_label.pack(side="right")

        # Keypress listener for line count
        self.textbox.bind("<KeyRelease>", self._update_line_count)
        self.textbox.bind("<ButtonRelease>", self._update_line_count)

        # --- Section 3: Primary Generate Button (Bright Crimson Red) ---
        btn_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(4, 4))

        self.btn_generate = ctk.CTkButton(
            btn_frame,
            text="🚀 TẠO MÃ  (Ctrl+Enter)",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            corner_radius=8,
            command=self._trigger_generation,
        )
        self.btn_generate.pack(fill="x")

        # Separator line
        ctk.CTkFrame(self.left_pane, height=1, fg_color="#FECDD3").pack(
            fill="x", padx=16, pady=2
        )

        # --- Section 4: Display Configuration Controls (High Contrast Fonts & Text) ---
        config_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        config_frame.pack(fill="x", padx=16, pady=(2, 4))

        ctk.CTkLabel(
            config_frame,
            text="⚙️ CẤU HÌNH HIỂN THỊ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(0, 2))

        # 4A: Kích thước mã (Zoom scale)
        ctk.CTkLabel(
            config_frame,
            text="Kích thước mã:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(1, 1))

        self.size_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["75%", "100%", "130%", "160%"],
            command=self._on_size_change,
            font=ctk.CTkFont(size=10, weight="bold"),
            selected_color="#DC2626",
            selected_hover_color="#B91C1C",
            unselected_color="#F1F5F9",
            unselected_hover_color="#E2E8F0",
            text_color="#0F172A",
            height=26,
        )
        self.size_selector.set("100%")
        self.size_selector.pack(fill="x", pady=(0, 3))

        # 4B: Số cột hiển thị (Grid columns)
        ctk.CTkLabel(
            config_frame,
            text="Số mã trên 1 dòng (Số cột):",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(1, 1))

        self.cols_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["Tự động", "1 Cột", "2 Cột", "3 Cột"],
            command=self._on_cols_change,
            font=ctk.CTkFont(size=10, weight="bold"),
            selected_color="#DC2626",
            selected_hover_color="#B91C1C",
            unselected_color="#F1F5F9",
            unselected_hover_color="#E2E8F0",
            text_color="#0F172A",
            height=26,
        )
        self.cols_selector.set("Tự động")
        self.cols_selector.pack(fill="x", pady=(0, 3))

        # 4C: Màu sắc mã vạch / QR
        ctk.CTkLabel(
            config_frame,
            text="Màu sắc mã:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(1, 1))

        self.color_selector = ctk.CTkOptionMenu(
            config_frame,
            values=list(self.color_palettes.keys()),
            command=self._on_color_change,
            font=ctk.CTkFont(size=11, weight="bold"),
            dropdown_font=ctk.CTkFont(size=11),
            fg_color="#991B1B",
            button_color="#7F1D1D",
            button_hover_color="#B91C1C",
            text_color="#FFFFFF",
            height=28,
            corner_radius=6,
        )
        self.color_selector.set("Cổ điển")
        self.color_selector.pack(fill="x", pady=(0, 3))

        # 4D: Hiển thị văn bản bên dưới mã (Bắt buộc chọn 1 trong 2: Có / Không, Mặc định: Có)
        ctk.CTkLabel(
            config_frame,
            text="Hiển thị văn bản bên dưới mã:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w", pady=(1, 1))

        chk_text_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        chk_text_frame.pack(fill="x", pady=(1, 2))

        self.chk_show_text_yes = ctk.CTkCheckBox(
            chk_text_frame,
            text="Có",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#0F172A",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            checkmark_color="#FFFFFF",
            checkbox_width=16,
            checkbox_height=16,
            border_width=2,
            height=20,
            command=lambda: self._on_show_text_toggle("Có"),
        )
        self.chk_show_text_yes.pack(side="left", padx=(0, 20))

        self.chk_show_text_no = ctk.CTkCheckBox(
            chk_text_frame,
            text="Không",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#0F172A",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            checkmark_color="#FFFFFF",
            checkbox_width=16,
            checkbox_height=16,
            border_width=2,
            height=20,
            command=lambda: self._on_show_text_toggle("Không"),
        )
        self.chk_show_text_no.pack(side="left")

        # Set default state: "Có" selected, "Không" deselected
        self.chk_show_text_yes.select()
        self.chk_show_text_no.deselect()

        # --- Section 5: Footer Credit (Bottom-Left Corner) ---
        footer_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            footer_frame,
            text="Developed by HOANG VAN CONG",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(anchor="w")


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

    def _parse_entries(self, raw_text: str) -> list[str]:
        """
        Extract code entries from raw input text.
        Supports splitting by newlines, blank lines, commas (,), semicolons (;), and spaces/tabs.
        """
        if not raw_text:
            return []
        raw_tokens = re.split(r'[\n\r,;\t ]+', raw_text)
        return [token.strip() for token in raw_tokens if token.strip()]

    def _update_line_count(self, event=None):
        """Update live entry counter without triggering code generation."""
        raw_text = self.textbox.get("1.0", "end-1c")
        entries = self._parse_entries(raw_text)
        self.count_label.configure(text=f"Số lượng: {len(entries)}")

    def _on_mode_change(self, value):
        self.current_mode = value
        if value == "Code 128":
            self.helper_label.configure(text="Tất cả ký tự ASCII (chữ, số, ký tự đặc biệt)")
        elif value == "Code 128A":
            self.helper_label.configure(text="Chữ in hoa (A-Z), số, điều khiển (Không chữ thường)")
        elif value == "Code 128B":
            self.helper_label.configure(text="Chữ hoa, chữ thường (A-Z, a-z), số & ký tự in được")
        elif value == "Code 128C":
            self.helper_label.configure(text="Chỉ chứa số (0-9), số lượng chữ số chẵn")
        else:
            self.helper_label.configure(text="Chấp nhận mọi văn bản / URL (UTF-8)")

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

    def _on_show_text_toggle(self, option):
        """Toggle text visibility setting with exclusive selection between 'Có' and 'Không'."""
        if option == "Có":
            self.show_text_setting = True
            self.chk_show_text_yes.select()
            self.chk_show_text_no.deselect()
        else:
            self.show_text_setting = False
            self.chk_show_text_no.select()
            self.chk_show_text_yes.deselect()

        if self._cached_results:
            self._render_grid(self._cached_results)

    # ================================================================
    #  GENERATION LOGIC
    # ================================================================
    def _trigger_generation(self):
        """Read input textbox, validate, generate images, render grid."""
        raw_text = self.textbox.get("1.0", "end-1c")
        entries = self._parse_entries(raw_text)

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
                if self.current_mode != "QR Code":
                    img = generate_code128(
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
        self._close_spotlight()
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

        total_items = len(results)

        # Place cards with row-level centering for incomplete rows (e.g. 1 card in 3-column mode)
        for idx, item in enumerate(results):
            row_idx = idx // num_cols
            col_in_row = idx % num_cols

            # Count how many items are in this specific row
            start_idx_of_row = row_idx * num_cols
            items_in_this_row = min(num_cols, total_items - start_idx_of_row)

            # Column offset to center incomplete rows (e.g. 1 card centers in column 1 of 3)
            col_offset = (num_cols - items_in_this_row) // 2
            col = col_in_row + col_offset

            card = self._create_card(self.scroll_frame, item)
            card.grid(row=row_idx, column=col, padx=10, pady=10)



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
                if self.current_mode != "QR Code":
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
                img_pady = (14, 6) if self.show_text_setting else (14, 14)
                img_container.pack(fill="x", padx=14, pady=img_pady)

                ctk.CTkLabel(
                    img_container, image=ctk_img, text="", anchor="center"
                ).pack(anchor="center")

            # Centered Text label below barcode (optional based on show_text_setting)
            if self.show_text_setting:
                disp_text = text if len(text) <= 38 else text[:35] + "..."
                ctk.CTkLabel(
                    card,
                    text=disp_text,
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                    text_color="#991B1B",
                    anchor="center",
                ).pack(padx=14, pady=(2, 12), fill="x")

            # Bind click handler for Lightbox Spotlight modal
            self._bind_card_click(card, item)

        return card

    # ================================================================
    #  LIGHTBOX SPOTLIGHT FEATURE
    # ================================================================
    def _bind_card_click(self, widget, item):
        """Recursively bind click event and hand pointer to valid card and child widgets."""
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass
        widget.bind("<Button-1>", lambda e: self._open_spotlight(item))
        for child in widget.winfo_children():
            self._bind_card_click(child, item)

    def _open_spotlight(self, item):
        """Open the Lightbox Spotlight modal for the clicked valid item."""
        self._spotlight_valid_items = [
            it for it in self._cached_results if not it["is_error"] and it["image"] is not None
        ]
        if not self._spotlight_valid_items or item not in self._spotlight_valid_items:
            return

        self._spotlight_index = self._spotlight_valid_items.index(item)

        # Bind keyboard navigation
        self.bind("<Escape>", self._on_spotlight_esc)
        self.bind("<Left>", self._on_spotlight_left)
        self.bind("<Right>", self._on_spotlight_right)

        if self.lightbox_overlay is None or not self.lightbox_overlay.winfo_exists():
            self._build_spotlight_modal()

        self._update_spotlight_content(animated=True)

    def _build_spotlight_modal(self):
        """Build full-screen dark backdrop overlay and spotlight dialog box."""
        # Solid dark backdrop overlay covering entire app window to prevent scanner misfires
        self.lightbox_overlay = ctk.CTkFrame(
            self,
            fg_color="#0F172A",
            corner_radius=0,
        )
        self.lightbox_overlay.place(x=0, y=0, relwidth=1, relheight=1)

        # Dimmed backdrop click closes modal
        self.lightbox_overlay.bind("<Button-1>", lambda e: self._close_spotlight())

        # Determine mode-dependent initial dialog size
        if self.current_mode != "QR Code":
            init_w, init_h = 560, 480
        else:
            init_w, init_h = 480, 520

        # Spotlight Modal Container (Crisp 100% solid white card)
        self.spotlight_dialog = ctk.CTkFrame(
            self.lightbox_overlay,
            fg_color="#FFFFFF",
            corner_radius=18,
            border_width=2,
            border_color="#FCA5A5",
            width=init_w,
            height=init_h,
        )
        self.spotlight_dialog.place(relx=0.5, rely=0.56, anchor="center")
        self.spotlight_dialog.pack_propagate(False)

        # Prevent click on dialog from closing backdrop
        self.spotlight_dialog.bind("<Button-1>", lambda e: "break")

        # --- Modal Header ---
        header = ctk.CTkFrame(self.spotlight_dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(14, 6))

        badge = ctk.CTkFrame(header, fg_color="#FEE2E2", corner_radius=6)
        badge.pack(side="left")

        ctk.CTkLabel(
            badge,
            text="🔍 XEM NỔI BẬT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#991B1B",
        ).pack(padx=10, pady=3)

        self.spotlight_counter_lbl = ctk.CTkLabel(
            header,
            text="(1 / 1)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#64748B",
        )
        self.spotlight_counter_lbl.pack(side="left", padx=10)

        btn_close = ctk.CTkButton(
            header,
            text="✖ Đóng",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FEF2F2",
            text_color="#DC2626",
            hover_color="#FEE2E2",
            border_color="#FCA5A5",
            border_width=1,
            width=75,
            height=30,
            corner_radius=8,
            command=self._close_spotlight,
        )
        btn_close.pack(side="right")

        # Divider
        ctk.CTkFrame(self.spotlight_dialog, height=1, fg_color="#FECDD3").pack(
            fill="x", padx=20, pady=2
        )

        # --- Image Display Container ---
        self.spotlight_img_container = ctk.CTkFrame(
            self.spotlight_dialog,
            fg_color="#F8FAFC",
            border_color="#E2E8F0",
            border_width=1,
            corner_radius=12,
        )
        self.spotlight_img_container.pack(fill="both", expand=True, padx=20, pady=(8, 8))

        self.spotlight_img_label = ctk.CTkLabel(
            self.spotlight_img_container, text="", anchor="center"
        )
        self.spotlight_img_label.pack(expand=True, padx=10, pady=10)

        # --- Code Text & Format Label ---
        self.spotlight_text_lbl = ctk.CTkLabel(
            self.spotlight_dialog,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#991B1B",
            anchor="center",
        )
        self.spotlight_text_lbl.pack(padx=20, pady=(4, 1))

        self.spotlight_format_lbl = ctk.CTkLabel(
            self.spotlight_dialog,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#DC2626",
        )
        self.spotlight_format_lbl.pack(padx=20, pady=(0, 8))

        # --- Navigation Footer ---
        footer = ctk.CTkFrame(self.spotlight_dialog, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(4, 16))

        self.btn_spotlight_prev = ctk.CTkButton(
            footer,
            text="◀ Mã trước",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=8,
            command=self._spotlight_prev,
        )
        self.btn_spotlight_prev.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_spotlight_next = ctk.CTkButton(
            footer,
            text="Mã tiếp ▶",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=8,
            command=self._spotlight_next,
        )
        self.btn_spotlight_next.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _update_spotlight_content(self, animated=False):
        """Update modal content with high-res zoomed image and counter."""
        if not self._spotlight_valid_items or self._spotlight_index < 0:
            return

        total = len(self._spotlight_valid_items)
        item = self._spotlight_valid_items[self._spotlight_index]

        # Update counter badge
        self.spotlight_counter_lbl.configure(text=f"({self._spotlight_index + 1} / {total})")

        # High-resolution rescaled image
        img = item["image"]
        if img:
            if self.current_mode != "QR Code":
                target_w = 420
                ratio = target_w / img.width
                target_h = max(int(img.height * ratio), 90)
                display_img = img.resize((target_w, target_h), Image.NEAREST)
            else:
                target_size = 250
                display_img = img.resize((target_size, target_size), Image.NEAREST)

            ctk_img = ctk.CTkImage(
                light_image=display_img,
                dark_image=display_img,
                size=(display_img.width, display_img.height),
            )
            self._spotlight_keep_img = ctk_img
            self.spotlight_img_label.configure(image=ctk_img)

        # Update text labels
        if self.show_text_setting:
            self.spotlight_text_lbl.configure(text=item["text"])
        else:
            self.spotlight_text_lbl.configure(text="")
        self.spotlight_format_lbl.configure(text=f"Định dạng: {self.current_mode}")

        # Update button states (Disabled on boundary ends)
        if self._spotlight_index == 0:
            self.btn_spotlight_prev.configure(
                state="disabled",
                fg_color="#F1F5F9",
                text_color="#94A3B8",
            )
        else:
            self.btn_spotlight_prev.configure(
                state="normal",
                fg_color="#DC2626",
                text_color="#FFFFFF",
                hover_color="#B91C1C",
            )

        if self._spotlight_index == total - 1:
            self.btn_spotlight_next.configure(
                state="disabled",
                fg_color="#F1F5F9",
                text_color="#94A3B8",
            )
        else:
            self.btn_spotlight_next.configure(
                state="normal",
                fg_color="#DC2626",
                text_color="#FFFFFF",
                hover_color="#B91C1C",
            )

        if animated:
            self._animate_spotlight_open()

    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        """Ease-out cubic interpolation: f(t) = 1 - (1 - t)^3 for 0 <= t <= 1."""
        return 1.0 - (1.0 - max(0.0, min(1.0, t))) ** 3

    def _animate_spotlight_open(self):
        """Smooth slide-up animation using place(rely=...) — avoids CTkFrame canvas redraw artifacts.

        The dialog is already built at final size. We only animate its vertical
        position from slightly below center (rely=0.56) to center (rely=0.50).
        Tk's place geometry manager repositions the widget without triggering
        CustomTkinter's internal canvas redraw, so the rounded corners and
        border stay crisp throughout the animation.
        """
        if not hasattr(self, "spotlight_dialog") or not self.spotlight_dialog or not self.spotlight_dialog.winfo_exists():
            return

        start_rely = 0.56       # Start position: slightly below center
        end_rely = 0.50         # End position: perfectly centered
        total_frames = 15       # ~240ms at 16ms/frame ≈ 60 FPS
        frame_ms = 16

        def frame(i):
            if (
                i <= total_frames
                and hasattr(self, "spotlight_dialog")
                and self.spotlight_dialog
                and self.spotlight_dialog.winfo_exists()
            ):
                t = i / total_frames
                eased = self._ease_out_cubic(t)
                current_rely = start_rely + (end_rely - start_rely) * eased
                self.spotlight_dialog.place_configure(rely=current_rely)
                if i < total_frames:
                    self.after(frame_ms, lambda: frame(i + 1))

        frame(0)

    def _spotlight_prev(self):
        if self._spotlight_index > 0:
            self._spotlight_index -= 1
            self._update_spotlight_content(animated=False)

    def _spotlight_next(self):
        if self._spotlight_index < len(self._spotlight_valid_items) - 1:
            self._spotlight_index += 1
            self._update_spotlight_content(animated=False)

    def _on_spotlight_esc(self, event=None):
        self._close_spotlight()

    def _on_spotlight_left(self, event=None):
        self._spotlight_prev()

    def _on_spotlight_right(self, event=None):
        self._spotlight_next()

    def _close_spotlight(self):
        """Close spotlight without visual tearing.

        CTkFrame.destroy() tears because the internal canvas (which draws
        rounded corners) is cleaned up before the raw tkinter frame disappears,
        causing a 1-2 frame flash of a square widget. Fix: hide everything
        from view first with place_forget(), then destroy in the next event
        loop tick where it's already invisible.
        """
        self.unbind("<Escape>")
        self.unbind("<Left>")
        self.unbind("<Right>")

        if hasattr(self, "lightbox_overlay") and self.lightbox_overlay and self.lightbox_overlay.winfo_exists():
            overlay = self.lightbox_overlay
            self.lightbox_overlay = None

            # Hide from view instantly — no visual artifacts possible
            overlay.place_forget()

            # Destroy in the next tick when it's already invisible
            self.after(1, overlay.destroy)

    # ================================================================
    #  RESIZE LISTENER
    # ================================================================
    def _on_window_configure(self, event=None):
        """Auto re-layout grid on window resize if column count changes (debounced)."""
        if event and event.widget != self:
            return

        if self.grid_cols_setting == "Tự động" and self._cached_results:
            if getattr(self, "_resize_timer", None) is not None:
                try:
                    self.after_cancel(self._resize_timer)
                except Exception:
                    pass

            def do_resize():
                self._resize_timer = None
                new_cols = self._get_column_count()
                if getattr(self, "_last_cols", None) != new_cols:
                    self._render_grid(self._cached_results)

            self._resize_timer = self.after(50, do_resize)
