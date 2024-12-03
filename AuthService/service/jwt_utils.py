import jwt
from datetime import datetime, timedelta
from django.conf import settings

# Use your secret key and token lifetime from settings
SECRET_KEY = settings.SECRET_KEY
TOKEN_LIFE_TIME = settings.TOKEN_LIFE_TIME
ALGORITHM = "HS256"


def generate_jwt(payload):
    """
    Generate a JWT with the given payload and expiration time.
    """
    payload['exp'] = datetime.utcnow() + timedelta(minutes=TOKEN_LIFE_TIME)
    payload['iat'] = datetime.utcnow()
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_jwt(token):
    """
    Decode a JWT and return the payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired.")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token.")
