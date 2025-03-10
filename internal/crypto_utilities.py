import os
from cryptography.fernet import Fernet
import base64

AUTHORIZATION_STRING = os.getenv("AUTHORIZATION_STRING")
SECRET_KEY = base64.urlsafe_b64encode(AUTHORIZATION_STRING[:32].encode())

cipher = Fernet(SECRET_KEY)


def encode_url(url):
    return cipher.encrypt(url.encode()).decode()


def decode_url(encrypted_url):
    return cipher.decrypt(encrypted_url.encode()).decode()
