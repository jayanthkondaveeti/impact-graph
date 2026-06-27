import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from app.core.config import settings

def _get_key_bytes() -> bytes:
    """Retrieve and convert the hex config key to raw 32 bytes."""
    hex_key = settings.IMPACTGRAPH_SECRET_KEY.strip()
    return bytes.fromhex(hex_key)

def encrypt_data(plaintext: str) -> str:
    """
    Encrypt a clear-text string using AES-256-CBC.
    Returns a base64 encoded string containing the 16-byte random IV prepended to the ciphertext.
    """
    if not plaintext:
        return ""
        
    key = _get_key_bytes()
    iv = os.urandom(16) # Random IV
    
    # Pad the plaintext to match AES block size (128 bits / 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV and Ciphertext, and encode as base64
    combined = iv + ciphertext
    return base64.b64encode(combined).decode('utf-8')

def decrypt_data(encrypted_base64: str) -> str:
    """
    Decrypt a base64 string using AES-256-CBC.
    Extracts the IV from the first 16 bytes of the decoded payload.
    """
    if not encrypted_base64:
        return ""
        
    key = _get_key_bytes()
    combined = base64.b64decode(encrypted_base64.encode('utf-8'))
    
    iv = combined[:16]
    ciphertext = combined[16:]
    
    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
    
    return plaintext_bytes.decode('utf-8')
