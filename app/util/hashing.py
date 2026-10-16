import bcrypt
from loguru import logger


def get_password_hash(password: str) -> str:
    password_bytes: bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool | None:
    try:
        return bool(
            bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        )
    except TypeError as e:
        logger.exception(f"Ошибка в функции verify_password (TypeError): {e}")
        raise
    except ValueError as e:
        logger.exception(f"Ошибка в функции verify_password (ValueError): {e}")
        raise
