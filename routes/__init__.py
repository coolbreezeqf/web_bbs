import uuid
from functools import wraps

from flask import session, request, abort, redirect, url_for

from models.user import User
from utils import log
from models.store import redis_store


def current_user():
    uid = session.get('user_id', '')
    u = User.one(id=uid)
    return u

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        uid = session.get('user_id', '')
        u = User.one(id=uid)
        if u is None:
            return redirect(url_for('index.login'))
        else:
            return f(*args, **kwargs)

def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        # csrf_tokens = redis_store.get('csrf_tokens') or {}
        # log('csrf_tokens', csrf_tokens, token)
        id = redis_store.hget("tokens", token)
        # if token in csrf_tokens and csrf_tokens == u.id:
        log('redis keys', len(redis_store.hkeys('tokens')), token)
        if int(id) == u.id:
            log('redis del', token)
            redis_store.hdel('tokens', token)
            log('redis tokens len', len(redis_store.hkeys('tokens')))
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    # csrf_tokens = redis_store.get('csrf_tokens') or {}
    # csrf_tokens[token] = u.id
    # redis_store['csrf_tokens'] = csrf_tokens
    redis_store.hset("tokens", token, str(u.id))
    return token
