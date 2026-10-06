"""
Code 128C barcode image generator.
Uses python-barcode library to produce correct Code 128 Subtype C barcodes.
"""

import io
from PIL import Image

# python-barcode uses 'barcode' as the import name
import barcode
from barcode.writer import ImageWriter


def generate_code128(
    data: str, fg_color: str = "#000000", bg_color: str = "#FFFFFF"
) -> Image.Image | None:
    """
    Generate a Code 128 barcode image (supports Code 128 Auto, 128A, 128B, 128C).
    
    Args:
        data: The input string.
        fg_color: Hex color string for bars.
        bg_color: Hex color string for background.
    
    Returns:
        PIL.Image.Image on success, None on failure.
    """
    try:
        code128_class = barcode.get_barcode_class('code128')
        writer = ImageWriter()
        barcode_instance = code128_class(data, writer=writer)
        
        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.4,       # Width of each bar module in mm
            'module_height': 18.0,     # Height of bars in mm
            'quiet_zone': 6.5,         # Quiet zone width in mm
            'font_size': 0,            # Hide text (rendered separately in UI)
            'text_distance': 1.0,
            'write_text': False,
            'dpi': 300,                # High resolution
            'bar_color': fg_color,
            'back_color': bg_color,
        })
        
        buffer.seek(0)
        img = Image.open(buffer).copy()
        buffer.close()
        return img
        
    except Exception:
        return None


# Alias for backward compatibility
generate_code128c = generate_code128

