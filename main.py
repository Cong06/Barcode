"""
Barcode Generator — Entry Point
Lightweight desktop app for generating Code 128C barcodes and QR Codes.
"""

from app.ui import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
