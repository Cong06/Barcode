"""
QR Code image generator.
Uses the qrcode library (ISO/IEC 18004 compliant).
"""

from PIL import Image
import qrcode
import qrcode.constants


def generate_qrcode(
    data: str, fill_color: str = "#000000", back_color: str = "#FFFFFF"
) -> Image.Image | None:
    """
    Generate a QR Code image from any text data.
    
    Uses Error Correction Level M (~15% recovery) as default.
    Auto-selects optimal QR version based on data length.
    
    Args:
        data: Any non-empty text string.
        fill_color: Foreground color (modules).
        back_color: Background color.
    
    Returns:
        PIL.Image.Image on success, None on failure.
    """
    try:
        qr = qrcode.QRCode(
            version=None,  # Auto-select version
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Ensure we return a standard PIL Image
        if not isinstance(img, Image.Image):
            img = img.convert("RGB")
        
        return img
        
    except Exception:
        return None

