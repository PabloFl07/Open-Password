import base64
import secrets
import string
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionManager:
    """Maneja el cifrado AES-256-GCM y la derivación de claves."""
    
    def __init__(self, master_password: str, salt_str: str):
        # 1. Derivar la clave de 32 bytes (256 bits)
        # Usamos un salt fijo para este ejemplo simplificado

        salt = base64.b64decode(salt_str)


        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,
        )
        key = kdf.derive(master_password.encode())
        self.aesgcm = AESGCM(key)

    def encrypt(self, plain_text: str) -> str:
        """Cifra y devuelve un string en base64 que incluye el nonce."""
        nonce = secrets.token_bytes(12)  # Nonce estándar para GCM
        ciphertext = self.aesgcm.encrypt(nonce, plain_text.encode(), None)
        # Combinamos nonce + ciphertext y lo pasamos a base64 para SQLite
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_base64: str) -> str:
        """Descifra el string base64 extrayendo el nonce inicial."""
        try:
            data = base64.b64decode(encrypted_base64)
            nonce = data[:12]
            ciphertext = data[12:]
            return self.aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        except Exception:
            return "--- ERROR: NO SE PUDO DESCIFRAR ---"

    def generate_password(self, length=32):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            if sum( c in "!@#$%^&*" for c in password) >= 3:
                return password