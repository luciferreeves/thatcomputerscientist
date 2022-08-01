import cryptocode
import os
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from dotenv import load_dotenv
from six import text_type

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

account_activation_token = AccountActivationTokenGenerator()
