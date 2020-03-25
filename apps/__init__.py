import os
import re


def xss_safe(value):
    """检查字符串对XSS攻击是否免疫"""

    if not re.search(r"[<>&]", value):
        return True
    else:
        return False


def legal_image_path(path):
    """检查字符串是否是合法的图片路径"""

    file, ext = os.path.splitext(path)
    if not file:
        return False
    if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
        return False
    return True
