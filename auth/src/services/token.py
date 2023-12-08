from datetime import datetime, timedelta
from functools import lru_cache
from http import HTTPStatus

import jwt
from fastapi import Depends, HTTPException

from src.core.config import FastApiConf, get_config


class TokenService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def encode_jwt(self, user_id: str, expires_delta: timedelta = timedelta(minutes=5), **kwargs):

        if expires_delta is None:
            expires_delta = timedelta(minutes=5)

        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": user_id,
            "exp": expire,
            **kwargs
        }
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return encoded_jwt

    def decode_jwt(self, token: str):
        try:
            decoded_jwt = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return decoded_jwt
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )


@lru_cache()
def get_token_service(config: FastApiConf = Depends(get_config)) -> TokenService:
    return TokenService(config.secret_key)
