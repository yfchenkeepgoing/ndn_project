import socket
import hashlib


def get_host_ip():
    '''
    获取本地IP地址的函数
    Function to get the local IP Address
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def hashstr(string):
    '''
    执行字符串 md5 哈希的函数  
    Function to perform md5 hashing of strings
    '''
    md5 = hashlib.md5()
    md5.update(string.encode('utf-8'))
    return md5.hexdigest()
