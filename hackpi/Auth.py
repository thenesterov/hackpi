from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from hackpi import Database
from hackpi.Database import Base
from hackpi.JWT import JWT

class AbstractUser:
    id = Column(Integer, primary_key=True)

class UserModel(Base, AbstractUser):
    __tablename__ = 'users'

    username = Column(String, unique=True)
    password = Column(String)


class UserSchema(BaseModel):
    username: str
    password: str


class Auth:
    def __init__(self, database: Database, jwt: JWT, model: Base = UserModel, schema: BaseModel = UserSchema):
        self.__database = database
        self.__model = model
        self.__schema = schema

        self.__router = APIRouter(prefix='/auth', tags=['auth'])

        self.__database.create_all()

        @self.__router.post('/sign-up')
        def sign_up(user: self.__schema, session=Depends(self.__database.get_session)):
            # check if user is exist
            session.add(self.__model(
                **user.__dict__  # TODO: add hash
            ))
            session.commit()

            return jwt.create({'username': user.username})

        @self.__router.post('/sign-in')
        def sign_in(user: self.__schema, session=Depends(self.__database.get_session)):
            row = session.query(self.__model).filter(self.__model.username == user.username).one()

            if row.password == user.password:
                return jwt.create({'username': user.username})
            else:
                return HTTPException(status_code=401, detail='Invalid credentials.')

        @self.__router.get('/get_users')
        def get_users(session=Depends(self.__database.get_session)):
            return session.query(self.__model).all()

        @self.__router.get('get_user_by_id')
        def get_user_by_id(id: int, session=Depends(self.__database.get_session)):
            # check if id is exist
            return session.query(self.__model).filter(self.__model.id == id).one()

        # Update userinfo
        # Delete user

    def __call__(self):
        return self.__router
