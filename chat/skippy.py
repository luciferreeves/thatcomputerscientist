from .chat_cache import get_user_messages, save_user_messages

def invokeMFSkippy(message, identifier):
    save_user_messages(user_identifier=identifier, message={'content': message, 'role': 'user'})
    user_messages = get_user_messages(user_identifier=identifier)
    if len(user_messages) == 1:
        return "Skippy here. No one's around, you are free to browse around or keep sending messages like a weirdo. Bye."
    else:
        return None
