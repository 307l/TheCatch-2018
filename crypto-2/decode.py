#Prerequisities: pip install pycrypto
import base64
from Crypto.Cipher import AES
from Crypto import Random

def _unpad(s):
    return s[:-ord(s[len(s)-1:])]

enc = base64.b64decode('f3QvZm8PqC0ku9q3RVfsYvNv6p8H/R4wadqsF0cYRKEfFxtV5fCLBraxqyWriwa+p28oRY0RUvFABsjcRDRwww==')
key="\x4e\x99\x06\xe8\xfc\xb6\x6c\xc9\xfa\xf4\x93\x10\x62\x0f\xfe\xe8\xf4\x96\xe8\x06\xcc\x05\x79\x90\x20\x9b\x09\xa4\x33\xb6\x6c\x1b"
cipher = AES.new(key, AES.MODE_CBC, "\x00"*16 ) #IV = zeroes
print _unpad(cipher.decrypt(enc))

