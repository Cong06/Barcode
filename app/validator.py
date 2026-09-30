"""
Validator module for Code 128C and QR Code input validation.
CRITICAL: Never modify the input string.
"""


def validate_code128c(text: str) -> tuple[bool, str]:
    """
    Validate input for Code 128C barcode.
    
    Rules:
    - Must contain only digits 0-9
    - Must have even number of digits
    - Leading zeros are valid and preserved
    
    Returns:
        (is_valid, error_message)
    """
    if not text:
        return (False, "")
    
    # Check digits only
    if not text.isdigit():
        return (False, "Không hợp lệ: Chỉ được chứa chữ số 0-9.")
    
    # Check even length
    if len(text) % 2 != 0:
        return (False, "Không hợp lệ: Code 128C yêu cầu số lượng chữ số chẵn.")
    
    return (True, "")


def validate_qrcode(text: str) -> tuple[bool, str]:
    """
    Validate input for QR Code.
    
    Rules:
    - Must be non-empty
    - Any characters accepted (UTF-8)
    - Warning if exceeds recommended length
    
    Returns:
        (is_valid, error_message) — error_message may contain a warning even if valid
    """
    if not text:
        return (False, "")
    
    # Warn if data is very long
    if len(text) > 4296:
        return (True, "Cảnh báo: Dữ liệu quá dài, mã QR có thể không quét được.")
    
    return (True, "")


def validate(text: str, mode: str) -> tuple[bool, str]:
    """
    Unified validation interface.
    
    Args:
        text: The raw input string (never modified)
        mode: "Code 128C" or "QR Code"
    
    Returns:
        (is_valid, error_message)
    """
    if mode == "Code 128C":
        return validate_code128c(text)
    elif mode == "QR Code":
        return validate_qrcode(text)
    else:
        return (False, "Chế độ không hợp lệ.")
