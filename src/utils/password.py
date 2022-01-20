import hashlib

from config import app_config


def password_hash(password):
    hashed_password = hashlib.sha512(
        password.encode("utf-8") + app_config.SECRET_KEY.encode("utf-8")
    ).hexdigest()
    return hashed_password
