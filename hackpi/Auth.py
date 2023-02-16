from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from starlette.responses import JSONResponse

from hackpi.HackPi import HackPi
from hackpi.Database import Base
from hackpi.Methods import Methods
from hackpi.Roles import StandartRoles

# move it to new file
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AbstractUser:
    id = Column(Integer, primary_key=True)
    role = Column(String, default=StandartRoles.USER)


class UserModel(Base, AbstractUser):
    __tablename__ = 'users'

    username = Column(String, unique=True)
    password = Column(String)


class UserSchema(BaseModel):
    username: str
    password: str


class Auth:
    def __init__(self, hp: HackPi, model: Base = UserModel, schema: BaseModel = UserSchema, roles: dict[str, list[str]] = {}):
        self.__database = hp.db
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

            return hp.jwt.create({'username': user.username, 'role': StandartRoles.USER})

        @self.__router.post('/sign-in')
        def sign_in(user: self.__schema, session=Depends(self.__database.get_session)):
            row = session.query(self.__model).filter(self.__model.username == user.username).one()

            if row.password == user.password:
                return hp.jwt.create({'username': user.username, 'role': row.role})
            else:
                return HTTPException(status_code=401, detail='Invalid credentials.')

        if roles.get(Methods.GET):
            @self.__router.get('/get-users')
            def get_users(session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if hp.jwt.parse(token).get('role') in roles[Methods.GET]:
                    return session.query(self.__model).all()
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

            @self.__router.get('/get-user-by-id')
            def get_user_by_id(id: int, session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if hp.jwt.parse(token).get('role') in roles[Methods.GET]:
                    # check if id is exist
                    return session.query(self.__model).filter(self.__model.id == id).one()
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

        if roles.get(Methods.PUT):
            @self.__router.put('/userinfo-update')
            def userinfo_update(id: int, userinfo: self.__schema, session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if hp.jwt.parse(token).get('role') in roles[Methods.PUT]:
                    session.query(self.__model).filter(self.__model.id == id).update(userinfo.__dict__)
                    session.commit()

                    return JSONResponse(content={'message': 'The user has been updated'}, status_code=204)
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

        if roles.get(Methods.DELETE):
            @self.__router.delete('/user-delete')
            def user_delete(id: int, session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if hp.jwt.parse(token).get('role') in roles[Methods.DELETE]:
                    session.query(self.__model).filter(self.__model.id == id).delete()
                    session.commit()

                    return JSONResponse(content={'message': 'The user has been deleted'}, status_code=200)
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

    def __call__(self):
        return self.__router
