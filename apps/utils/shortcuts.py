import hashlib


def id_md5(id):
    m = hashlib.md5()
    m.update(str(id).encode('utf8'))  # 传入需要加密的字符串进行MD5加密，适用于ID混淆等
    return m.hexdigest()
