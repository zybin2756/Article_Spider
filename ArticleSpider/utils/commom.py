import hashlib

def get_md5(str):
    str = str.encode(encoding='gb2312')
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()