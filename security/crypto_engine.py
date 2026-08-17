import os
import json
import io
from cryptography.fernet import Fernet
from security.keystore_manager import KeystoreManager

class CryptoEngine:
    """Zero-trust encryption pipeline operating exclusively in memory."""
    
    def __init__(self):
        km = KeystoreManager()
        master_key = km.get_or_create_master_key()
        self.cipher = Fernet(master_key)

    def encrypt_image_bytes(self, image_bytes: bytes, metadata: dict) -> bytes:
        """Combines metadata + image buffer and encrypts into a single .spv payload."""
        payload = {
            "metadata": metadata,
            "data": base64.b64encode(image_bytes).decode('utf-8')
        }
        json_data = json.dumps(payload).encode('utf-8')
        return self.cipher.encrypt(json_data)

    def decrypt_spv_bytes(self, spv_bytes: bytes) -> tuple[bytes, dict]:
        """Decrypts .spv buffer in memory returning (raw_image_bytes, metadata)."""
        decrypted_json_data = self.cipher.decrypt(spv_bytes)
        payload = json.loads(decrypted_json_data.decode('utf-8'))
        image_bytes = base64.b64decode(payload["data"].encode('utf-8'))
        return image_bytes, payload.get("metadata", {})

    def save_encrypted_file(self, encrypted_bytes: bytes, target_path: str):
        """Writes encrypted bytes directly to .spv file."""
        with open(target_path, "wb") as f:
            f.write(encrypted_bytes)

    def read_encrypted_file(self, spv_path: str) -> tuple[bytes, dict]:
        """Reads encrypted file and decrypts straight to memory."""
        with open(spv_path, "rb") as f:
            encrypted_bytes = f.read()
        return self.decrypt_spv_bytes(encrypted_bytes)
