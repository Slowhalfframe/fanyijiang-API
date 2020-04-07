import hashlib
from PIL import Image


def id_md5(id):
    m = hashlib.md5()
    m.update(str(id).encode('utf8'))  # 传入需要加密的字符串进行MD5加密，适用于ID混淆等
    return m.hexdigest()


def compress_picture(pic_path, size=None):
    '''

    :param pic_path: 图片路径
    :param size: 压缩尺寸，没有则按照比例进行压缩
    :return: None
    '''
    _image = Image.open(pic_path)
    if not size:
        width = _image.width
        height = _image.height
        rate = 1.0  # 压缩率
        # 根据图像大小设置压缩率
        if width >= 2000 or height >= 2000:
            rate = 0.3
        elif width >= 1000 or height >= 1000:
            rate = 0.6
        elif width >= 500 or height >= 500:
            rate = 0.9

        width = int(width * rate)  # 新的宽
        height = int(height * rate)  # 新的高
    else:
        width, height = size
    # Image.NEAREST：最低质量，
    # Image.BILINEAR：双线性，
    # Image.BICUBIC：三次样条插值，
    # Image.ANTIALIAS：最高质量
    _image.thumbnail((width, height), Image.ANTIALIAS)  # 生成缩略图
    _image.save(pic_path, quality=95)
