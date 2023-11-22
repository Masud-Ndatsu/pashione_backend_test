from Library.settings import JWT_SECRET_KEY
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
import jwt, datetime
from LibraryAPI.models import User

def generate_token(user):
    payload = {
    "user_id": user.id,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
    "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        if isinstance(payload, dict) and "user_id" in payload:
            user_id = payload["user_id"]
            user = User.objects.filter(id=user_id).first()
            if user:
                user_data = {
                    "id": user.id,
                }
            else:
                return "User not found"
        return user_data
    except jwt.ExpiredSignatureError:
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in.'

