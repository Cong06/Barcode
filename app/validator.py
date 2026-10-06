"""
Validator module for Code 128 variants and QR Code input validation.
CRITICAL: Never modify the input string.
"""


def validate_code128(text: str) -> tuple[bool, str]:
    """
    Validate input for Code 128 (Auto mode).
    Rules: Must contain only ASCII characters (0-127).
    """
    if not text:
        return (False, "")
    try:
        text.encode("ascii")
        return (True, "")
    except UnicodeEncodeError:
        return (False, "Không hợp lệ: Code 128 chỉ chấp nhận ký tự ASCII.")


def validate_code128a(text: str) -> tuple[bool, str]:
    """
    Validate input for Code 128A.
    Rules: ASCII characters without lowercase letters (a-z).
    """
    if not text:
        return (False, "")
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        return (False, "Không hợp lệ: Code 128A chỉ chấp nhận ký tự ASCII.")

    if any("a" <= c <= "z" for c in text):
        return (False, "Không hợp lệ: Code 128A không chấp nhận chữ thường (a-z).")

    return (True, "")


def validate_code128b(text: str) -> tuple[bool, str]:
    """
    Validate input for Code 128B.
    Rules: Printable ASCII characters (ASCII 32 to 126).
    """
    if not text:
        return (False, "")
    for char in text:
        if ord(char) < 32 or ord(char) > 126:
            return (False, "Không hợp lệ: Code 128B chỉ chấp nhận ký tự ASCII in được.")
    return (True, "")


def validate_code128c(text: str) -> tuple[bool, str]:
    """
    Validate input for Code 128C barcode.

    Rules:
    - Must contain only digits 0-9
    - Must have even number of digits
    - Leading zeros are valid and preserved
    """
    if not text:
        return (False, "")

    if not text.isdigit():
        return (False, "Không hợp lệ: Chỉ được chứa chữ số 0-9.")

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
    """
    if not text:
        return (False, "")

    if len(text) > 4296:
        return (True, "Cảnh báo: Dữ liệu quá dài, mã QR có thể không quét được.")

    return (True, "")


def validate(text: str, mode: str) -> tuple[bool, str]:
    """
    Unified validation interface.

    Args:
        text: The raw input string (never modified)
        mode: "Code 128", "Code 128A", "Code 128B", "Code 128C", or "QR Code"

    Returns:
        (is_valid, error_message)
    """
    if mode == "Code 128":
        return validate_code128(text)
    elif mode == "Code 128A":
        return validate_code128a(text)
    elif mode == "Code 128B":
        return validate_code128b(text)
    elif mode == "Code 128C":
        return validate_code128c(text)
    elif mode == "QR Code":
        return validate_qrcode(text)
    else:
        return (False, "Chế độ không hợp lệ.")
