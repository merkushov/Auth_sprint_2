import hashlib
import random
import string

from config import app_config


def password_hash(password):
    hashed_password = hashlib.sha512(
        password.encode("utf-8") + app_config.secret_key.encode("utf-8")
    ).hexdigest()
    return hashed_password


def random_password():
    alphabet = string.digits + string.ascii_letters
    password = ''.join(random.choice(alphabet) for _ in range(20))
    return password
