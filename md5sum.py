# -*- coding: utf-8 -*-
import hashlib
import os  
  
def md5hex(word):  
    """ MD5加密算法，返回32位小写16进制符号 """  
    if isinstance(word, unicode):  
        word = word.encode("utf-8")  
    elif not isinstance(word, str):  
        word = str(word)  
    m = hashlib.md5()  
    m.update(word)  
    return m.hexdigest()    

def check_sum(fname, algorithm):  
    def read_chunks(fh):  
        fh.seek(0)  
        chunk = fh.read(8096*1024)  
        while chunk:  
            yield chunk  
            chunk = fh.read(8096*1024)  
        else: #最后要将游标放回文件开头  
            fh.seek(0)            

    m = algorithm  
    if isinstance(fname, basestring) \
            and os.path.exists(fname):  
        with open(fname, "rb") as fh:  
            for chunk in read_chunks(fh):  
                m.update(chunk)  
    #上传的文件缓存 或 已打开的文件流  
    elif fname.__class__.__name__ in ["StringIO", "StringO"] \
                or isinstance(fname, file):  
        for chunk in read_chunks(fname):  
            m.update(chunk)  
    else:  
        return ""  
    return m.hexdigest()

def md5sum(fname):
    return check_sum(fname, hashlib.md5())

def sha1sum(fname):
    return check_sum(fname, hashlib.sha1())

def sha256sum(fname):
    return check_sum(fname, hashlib.sha256())

if __name__ == "__main__":
    #hexd = md5sum("e:\cpeng\Downloads\ubuntu-14.04.2-server-amd64.iso")
    hexd = sha256sum("c:\Users\cpeng\Desktop\Log\Huangxiangquan\lieyanqibao_300008979590_3000001336.apk");
    #hexd = md5sum("e:\cpeng\Downloads\wubi.exe")
    print hexd
