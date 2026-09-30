# Barcode Generator — Application Specification

> **Version**: 1.0 (MVP)
> **Last Updated**: 2026-09-30
> **Platform**: Windows Desktop
> **Language**: Python 3.x
> **Supported Code Types**: Code 128C, QR Code

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Supported Code Types](#3-supported-code-types)
4. [UX Goals](#4-ux-goals)
5. [UI Layout](#5-ui-layout)
6. [Header](#6-header)
7. [Mode Selector](#7-mode-selector)
8. [Input Area](#8-input-area)
9. [Auto-Generation](#9-auto-generation)
10. [Code 128C Validation](#10-code-128c-validation)
11. [Code 128C Encoding Accuracy](#11-code-128c-encoding-accuracy)
12. [QR Code Validation](#12-qr-code-validation)
13. [QR Code Encoding](#13-qr-code-encoding)
14. [Result Area — Code Grid](#14-result-area--code-grid)
15. [Code Card](#15-code-card)
16. [Code Sizing](#16-code-sizing)
17. [Scrolling](#17-scrolling)
18. [Statistics](#18-statistics)
19. [Error Card Handling](#19-error-card-handling)
20. [Empty State](#20-empty-state)
21. [Duplicate Handling](#21-duplicate-handling)
22. [Display Order](#22-display-order)
23. [Clipboard & Keyboard](#23-clipboard--keyboard)
24. [Performance](#24-performance)
25. [Visual Design](#25-visual-design)
26. [Responsive Window](#26-responsive-window)
27. [Project Structure](#27-project-structure)
28. [Module Responsibilities](#28-module-responsibilities)
29. [Mandatory Test Cases](#29-mandatory-test-cases)
30. [Error Handling Policy](#30-error-handling-policy)
31. [Data Persistence](#31-data-persistence)
32. [Features Explicitly Excluded](#32-features-explicitly-excluded)
33. [Build & Packaging](#33-build--packaging)
34. [README Requirements](#34-readme-requirements)
35. [Dependencies](#35-dependencies)
36. [Priority Order](#36-priority-order)
37. [Development Phases](#37-development-phases)
38. [Expected User Experience](#38-expected-user-experience)
39. [Completion Criteria](#39-completion-criteria)

---

## 1. Overview

**Barcode Generator** is a lightweight, offline Windows desktop application built with Python.

It supports two code types:
- **Code 128C** — standard linear barcode for numeric data
- **QR Code** — 2D matrix code for any text/URL data

**Core Workflow:**

```
CHỌN LOẠI MÃ → NHẬP DỮ LIỆU → TỰ ĐỘNG TẠO MÃ → HIỂN THỊ DƯỚI DẠNG GRID → ĐỐI CHIẾU NHANH
```

The user selects a code type, pastes a list of data into a text box, and the app instantly generates codes and displays them in a scrollable grid. Each card shows both the code image and the original input beneath it, enabling rapid visual comparison.

> **IMPORTANT**: This is a **utility app**, not a management system. Simplicity and accuracy are paramount.
> Future versions may add more code types (e.g., Code 39, EAN-13, DataMatrix), but v1.0 focuses exclusively on **Code 128C** and **QR Code**.

---

## 2. Technology Stack

| Component | Technology |
|:---|:---|
| Language | **Python 3.x** |
| GUI Framework | **CustomTkinter** |
| Barcode Generation (128C) | **python-barcode** |
| QR Code Generation | **qrcode** |
| Image Processing | **Pillow (PIL)** |
| Packaging | **PyInstaller** |

### Hard Constraints

- ✅ Runs **100% offline**
- ❌ No database
- ❌ No API / Web server / Internet
- ❌ No login / authentication / cloud
- ❌ No web framework

---

## 3. Supported Code Types

| Code Type | Library | Input Type | Use Case |
|:---|:---|:---|:---|
| **Code 128C** | `python-barcode` | Numeric only (even-length digits) | Product codes, serial numbers, inventory IDs |
| **QR Code** | `qrcode` | Any text (UTF-8) | URLs, text, Wi-Fi credentials, serial numbers |

### Future Expansion (NOT in v1.0)

The following code types may be added in future versions:
- Code 39
- EAN-13 / EAN-8
- UPC-A
- DataMatrix
- PDF417

The architecture should be designed so that adding new code types is straightforward (e.g., a new generator class + validator function), but v1.0 **only** implements Code 128C and QR Code.

---

## 4. UX Goals

The user experience must be **dead simple**:

1. Open the app.
2. Choose code type (128C or QR).
3. Paste a list of data.
4. Codes appear automatically.
5. Read code image + original text to compare.

### UX Principles

| Priority | Principle |
|:---|:---|
| 1 | Easy to use — minimal clicks |
| 2 | Fast — instant feedback |
| 3 | Accurate — standards-compliant encoding |
| 4 | Easy to read — clear visual comparison |
| 5 | Minimal interaction — no unnecessary configuration |
| 6 | No confusion — impossible to mix up codes |

### Explicitly Avoided

- ❌ Complex menus
- ❌ Sidebars
- ❌ Dashboards
- ❌ Settings panels
- ❌ Excessive configuration parameters

---

## 5. UI Layout

The interface is a single-window, vertically stacked layout:

```
┌─────────────────────────────────────────────────────────────┐
│                   BARCODE GENERATOR                         │
│       Generate and compare Code 128C & QR Code              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Loại mã:  [ Code 128C ]  [ QR Code ]                       │
│                                                             │
│  Nhập danh sách mã                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 64630096561958                                        │  │
│  │ 64630096561959                                        │  │
│  │ 64630096561960                                        │  │
│  │ 64630096561961                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│  Mỗi dòng là một mã                         Số lượng: 4    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                         KẾT QUẢ                             │
│         10 mã  |  ✓ 8 hợp lệ  |  ⚠ 2 lỗi                  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   BARCODE    │  │   BARCODE    │  │   BARCODE    │      │
│  │              │  │              │  │              │      │
│  │64630096561958│  │64630096561959│  │64630096561960│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐                                           │
│  │   BARCODE    │                                           │
│  │              │                                           │
│  │64630096561961│                                           │
│  └──────────────┘                                           │
│                                              ▼ scrollbar    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Header

- **Title**: `Barcode Generator`
- **Subtitle** (small text): `Generate and compare Code 128C & QR Code`
- No complex logo required
- Standard window controls: Minimize, Maximize, Close
- Default window size: **1200 × 800 px**
- Window is **resizable**

---

## 7. Mode Selector

Above the input area, provide a **simple mode selector** to switch between code types:

```
Loại mã:  [ Code 128C ]  [ QR Code ]
```

### Implementation

- Use a **segmented button** or **tab control** (CustomTkinter `CTkSegmentedButton` or `CTkTabview`)
- **Default mode**: Code 128C
- Switching modes:
  - Clears the result grid
  - Keeps the input text (does not erase the TextBox)
  - Re-validates and re-generates all codes using the new mode
  - Updates the helper text if needed

### Mode-Specific Behavior

| Mode | Input Rules | Helper Text |
|:---|:---|:---|
| Code 128C | Numeric only, even-length | `Mỗi dòng là một mã (chỉ chứa số, số lượng chữ số chẵn)` |
| QR Code | Any text (UTF-8) | `Mỗi dòng là một mã (chấp nhận mọi ký tự)` |

### Design Rules

- The mode selector must be **visually prominent** but not overwhelming
- Must be clearly labeled
- Switching must feel **instant** (no loading screen)

---

## 8. Input Area

### Layout

- **Label**: `Nhập danh sách mã`
- **Multi-line TextBox** below the label
- **Helper text**: Changes based on selected mode (see [Section 7](#7-mode-selector))
- **Count display**: `Số lượng: N` (updates live)

### Placeholder Examples

**Code 128C mode:**
```
64630096561958
64630096561959
64630096561960
```

**QR Code mode:**
```
https://example.com
Hello World 123
WiFi:SSID=MyNetwork
```

### Keyboard Support

The TextBox must natively support:

| Shortcut | Action |
|:---|:---|
| `Ctrl + V` | Paste |
| `Ctrl + C` | Copy |
| `Ctrl + A` | Select All |
| `Backspace` / `Delete` | Delete characters |

### Data Integrity Rule

> **CAUTION**: The app **MUST NEVER** automatically modify user input. Specifically:
>
> - ❌ Do NOT strip leading zeros (`001234` must remain `001234`, never `1234`)
> - ❌ Do NOT add digits or characters
> - ❌ Do NOT remove digits or characters
> - ❌ Do NOT insert spaces
> - ❌ Do NOT insert dashes or hyphens
> - ❌ Do NOT reformat the code in any way
> - ❌ Do NOT trim whitespace from QR Code input lines (spaces may be intentional)

---

## 9. Auto-Generation

When the user types or pastes data into the TextBox:

1. Detect content change.
2. Read each line.
3. Strip trailing empty lines.
4. Determine current mode (Code 128C or QR Code).
5. Validate each code according to the current mode's rules.
6. Valid → generate code image using the appropriate generator.
7. Invalid → show error state on card.
8. Update the grid immediately.

### No Button Required

The user should **never** need to press a "Generate" button. Generation is automatic.

### Debounce

If real-time generation causes lag with many lines, apply a **200–300ms debounce** after the user stops typing before triggering generation. This balances responsiveness with performance.

---

## 10. Code 128C Validation

> **IMPORTANT**: This is a **critical section** of the specification.

### Rules for a Valid Code 128C Input

| Rule | Description |
|:---|:---|
| Digits only | Must contain only characters `0-9` |
| Even length | Total number of digits must be **even** |
| Leading zeros OK | `001234` is valid and must be preserved |

### Valid Examples

| Input | Status | Reason |
|:---|:---|:---|
| `64630096561958` | ✅ Valid | 14 digits (even), all numeric |
| `001234` | ✅ Valid | 6 digits (even), leading zeros preserved |
| `123456` | ✅ Valid | 6 digits (even) |
| `9876543210` | ✅ Valid | 10 digits (even) |

### Invalid Examples

| Input | Status | Error Message |
|:---|:---|:---|
| `12345` | ❌ Invalid | `Không hợp lệ: Code 128C yêu cầu số lượng chữ số chẵn.` |
| `123A45` | ❌ Invalid | `Không hợp lệ: Chỉ được chứa chữ số 0-9.` |
| `12-3456` | ❌ Invalid | `Không hợp lệ: Chỉ được chứa chữ số 0-9.` |
| `12 3456` | ❌ Invalid | `Không hợp lệ: Chỉ được chứa chữ số 0-9.` |
| `ABC123` | ❌ Invalid | `Không hợp lệ: Chỉ được chứa chữ số 0-9.` |

### Validation Must Not Crash

If a code is invalid:
- Do **not** generate a barcode for it.
- Show an error card (see [Section 19](#19-error-card-handling)).
- Continue processing all other codes normally.

---

## 11. Code 128C Encoding Accuracy

Beyond input validation, the barcode **encoding** itself must be correct.

### Requirements

- Must use the **Code 128 Subtype C** encoding (not Auto, not Subtype A, not Subtype B).
- The `python-barcode` library must be configured to use the correct Code 128C class/module.
- The generated barcode must contain:
  - ✅ Correct **Start Code C** character
  - ✅ Data encoded as **digit pairs** (00–99)
  - ✅ Correct **checksum** (Modulo 103)
  - ✅ Correct **Stop code**

### Implementation Guidance

- Use the proven `python-barcode` library — do **not** write a custom barcode encoder.
- If the library doesn't natively distinguish 128C from 128 Auto, additional configuration or subclassing may be needed to force Subtype C encoding.

---

## 12. QR Code Validation

QR Code mode has **much more lenient** validation compared to Code 128C.

### Rules for a Valid QR Code Input

| Rule | Description |
|:---|:---|
| Non-empty | The line must contain at least 1 character |
| Any characters | Letters, numbers, symbols, spaces, Unicode — all accepted |
| Max length | Recommended limit: **4296 characters** (alphanumeric) or **7089 digits** per QR spec. Lines exceeding this should show a warning. |

### Valid Examples

| Input | Status | Reason |
|:---|:---|:---|
| `https://example.com` | ✅ Valid | URL text |
| `Hello World 123` | ✅ Valid | Plain text with spaces |
| `001234` | ✅ Valid | Numeric (any length OK for QR) |
| `WiFi:T:WPA;S:MyNetwork;P:password;;` | ✅ Valid | Wi-Fi QR format |
| `Đây là tiếng Việt` | ✅ Valid | Unicode text |

### Invalid Examples

| Input | Status | Error Message |
|:---|:---|:---|
| *(empty line)* | ❌ Skipped | Empty lines are silently ignored |
| *(string > 4296 chars)* | ⚠ Warning | `Cảnh báo: Dữ liệu quá dài, mã QR có thể không quét được.` |

---

## 13. QR Code Encoding

### Requirements

- Use the **`qrcode`** Python library (ISO/IEC 18004 compliant)
- The generated QR Code must:
  - ✅ Encode the **exact input text** without modification
  - ✅ Use appropriate **error correction level** (default: `M` — 15% recovery)
  - ✅ Auto-select the optimal **QR version** (size) based on data length
  - ✅ Produce a clear, high-contrast black-on-white image

### Error Correction Levels

| Level | Recovery Capacity | Use Case |
|:---|:---|:---|
| L | ~7% | Maximum data capacity |
| **M** (default) | **~15%** | **Good balance of size and reliability** |
| Q | ~25% | Higher reliability |
| H | ~30% | Maximum reliability, largest QR |

For v1.0, use **Level M** as the fixed default. No user configuration needed.

### Implementation Guidance

- Use the `qrcode` library with `qrcode.make()` or `qrcode.QRCode()` class.
- Output as a `Pillow.Image` object for consistent rendering with the barcode cards.
- Set `box_size` and `border` appropriately for clear on-screen display.

---

## 14. Result Area — Code Grid

### Section Header

- Title: `KẾT QUẢ`
- Statistics line below (see [Section 18](#18-statistics))

### Grid Layout

- **Default**: 3 columns on a standard desktop screen
- Cards arranged left-to-right, top-to-bottom
- Grid must **not** cut off codes

**Code 128C mode:**
```
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   BARCODE     │ │   BARCODE     │ │   BARCODE     │
│               │ │               │ │               │
│ 646300...958  │ │ 646300...959  │ │ 646300...960  │
└───────────────┘ └───────────────┘ └───────────────┘
```

**QR Code mode:**
```
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   ██ █ ██     │ │   █ ██ ██     │ │   ██ ██ █     │
│   █ ██ █      │ │   ██ █ █      │ │   █ █ ██      │
│   ██ █ ██     │ │   █ ██ ██     │ │   ██ ██ █     │
│               │ │               │ │               │
│ example.com   │ │ Hello World   │ │ WiFi:SSID=... │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Responsive Columns

| Window Width | Columns |
|:---|:---|
| ≥ 1200 px | 3 |
| ≥ 900 px | 2 |
| < 900 px | 1 |

---

## 15. Code Card

Each code is displayed inside an individual **card** widget.

### Card Contents — Code 128C

```
┌──────────────────────────┐
│                          │
│      █ ███ █ ███ █       │
│      █ █ ███ █ ██        │
│      ███ █ ███ ███       │
│                          │
│      64630096561958      │
└──────────────────────────┘
```

### Card Contents — QR Code

```
┌──────────────────────────┐
│                          │
│      ██ █ ██ █ ██        │
│      █ ██ █ ██ █         │
│      ██ █ ██ █ ██        │
│      █ ██ █ ██ █         │
│      ██ █ ██ █ ██        │
│                          │
│   https://example.com    │
└──────────────────────────┘
```

### Card Elements

1. **Code image** (barcode or QR) — centered, with adequate padding
2. **Original input text** — displayed below the code image

### Text Display Rules

- Show the **full, unmodified** original input
- **No** added spaces or formatting
- Easy-to-read font
- **Centered** alignment
- **High contrast** (dark text on light background, or vice versa)
- For very long QR Code input text, **truncate with ellipsis** in the card display (e.g., `https://very-long-url.com/path/to/pa...`) but the full text is used for QR generation

### Purpose

The card layout enables the user to visually compare:

```
CODE IMAGE ↔ ORIGINAL INPUT
```

quickly and without ambiguity.

---

## 16. Code Sizing

### Code 128C (Linear Barcode)

- Barcode images must be **large enough** to:
  - Read clearly on screen
  - Not appear distorted
  - Be scannable if needed
- **Maintain correct aspect ratio** — never stretch or squish
- Adequate **quiet zone** (white space) around the barcode
- Text must **never** overlap the barcode bars

### QR Code (2D Matrix)

- QR Code images should be **square** (1:1 aspect ratio)
- Minimum display size: **150 × 150 px** on screen
- Must have a **quiet zone** (white border) of at least 4 modules
- Must be sharp and crisp — no anti-aliasing blur on the modules

---

## 17. Scrolling

When many codes are entered (e.g., 100+):

- The result area **must** have a **vertical scrollbar**
- The window must **not** grow infinitely tall
- The input area **stays fixed** at the top
- **Only the result grid scrolls**

```
┌─────────────────────────┐
│  [MODE + INPUT - Fixed] │
├─────────────────────────┤
│  [RESULT GRID]          │
│  [code][code][code]     │  ← scrollable
│  [code][code][code]     │
│  ...                    │
│               ▼ scroll  │
└─────────────────────────┘
```

---

## 18. Statistics

Display a live statistics summary in the result area header:

### Format

```
Code 128C  |  10 mã  |  ✓ 8 hợp lệ  |  ⚠ 2 lỗi
```

or for QR mode:

```
QR Code  |  10 mã  |  ✓ 10 hợp lệ
```

### Rules

- Updates automatically when input changes
- Shows the **current mode** name
- When all codes are valid, omit the error count or show `⚠ 0 lỗi`
- When no codes are entered, show nothing or show `0 mã`

---

## 19. Error Card Handling

When a code is invalid (only applicable in Code 128C mode — QR mode accepts almost anything):

- Still display a card for it in the grid (maintaining input order)
- The card must be **visually distinct** (e.g., different background color, warning icon)
- Show the **original invalid input**
- Show a **clear error message** explaining why

### Example Error Card (Code 128C mode)

```
┌──────────────────────────┐
│   ⚠ Không hợp lệ        │
│                          │
│   12345                  │
│                          │
│   Code 128C yêu cầu     │
│   số lượng chữ số chẵn. │
└──────────────────────────┘
```

### Example Warning Card (QR mode — data too long)

```
┌──────────────────────────┐
│   ⚠ Cảnh báo             │
│                          │
│   [QR CODE IMAGE]        │
│                          │
│   Dữ liệu quá dài,      │
│   mã QR có thể không    │
│   quét được.             │
└──────────────────────────┘
```

### Error Card Design

- Visually distinct but **not overwhelming**
- Subtle warning color (e.g., soft amber/yellow border or background)
- Does not break the grid layout

---

## 20. Empty State

### No Input Yet

When the TextBox is empty:

- Do **not** show error messages
- Show a friendly message in the result area:
  > `Nhập mã ở phía trên để bắt đầu`

### All Input Cleared

When the user deletes all text:

- Result area must **clear automatically**
- Return to the empty state message

---

## 21. Duplicate Handling

> **WARNING**: Do **NOT** auto-remove duplicates.

If the user enters:

```
64630096561958
64630096561958
64630096561959
```

The app must display **3 cards** (including both duplicates).

**Rationale**: Each line represents a distinct record that the user needs to verify. The app must never alter the user's input data. This applies to both Code 128C and QR Code modes.

---

## 22. Display Order

The grid must display codes in **exactly the same order** as the input lines.

- ❌ No sorting
- ❌ No reversing
- ❌ No grouping
- ❌ No deduplication

```
Input:          Grid:
Line 1    →    Card 1  Card 2  Card 3
Line 2    →    Card 4  Card 5  ...
Line 3    →
...
```

---

## 23. Clipboard & Keyboard

The TextBox must support standard clipboard operations:

| Shortcut | Action |
|:---|:---|
| `Ctrl + A` | Select all text |
| `Ctrl + C` | Copy selected text |
| `Ctrl + V` | Paste from clipboard |

No special barcode-copy functionality is needed.

---

## 24. Performance

### Target Scale

| Code Count | Expectation |
|:---|:---|
| 10 | Instant |
| 50 | Fast (< 1 second) |
| 100 | Smooth (< 2 seconds) |
| 200+ | Acceptable with slight delay |

> **NOTE**: QR Code generation is slightly slower than Code 128C per item (due to matrix computation). Performance targets still apply but a small additional delay for QR is acceptable.

### Optimization Strategies

- If architecture allows, avoid regenerating **all** codes when only part of the input changes
- UI must **never freeze** — use background threads if needed (but update UI safely on the main thread)
- Apply debounce (200–300ms) on text input changes
- Do **not** over-engineer for edge cases — typical usage is tens to a few hundred codes

---

## 25. Visual Design

### Style

- **Modern**, minimal, clean, professional
- Easy to read, not cluttered
- Not flashy or colorful

### Color Usage

Use color **sparingly** and only for semantic meaning:

| Meaning | Color |
|:---|:---|
| Normal / Neutral | Neutral grays / whites |
| Success / Valid | Subtle green accent |
| Error / Invalid | Subtle amber/red accent |
| Active mode tab | Accent color to indicate selected mode |

### Mode

- Light mode as default
- Dark mode is optional (nice-to-have, not required)

### Typography

- Use system fonts for readability
- Buttons must be adequately sized
- Code numbers / text must use a legible, monospace-like font

---

## 26. Responsive Window

When the user resizes the window:

| Window Width | Grid Columns |
|:---|:---|
| ≥ 1200 px | 3 columns |
| ≥ 900 px | 2 columns |
| < 900 px | 1 column |

### Resize Rules

- Cards must **not** be squished or distorted
- Code images must maintain their aspect ratio
- TextBox expands/contracts horizontally with the window
- Grid re-flows naturally
- Mode selector stays aligned properly

---

## 27. Project Structure

```
D:\Barcode\
│
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
│
├── app/
│   ├── __init__.py
│   ├── ui.py                  # GUI: window, input, grid, cards, scroll, mode selector
│   ├── barcode_generator.py   # Code 128C barcode generation
│   ├── qr_generator.py        # QR Code generation
│   ├── validator.py           # Input validation logic (both modes)
│   └── models.py              # Data models (if needed)
│
├── assets/
│   └── icon.ico               # Application icon
│
└── spec/
    └── SPEC.md                # This specification
```

> **NOTE**: Keep the structure **simple**. Do not create unnecessary files or deep directory nesting. If `models.py` is not needed, omit it.

---

## 28. Module Responsibilities

### `validator.py`

- **Code 128C validation**:
  - Check if string contains only digits (`0-9`)
  - Check if digit count is even
  - Return validation result with error message if invalid
- **QR Code validation**:
  - Check if string is non-empty
  - Warn if string exceeds recommended QR data length
  - Return validation result
- **Never** modify the input string
- Provide a unified interface: `validate(text, mode)` → returns `(is_valid, error_message)`

### `barcode_generator.py`

- Accept a validated numeric string
- Generate a Code 128C barcode using `python-barcode`
- Return a `Pillow.Image` object (or equivalent) for GUI display
- Handle barcode library errors gracefully

### `qr_generator.py`

- Accept any validated text string
- Generate a QR Code using the `qrcode` library
- Use error correction level M (default)
- Return a `Pillow.Image` object for GUI display
- Handle QR library errors gracefully

### `ui.py`

- Build the GUI using CustomTkinter
- Manage the **mode selector** (Code 128C / QR Code)
- Manage the input TextBox
- Manage the code grid and card rendering
- Manage scrolling
- Manage statistics display
- Handle debounced auto-generation
- Handle window resize / responsive grid
- Route generation to the correct generator based on selected mode

### `main.py`

- Initialize and launch the application
- Nothing else

---

## 29. Mandatory Test Cases

All test cases must pass before the app is considered complete.

### Code 128C Mode Tests

| # | Input | Expected Result |
|:---|:---|:---|
| 1 | `64630096561958` | ✅ Valid Code 128C barcode displayed |
| 2 | `001234` | ✅ Valid. Number displayed as `001234` (leading zeros preserved) |
| 3 | `12345` | ❌ Invalid — odd digit count |
| 4 | `123A45` | ❌ Invalid — contains non-numeric character |
| 5 | `12-3456` | ❌ Invalid — contains non-numeric character |
| 6 | `ABC123` | ❌ Invalid — contains non-numeric characters |
| 7 | *(empty TextBox)* | No crash, shows empty state message |
| 8 | 100 valid numeric codes | UI remains responsive, all barcodes displayed with scroll |
| 9 | Mix of valid + invalid codes | Valid codes get barcodes, invalid codes get error cards |
| 10 | Paste large list via `Ctrl + V` | App does not crash, processes all lines |

### QR Code Mode Tests

| # | Input | Expected Result |
|:---|:---|:---|
| 11 | `https://example.com` | ✅ Valid QR Code displayed |
| 12 | `Hello World 123` | ✅ Valid QR Code displayed (spaces allowed) |
| 13 | `001234` | ✅ Valid QR Code displayed (leading zeros preserved) |
| 14 | `Đây là tiếng Việt` | ✅ Valid QR Code displayed (Unicode supported) |
| 15 | *(empty TextBox)* | No crash, shows empty state message |
| 16 | 50 valid text lines | UI remains responsive, all QR codes displayed with scroll |
| 17 | Paste large list via `Ctrl + V` | App does not crash, processes all lines |

### Mode Switching Tests

| # | Action | Expected Result |
|:---|:---|:---|
| 18 | Enter numeric data in 128C mode → switch to QR mode | Grid regenerates as QR codes, input text preserved |
| 19 | Enter text data in QR mode → switch to 128C mode | Invalid text shows error cards, valid numbers show barcodes |
| 20 | Rapidly switch modes multiple times | App does not crash or freeze |

---

## 30. Error Handling Policy

> **CAUTION**: The app must **NEVER** crash due to user input.

### Handled Scenarios

- Empty input
- Invalid characters (Code 128C mode)
- Odd-length codes (Code 128C mode)
- Excessively long data (QR Code mode)
- Blank lines in input
- Barcode generation library errors
- QR Code generation library errors
- Pillow image processing errors
- UI rendering errors
- Mode switching during generation

### Rules

- Never show a Python traceback to the end user
- Display user-friendly error messages
- Isolate errors per-code (one bad code must not block others)
- If a critical error occurs, show a simple dialog with a human-readable message

---

## 31. Data Persistence

- **None**. All data exists only in RAM while the app is running.
- Closing the app **discards all data**. This is the intended behavior.
- No files are saved to disk during normal operation.

---

## 32. Features Explicitly Excluded

The following features are **NOT** to be implemented in this version:

| Feature | Status |
|:---|:---|
| Save / Download PNG | ❌ Not needed |
| Export to file | ❌ Not needed |
| Additional barcode types (Code 39, EAN, etc.) | ❌ Future versions |
| QR Code custom error correction level selector | ❌ Future versions |
| QR Code logo embedding | ❌ Future versions |
| Database | ❌ Not needed |
| Cloud sync | ❌ Not needed |
| User settings/preferences | ❌ Not needed |
| Print function | ❌ Not needed |
| Copy barcode image | ❌ Not needed |
| Save/Download buttons in UI | ❌ Do not add |
| Login / Authentication | ❌ Not needed |

---

## 33. Build & Packaging

### Tool

**PyInstaller**

### Output

Single executable: `BarcodeGenerator.exe`

### PyInstaller Flags

```bash
pyinstaller --onefile --windowed --name BarcodeGenerator --icon assets/icon.ico main.py
```

- `--windowed` — Do **not** open a console window
- `--onefile` — Single `.exe` file
- `--icon` — Application icon

### Requirements

- The `.exe` must run on Windows **without** Python installed
- No complex installer needed for v1

---

## 34. README Requirements

Create a `README.md` that covers:

1. What the app does (Code 128C + QR Code generation)
2. Supported code types and their rules
3. How to install dependencies (`pip install -r requirements.txt`)
4. How to run in development mode (`python main.py`)
5. How to build the `.exe`
6. Project structure overview
7. Code 128C rules and constraints
8. QR Code capabilities

---

## 35. Dependencies

`requirements.txt`:

```
customtkinter
python-barcode
qrcode
Pillow
```

- **No** unnecessary packages
- **No** web frameworks
- **No** database drivers

---

## 36. Priority Order

When making design or implementation decisions, follow this priority:

| Priority | Principle |
|:---|:---|
| 🥇 1 | **Correct encoding** — Code 128C and QR Code must be technically accurate |
| 🥈 2 | **Preserve user data** — never modify input |
| 🥉 3 | **Easy comparison** — code image ↔ original input must be clear |
| 4 | **Fast UI** — responsive, no freezing |
| 5 | **Simple** — minimal features, minimal clicks |
| 6 | **Maintainable code** — clean, readable, documented |

---

## 37. Development Phases

> **IMPORTANT**: After each phase, the app must still **run without errors**. Do not proceed to the next phase if the current phase has bugs.

| Phase | Description |
|:---|:---|
| **1** | Create project structure and `requirements.txt` |
| **2** | Build basic GUI window with CustomTkinter |
| **3** | Add mode selector (Code 128C / QR Code) |
| **4** | Add multi-line TextBox input |
| **5** | Implement Code 128C validation (`validator.py`) |
| **6** | Implement QR Code validation (`validator.py`) |
| **7** | Implement Code 128C barcode generation (`barcode_generator.py`) |
| **8** | Implement QR Code generation (`qr_generator.py`) |
| **9** | Display a single code card in the UI |
| **10** | Implement multi-code grid layout |
| **11** | Implement scrollbar for the result area |
| **12** | Implement auto-generation on input change (with debounce) |
| **13** | Implement mode switching with re-generation |
| **14** | Implement statistics (total / valid / error counts) |
| **15** | Run all mandatory test cases (128C + QR + mode switching) |
| **16** | Build `.exe` with PyInstaller |
| **17** | Test `.exe` on Windows |

---

## 38. Expected User Experience

The final app should deliver this experience:

### Scenario A: Code 128C

1. User opens `BarcodeGenerator.exe`.
2. A clean window appears with mode selector set to **Code 128C** (default).
3. User pastes:

```
64630096561958
64630096561959
64630096561960
64630096561961
```

4. Within milliseconds, four barcode cards appear:

```
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│                │ │                │ │                │
│    BARCODE     │ │    BARCODE     │ │    BARCODE     │
│                │ │                │ │                │
│64630096561958  │ │64630096561959  │ │64630096561960  │
└────────────────┘ └────────────────┘ └────────────────┘

┌────────────────┐
│                │
│    BARCODE     │
│                │
│64630096561961  │
└────────────────┘
```

5. **No additional action required.**

### Scenario B: QR Code

1. User clicks **QR Code** on the mode selector.
2. User pastes:

```
https://example.com/page1
https://example.com/page2
Hello World
```

3. Three QR Code cards appear instantly:

```
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   ██ █ ██      │ │   █ ██ ██      │ │   ██ ██ █      │
│   █ ██ █       │ │   ██ █ █       │ │   █ █ ██       │
│   ██ █ ██      │ │   █ ██ ██      │ │   ██ ██ █      │
│                │ │                │ │                │
│example.com/... │ │example.com/... │ │ Hello World    │
└────────────────┘ └────────────────┘ └────────────────┘
```

4. The user verifies each QR code matches the expected text.

---

## 39. Completion Criteria

The project is **only considered complete** when ALL of the following are verified:

### Code 128C

- [ ] Barcodes are genuinely **Code 128C** (not 128A or 128B)
- [ ] Odd-length numeric strings are **rejected** in 128C mode
- [ ] Non-numeric strings are **rejected** in 128C mode

### QR Code

- [ ] QR Codes are generated correctly and are scannable
- [ ] Any text input is accepted in QR mode
- [ ] Unicode / Vietnamese text works in QR mode

### General

- [ ] App opens without errors
- [ ] Mode selector switches between Code 128C and QR Code
- [ ] Switching modes re-generates all codes correctly
- [ ] User input is **preserved exactly** (leading zeros, no formatting)
- [ ] Multiple lines generate multiple code cards
- [ ] Grid layout works correctly
- [ ] Scrollbar works with 100+ codes
- [ ] Window resize adjusts grid columns
- [ ] Duplicate inputs are **not removed**
- [ ] Display order matches input order
- [ ] App does **not crash** with any input
- [ ] Statistics update automatically
- [ ] Empty state displays correctly
- [ ] `.exe` runs on Windows without Python installed
- [ ] All 20 mandatory test cases pass

---

> **END OF SPECIFICATION**
