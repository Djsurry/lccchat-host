from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import os, sys



def encrypt(s):
    key = os.urandom(16)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return (iv + cipher.encrypt(s), key)

def decrypt(s, key):
    iv = s[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(s)[16:].decode("utf-8")
