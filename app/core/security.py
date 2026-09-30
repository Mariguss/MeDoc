from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from starlette import status

from app.core.config import settings
from app.core.exception import AuthError
from app.util.date import get_now

ALGORITHM = "HS256"


def create_jwt_token(subject: dict, type_: str | None = "access", expires_delta: timedelta | None = None) -> tuple[str, str]:
    now = get_now()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(seconds=settings.token.access_token_expire_seconds)

    payload = {
        "exp": int(expire.timestamp()),
        "type": type_,
        **subject,
    }

    encoded_jwt = jwt.encode(payload, settings.token.secret_key, algorithm=ALGORITHM)
    expiration_datetime = expire.strftime(settings.token.DATETIME_FORMAT)

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
        decoded_token = jwt.decode(token, settings.token.secret_key, algorithms=ALGORITHM)
        print("decoded_token['exp']" ,decoded_token["exp"])
        return decoded_token if decoded_token["exp"] >= int(round(datetime.utcnow().timestamp())) else None
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек, пожалуйста, авторизуйтесь заново.",
        )
    except jwt.exceptions.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен авторизации.",
        )
    except Exception as e:
        print("decode_jwt", e)
        raise e


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        # auto_error=True заставляет FastAPI автоматически выкидывать ошибку, 
        # если клиент вообще забыл прикрепить токен
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict | None:
        # Он идет в заголовки запроса и вытаскивает оттуда строчку "Authorization: Bearer <токен>"
        credentials_: HTTPAuthorizationCredentials | None = await super().__call__(request)

        if credentials_ is not None:
            if credentials_.scheme != "Bearer":
                raise AuthError(detail="Invalid authentication scheme.")
            payload = self.verify_jwt(credentials_.credentials)
            if payload.get("type") != "access":
                raise AuthError(detail="Invalid token type.")
            return payload
        else:
            raise AuthError(detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str) -> dict:
        try:
            payload = decode_jwt(jwt_token)
            if payload:
                return payload
            raise AuthError(detail="Invalid token or expired token.")
        except Exception as e:
            print("verify_jwt", e)
            raise AuthError(detail="Invalid authorization code.")
