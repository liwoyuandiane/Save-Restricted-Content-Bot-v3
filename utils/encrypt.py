# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os
import base64
import logging
from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import MASTER_KEY, IV_KEY

# 配置日志
logger = logging.getLogger(__name__)

def derive_key(password: str = MASTER_KEY, salt: str = IV_KEY, length: int = 16) -> bytes:
    """使用PBKDF2派生加密密钥"""
    try:
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt_bytes,
            iterations=100000,
        )
        
        key = kdf.derive(password_bytes)
        logger.debug("密钥派生成功")
        return key
    except Exception as e:
        logger.error(f"密钥派生失败: {e}")
        raise

def encrypt_string(plaintext: str) -> str:
    """加密字符串"""
    try:
        if not plaintext:
            logger.warning("尝试加密空字符串")
            return ""
        
        key = derive_key()
        nonce = os.urandom(12)  # GCM模式需要12字节的nonce
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        tag = encryptor.tag
        
        # 组合nonce + tag + ciphertext
        encrypted_data = nonce + tag + ciphertext
        encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
        
        logger.debug("字符串加密成功")
        return encoded_data
    except Exception as e:
        logger.error(f"字符串加密失败: {e}")
        raise

def decrypt_string(encrypted_data: str) -> str:
    """解密字符串"""
    try:
        if not encrypted_data:
            logger.warning("尝试解密空字符串")
            return ""
        
        key = derive_key()
        
        # 解码base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # 分离nonce、tag和ciphertext
        nonce = encrypted_bytes[:12]
        tag = encrypted_bytes[12:28]
        ciphertext = encrypted_bytes[28:]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
        decryptor = cipher.decryptor()
        
        decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = decrypted_bytes.decode('utf-8')
        
        logger.debug("字符串解密成功")
        return plaintext
    except Exception as e:
        logger.error(f"字符串解密失败: {e}")
        raise

# 为了向后兼容，保留旧的函数名
def ecs(s: str) -> str:
    """加密字符串（向后兼容）"""
    return encrypt_string(s)

def dcs(ed: str) -> str:
    """解密字符串（向后兼容）"""
    return decrypt_string(ed)
