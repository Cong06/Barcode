# Barcode Generator (Code 128C & QR Code)

Ứng dụng Desktop Windows nhẹ, mượt và chính xác cao dùng để tự động tạo mã vạch **Code 128C** và **QR Code** từ danh sách dữ liệu nhập vào, hiển thị dạng lưới (Grid) để đối chiếu trực tiếp trên màn hình.

---

## 🌟 Tính năng chính

- **Tạo mã vạch Code 128C**: Tự động xác thực dữ liệu chữ số chẵn (Subtype C), giữ nguyên các số 0 ở đầu.
- **Tạo mã QR (QR Code)**: Hỗ trợ tạo mã QR từ chuỗi văn bản, đường dẫn URL bất kỳ.
- **Tự động cập nhật (Debounce)**: Tự tạo mã sau 300ms dừng gõ phím.
- **Hiển thị dạng Grid linh hoạt**: 1, 2 hoặc 3 cột tùy thuộc độ rộng cửa sổ ứng dụng.
- **Thống kê thời gian thực**: Tổng số dòng, số mã thành công, số mã lỗi.
- **Chi tiết & Sao chép**: Xem phóng to mã, sao chép dữ liệu chỉ bằng 1 cú click.
- **100% Offline**: Không cần kết nối Internet, không lưu trữ dữ liệu cá nhân.

---

## 🛠️ Yêu cầu hệ thống & Cài đặt

### Yêu cầu:
- Windows 10/11
- Python 3.10 trở lên (nếu chạy từ source)

### Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng dẫn sử dụng

### 1. Chạy ứng dụng từ mã nguồn (Source code):
```bash
python main.py
```

### 2. Thao tác trên giao diện:
1. **Chọn loại mã**: Chọn **Code 128C** hoặc **QR Code** từ thanh chuyển đổi ở trên cùng.
2. **Nhập dữ liệu**: Dán danh sách mã vào khung văn bản bên trái (Mỗi mã trên 1 dòng).
3. **Xem kết quả**: Danh sách mã sẽ tự động xuất hiện ở lưới bên phải.
4. **Xem chi tiết / Coppy**: Bấm **Chi tiết** trên từng ô mã để xem hình lớn hoặc bấm **Copy** để sao chép chuỗi gốc.

---

## 📦 Đóng gói ứng dụng thành file EXE (PyInstaller)

Để tạo file ứng dụng chạy độc lập `.exe` (chạy không cần cài Python):

```bash
pyinstaller --noconfirm --onedir --windowed --icon="assets/icon.ico" --add-data "assets;assets" --name "BarcodeGenerator" main.py
```

Sau khi hoàn tất, file thực thi sẽ nằm tại thư mục:
`dist/BarcodeGenerator/BarcodeGenerator.exe`

---

## 📁 Cấu trúc thư mục dự án

```
d:/Barcode/
├── app/
│   ├── __init__.py
│   ├── validator.py          # Kiểm tra dữ liệu hợp lệ (Code 128C & QR)
│   ├── barcode_generator.py  # Tạo hình ảnh Code 128C
│   ├── qr_generator.py       # Tạo hình ảnh QR Code
│   └── ui.py                 # Giao diện CustomTkinter
├── assets/
│   ├── icon.ico              # Icon ứng dụng (.ico)
│   └── icon.png              # Icon ứng dụng (.png)
├── spec/
│   └── SPEC.md               # Đặc tả kỹ thuật chi tiết
├── main.py                   # File khởi chạy chính
├── requirements.txt          # Danh sách thư viện phụ thuộc
└── README.md                 # Hướng dẫn sử dụng & Đóng gói
```
