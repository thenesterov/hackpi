import random
import string

from hackpi.Database import Database
from hackpi.JWT import JWT


class HackPi:
    def __init__(
        self,
        db: Database = Database('sqlite:///database.sqlite3'),
        jwt: JWT = JWT(
            ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        )
    ):
        self.db = db
        self.jwt = jwt
