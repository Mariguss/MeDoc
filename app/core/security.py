from datetime import datetime, timedelta

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.core.config import settings
from app.core.exception import AuthError
from app.util.date import get_now

ALGORITHM = "HS256"


def create_jwt_token(subject: dict, type_: str | None = "access", expires_delta: timedelta | None = None) -> tuple[str, str]:
    now = get_now()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "exp": int(expire.timestamp()),
        "type": type_,
        **subject,
    }

    encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    expiration_datetime = expire.strftime(settings.DATETIME_FORMAT)

    return encoded_jwt, expiration_datetime

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     try:
#         return bcrypt.checkpw(
#             plain_password.encode('utf-8'),
#             hashed_password.encode('utf-8')
#         )
#     except Exception:
#         return False
#
# def get_password_hash(password: str) -> str:
#     pwd_bytes = password.encode('utf-8')
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(pwd_bytes, salt)
#     return hashed.decode('utf-8')


def decode_jwt(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=ALGORITHM)
        return decoded_token if decoded_token["exp"] >= int(round(datetime.utcnow().timestamp())) else None
    except Exception as e:
        return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        # auto_error=True заставляет FastAPI автоматически выкидывать ошибку, 
        # если клиент вообще забыл прикрепить токен
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):

        # Он идет в заголовки запроса и вытаскивает оттуда строчку "Authorization: Bearer <токен>"
        credentials_: HTTPAuthorizationCredentials | None = await super().__call__(request)

        if credentials_ is not None:
            if credentials_.scheme != "Bearer":
                raise AuthError(detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials_.credentials):
                raise AuthError(detail="Invalid token or expired token.")
            return credentials_.credentials
        else:
            raise AuthError(detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_jwt(jwt_token)
            if payload:
                is_token_valid = True
            return is_token_valid
        except Exception as e:
            print("verify_jwt", e)
            raise AuthError(detail="Invalid authorization code.")
