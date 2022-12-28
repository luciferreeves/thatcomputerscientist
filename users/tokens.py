import cryptocode
import os
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from dotenv import load_dotenv
from six import text_type
from Crypto.Cipher import AES

load_dotenv()

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.is_active)
        )

class EmailChangeTokenGenerator():
    def encrypt(self, email):
        auth_string = os.getenv('AUTHORIZATION_STRING')
        return cryptocode.encrypt(email, auth_string)
    
    def decrypt(self, token):
        auth_string = os.getenv('AUTHORIZATION_STRING')
        return cryptocode.decrypt(token, auth_string)

class CaptchaTokenGenerator():
    def encrypt(self, captcha_string):
        auth_string = os.getenv('AUTHORIZATION_STRING')
        key = auth_string.encode('utf-8')[0:16]
        cipher = AES.new(key, AES.MODE_CFB, key)
        return cipher.encrypt(captcha_string.encode('utf-8')).hex()

    def decrypt(self, token):
        auth_string = os.getenv('AUTHORIZATION_STRING')
        key = auth_string.encode('utf-8')[0:16]
        cipher = AES.new(key, AES.MODE_CFB, key)
        return cipher.decrypt(bytes.fromhex(token)).decode('utf-8')

account_activation_token = AccountActivationTokenGenerator()
