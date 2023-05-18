
import redis
from .chat_cache import get_user_messages, save_user_messages

r = redis.Redis(host='localhost', port=6379, db=0)
subsequent_message = "I told you, no one's around. Stop talking to yourself, you weirdo!"

def invokeMFSkippy(message, identifier):
    save_user_messages(user_identifier=identifier, message={'content': message, 'role': 'user'})
    user_messages = get_user_messages(user_identifier=identifier)
    if len(user_messages) == 1:
        return "Skippy here. No one's around, you lonely rat!"
    elif len(user_messages) == 2:
        return  "I told you, no one's around. Stop talking to yourself, you weirdo!"
    elif len(user_messages) == 3:
        return "I'm not going to respond to you anymore. Not only are you a weirdo, you're also relentlesslly annoying."
    else:
        return None