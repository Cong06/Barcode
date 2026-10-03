# Barcode Generator (Code 128C & QR Code) - Red & White Edition

Ứng dụng Desktop Windows nhẹ, mượt và chính xác cao dùng để tự động tạo mã vạch **Code 128C** và **QR Code** từ danh sách dữ liệu nhập vào, hiển thị dạng lưới (Grid) căn giữa đẹp mắt để đối chiếu trực tiếp trên màn hình.

> **Developed by HOANG VAN CONG**

---

## ⚡ Tải Về Nhanh File `.exe` (Chạy Độc Lập)

Bạn có thể tải ngay file ứng dụng thực thi duy nhất **`BarcodeGenerator.exe`** (chạy trực tiếp trên Windows không cần cài Python) tại đây:

👉 **[Tải xuống Release v1.0.0 (BarcodeGenerator.exe)](https://github.com/Cong06/Barcode/releases/tag/v1.0.0)**

---

## 🌟 Tính Năng Nổi Bật

- **Tạo mã vạch Code 128C chuẩn**: Xác thực chữ số chẵn (Subtype C), giữ nguyên các số 0 ở đầu.
- **Tạo mã QR (QR Code)**: Hỗ trợ văn bản UTF-8 và đường dẫn URL bất kỳ với mức sửa lỗi `ERROR_CORRECT_M`.
- **Giao diện Red & White Edition**: Phong cách màu Đỏ Tươi & Trắng sang trọng, sắc nét.
- **Nút "🚀 TẠO MÃ" (Ctrl + Enter)**: Chủ động phát mã, tránh giật lag khi paste danh sách dài.
- **Nút "🔄 Refresh"**: Xóa nhanh toàn bộ ô nhập dữ liệu chỉ bằng 1 cú nhấp.
- **Căn giữa 100% (Row-Level Centering)**: Mã vạch và QR luôn được đặt ở **chính giữa màn hình** dù chỉ có 1 mã hay nhiều mã.
- **Tùy chỉnh hiển thị linh hoạt**:
  - *Kích thước mã*: 75%, 100%, 130%, 160%.
  - *Số cột*: Tự động (Responsive) hoặc 1 Cột, 2 Cột, 3 Cột.
  - *Bảng màu sắc*: Cổ điển, Đỏ Rực Rỡ, Navy Đậm, Xanh Emerald, Tím Violet.
- **100% Offline & Bảo Mật**: Không cần Internet, không thu thập dữ liệu người dùng.

---

## 🚀 Hướng Dẫn Dành Cho Lập Trình Viên (Source Code)

### Cài đặt phụ thuộc:
```bash
pip install -r requirements.txt
```

### Chạy ứng dụng từ mã nguồn:
```bash
python main.py
```

### Đóng gói file `.exe` đơn (Single File Executable):
```bash
pyinstaller --noconfirm --onefile --windowed --icon="assets/icon.ico" --add-data "assets;assets" --name "BarcodeGenerator" main.py
```
*File thực thi sẽ nằm tại `dist/BarcodeGenerator.exe`.*

---

## 📁 Cấu Trúc Dự Án

```
d:/Barcode/
├── app/
│   ├── __init__.py
│   ├── validator.py          # Xác thực dữ liệu Code 128C & QR Code
│   ├── barcode_generator.py  # Tạo hình ảnh Code 128C nét cao (300 DPI)
│   ├── qr_generator.py       # Tạo hình ảnh QR Code (ISO/IEC 18004)
│   └── ui.py                 # Giao diện Red & White Edition (CustomTkinter)
├── assets/
│   ├── icon.ico              # Biểu tượng Windows (.ico)
│   └── icon.png              # Biểu tượng PNG
├── spec/
│   └── SPEC.md               # Đặc tả kỹ thuật chi tiết
├── main.py                   # Entry point ứng dụng
├── requirements.txt          # Danh sách thư viện phụ thuộc
└── README.md                 # Hướng dẫn sử dụng & Tải về
```
