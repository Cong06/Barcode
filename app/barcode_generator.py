"""
Code 128C barcode image generator.
Uses python-barcode library to produce correct Code 128 Subtype C barcodes.
"""

import io
from PIL import Image

# python-barcode uses 'barcode' as the import name
import barcode
from barcode.writer import ImageWriter


def generate_code128c(
    data: str, fg_color: str = "#000000", bg_color: str = "#FFFFFF"
) -> Image.Image | None:
    """
    Generate a Code 128C barcode image from numeric data.
    
    The data must already be validated (digits only, even length).
    
    Args:
        data: A string of digits with even length.
        fg_color: Hex color string for bars.
        bg_color: Hex color string for background.
    
    Returns:
        PIL.Image.Image on success, None on failure.
    """
    try:
        # python-barcode's Code128 class auto-selects subtype.
        # For pure even-length digits, it will use Subtype C automatically.
        code128_class = barcode.get_barcode_class('code128')
        
        # Configure the writer for clean output
        writer = ImageWriter()
        
        # Create barcode instance
        barcode_instance = code128_class(data, writer=writer)
        
        # Render to bytes buffer
        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.4,       # Width of each bar module in mm
            'module_height': 18.0,     # Height of bars in mm
            'quiet_zone': 6.5,         # Quiet zone width in mm
            'font_size': 0,            # Hide text (we show it separately in UI)
            'text_distance': 1.0,
            'write_text': False,       # Don't render text on barcode image
            'dpi': 300,                # High resolution
            'bar_color': fg_color,
            'back_color': bg_color,
        })
        
        # Read back as PIL Image
        buffer.seek(0)
        img = Image.open(buffer).copy()  # .copy() to detach from buffer
        buffer.close()
        
        return img
        
    except Exception:
        return None

