import json

import redis

import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
  host=os.getenv('REDIS_HOST'),
  port=os.getenv('REDIS_PORT'),
  password=os.getenv('REDIS_PASSWORD'),
  db=0
)

def handle_connect():
    # increase number of connected users
    r.set('n_connected_lc_users', max(1, int(r.get('n_connected_lc_users')) + 1))
    print('There are now {} connected users.'.format(r.get('n_connected_lc_users')))

def handle_disconnect():
    # decrease number of connected users
    r.set('n_connected_lc_users', max(0, int(r.get('n_connected_lc_users')) - 1))
    print('There are now {} connected users.'.format(r.get('n_connected_lc_users')))

def handle_alone_user():
    if int(r.get('n_connected_lc_users')) == 1:
        return True
    else:
        return False
    
def save_user_messages(user_identifier, message):
    # get user_messages from redis
    user_messages = r.get(user_identifier)
    if user_messages:
        user_messages = json.loads(user_messages)
    else:
        user_messages = []
    # append new message
    user_messages.append(message)
    # save user_messages to redis
    r.set(user_identifier, json.dumps(user_messages))

def get_user_messages(user_identifier):
    # get user_messages from redis
    user_messages = r.get(user_identifier)
    if user_messages:
        return json.loads(user_messages)
    else:
        return []

def discard_user_messages(user_identifier):
    r.delete(user_identifier)