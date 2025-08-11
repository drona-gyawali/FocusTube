from datetime import datetime, timedelta, timezone

import jwt
from app.config import conf, get_logger
from app.schema import TokenData
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError

logger = get_logger("[/authentication/jwt]")

SECRET_KEY = conf.secret_key
ALGORITHM = conf.algorithm


def create_access_token(user_id: int, expires_delta: timedelta | None = None):
    to_encode = {"sub": str(user_id)}  # sub as string
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user id (sub)",
            )
        return TokenData(user_id=int(user_id))
    except InvalidTokenError:
        logger.error(f"Error: {InvalidTokenError}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
