from cryptography.fernet import Fernet
from django.conf import settings

# Generate a key once and store it securely (use Fernet.generate_key() to generate)
# Add your key to settings.SECRET_ENCRYPTION_KEY
encryption_key = settings.SECRET_ENCRYPTION_KEY
cipher = Fernet(encryption_key)


def encrypt_data(data):
    """Encrypt data using Fernet symmetric encryption."""
    if not data:
        return data
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data):
    """Decrypt data using Fernet symmetric encryption."""
    if not encrypted_data:
        return encrypted_data
    return cipher.decrypt(encrypted_data.encode()).decode()
