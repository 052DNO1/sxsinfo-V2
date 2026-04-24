"""
密码加密解密工具
"""

import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_password(encrypted_data: str) -> str:
    """
    解密前端加密的密码
    
    前端加密格式: timeHex:encryptedBase64
    - timeHex: 16位十六进制时间戳
    - encryptedBase64: Base64编码的加密数据
    """
    if not encrypted_data or ':' not in encrypted_data:
        return encrypted_data
    
    secret_key = os.environ.get('PASSWORD_ENCRYPT_KEY', '')
    if not secret_key:
        return encrypted_data
    
    try:
        time_hex, encrypted_base64 = encrypted_data.split(':')
        
        iv = time_hex[:16].encode('utf-8')
        
        key = secret_key.ljust(32, '0')[:32].encode('utf-8')
        
        encrypted_bytes = base64.b64decode(encrypted_base64)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        
        return decrypted.decode('utf-8')
    except Exception as e:
        return encrypted_data
