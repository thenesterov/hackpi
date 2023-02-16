from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from hackpi.HackPi import HackPi
from hackpi.Methods import Methods
from hackpi.Database import Base

# move it to new file
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Router:
    def __init__(self, hp: HackPi, model: Base, schema: BaseModel, roles: dict[str, list[str]] = {}):
        self.__database = hp.db
        self.__model = model
        self.__schema = schema
        self.__jwt = hp.db
        self.__roles = roles

        self.__router = APIRouter(prefix=f'/{self.__model.__name__.lower()}', tags=[self.__model.__name__.lower()])

    # use some pattern to get out of big code
    def get_router(self):
        if self.__roles.get(Methods.GET):
            @self.__router.get(f'/{self.__model.__name__.lower()}')
            def get_records(session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if self.__jwt.parse(token).get('role') in self.__roles[Methods.GET]:
                    return session.query(self.__model).all()
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

            @self.__router.get(f'/{self.__model.__name__.lower()}/' + 'id')
            def get_record(id: int, session=Depends(self.__database.get_session)):
                return session.query(self.__model).filter(self.__model.id == id).one()

        if self.__roles.get(Methods.POST):
            @self.__router.post(f'/{self.__model.__name__.lower()}')
            def set_record(schema: self.__schema, session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if self.__jwt.parse(token).get('role') in self.__roles[Methods.POST]:
                    session.add(self.__model(
                        **schema.__dict__
                    ))
                    session.commit()
                    return 201
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

        if self.__roles.get(Methods.PUT):
            @self.__router.put(f'/{self.__model.__name__.lower()}/' + 'id')
            def update_record(id: int, schema: self.__schema, session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if self.__jwt.parse(token).get('role') in self.__roles[Methods.PUT]:
                    session.query(self.__model).filter(self.__model.id == id).update(
                        schema.__dict__
                    )
                    session.commit()
                    return 200
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

        if self.__roles.get(Methods.DELETE):
            @self.__router.delete(f'/{self.__model.__name__.lower()}/' + 'id')
            def delete_record(id: int, session=Depends(self.__database.get_session), token: str = Depends(oauth2_scheme)):
                if self.__jwt.parse(token).get('role') in self.__roles[Methods.DELETE]:
                    session.query(self.__model).filter(self.__model.id == id).delete()
                    session.commit()
                    return 200
                else:
                    return HTTPException(status_code=401, detail='Not permitted')

            return self.__router
