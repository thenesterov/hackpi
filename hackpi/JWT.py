import datetime
from typing import Dict

from jose import jwt, JWTError


class JWT:
    def __init__(self, secret: str):
        self.__secret = secret

    def create(self, payload: Dict[str, str | datetime.datetime]) -> str:
        payload['exp'] = datetime.datetime.now() + datetime.timedelta(minutes=5)
        return jwt.encode(payload, self.__secret, algorithm='HS256')

    def verify(self, token: str) -> bool:
        try:
            return True if jwt.decode(token, self.__secret, algorithms=['HS256']) else False
        except JWTError:
            return False

    def parse(self, token: str) -> dict:
        return jwt.decode(token, self.__secret, algorithms=['HS256'])
