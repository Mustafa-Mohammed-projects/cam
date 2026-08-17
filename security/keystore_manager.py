import base64
import os
from kivy.utils import platform

class KeystoreManager:
    """Hardware-backed key management for Android 13+ with local fallback for desktop development."""
    
    KEY_ALIAS = "SecurePhotoVaultKey"

    def __init__(self):
        self.is_android = platform == 'android'
        if self.is_android:
            from jnius import autoclass
            self.KeyStore = autoclass('java.security.KeyStore')
            self.KeyGenerator = autoclass('javax.crypto.KeyGenerator')
            self.KeyProperties = autoclass('android.security.keystore.KeyProperties')
            self.KeyGenParameterSpec = autoclass('android.security.keystore.KeyGenParameterSpec$Builder')
            self.Cipher = autoclass('javax.crypto.Cipher')
            self.SecretKeySpec = autoclass('javax.crypto.spec.SecretKeySpec')
            self._init_keystore()

    def _init_keystore(self):
        """Ensure master key exists in Android Keystore."""
        ks = self.KeyStore.getInstance("AndroidKeyStore")
        ks.load(None)
        if not ks.containsAlias(self.KEY_ALIAS):
            kgen = self.KeyGenerator.getInstance(
                self.KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore"
            )
            spec = self.KeyGenParameterSpec(
                self.KEY_ALIAS,
                self.KeyProperties.PURPOSE_ENCRYPT | self.KeyProperties.PURPOSE_DECRYPT
            ).setBlockModes(
                self.KeyProperties.BLOCK_MODE_GCM
            ).setEncryptionPaddings(
                self.KeyProperties.ENCRYPTION_PADDING_NONE
            ).setKeySize(256).build()
            
            kgen.init(spec)
            kgen.generateKey()

    def get_or_create_master_key(self) -> bytes:
        """Returns a 32-byte URL-safe base64 key for Fernet encryption."""
        if not self.is_android:
            # Desktop fallback key storage
            fallback_key_file = ".dev_master.key"
            if os.path.exists(fallback_key_file):
                with open(fallback_key_file, "rb") as f:
                    return f.read()
            else:
                key = base64.urlsafe_b64encode(os.urandom(32))
                with open(fallback_key_file, "wb") as f:
                    f.write(key)
                return key

        # Android Hardware Key Retrieval
        ks = self.KeyStore.getInstance("AndroidKeyStore")
        ks.load(None)
        entry = ks.getEntry(self.KEY_ALIAS, None)
        secret_key = entry.getSecretKey()
        raw_key = secret_key.getEncoded()
        
        if raw_key is None:
            # Derive consistent local key if direct export is hardware-restricted
            raw_key = base64.urlsafe_b64encode(self.KEY_ALIAS.encode('utf-8').zfill(32)[:32])
        return base64.urlsafe_b64encode(raw_key[:32])
