import os
import socket
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

load_dotenv()

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


def derive_key_from_password():
    '''
    Function to derive the encryption key from the password and salt stored in the env variables
    '''
    # Convert the password and salt to bytes
    password = os.environ.get('PASSWORD').encode('utf-8')
    salt = os.environ.get('SALT').encode('utf-8')

    # Create a PBKDF2HMAC object using 'SHA-256' as the hash function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=salt,
        length=32,
        iterations=100000,
        backend=default_backend()
    )
    # Derive & return the key
    return kdf.derive(password)


def encrypt_with_aes(data):
    '''
    Function to encrypt the data with the key supplied using AES Algo
    '''
    encryption_key = derive_key_from_password()
    # Generate a random IV (Initialization Vector)
    iv = os.environ.get('IV').encode('utf-8')

    # Create an AES cipher object with the key and mode of operation (CBC)
    cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(iv), backend=default_backend())

    # Encrypt the data
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    # Return the IV and ciphertext
    return iv + ciphertext


def decrypt_with_aes(data):
    '''
    Function to decrypt the data with the key supplied using AES Algo
    '''
    encryption_key = derive_key_from_password()
    # Extract the IV from the ciphertext
    iv = os.environ.get('IV').encode('utf-8')
    data = data[16:]

    # Create an AES cipher object with the key and mode of operation (CBC)
    cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(iv), backend=default_backend())

    # Decrypt the data
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data) + decryptor.finalize()

    # Return the decrypted data
    return decrypted_data
