from fastapi import APIRouter, Depends
from pydantic import BaseModel

from hackpi.Database import Base, Database


class Router:
    def __init__(self, database: Database, model: Base, schema: BaseModel):
        self.__database = database
        self.__model = model
        self.__schema = schema

        self.__router = APIRouter(prefix=f'/{self.__model.__name__.lower()}', tags=[self.__model.__name__.lower()])

    def get_router(self):
        @self.__router.get(f'/{self.__model.__name__.lower()}')
        def get_records(session=Depends(self.__database.get_session)):
            return session.query(self.__model).all()

        @self.__router.get(f'/{self.__model.__name__.lower()}/' + 'id')
        def get_record(id: int, session=Depends(self.__database.get_session)):
            return session.query(self.__model).filter(self.__model.id == id).one()

        @self.__router.post(f'/{self.__model.__name__.lower()}')
        def set_record(schema: self.__schema, session=Depends(self.__database.get_session)):
            session.add(self.__model(
                **schema.__dict__
            ))
            session.commit()
            return 201

        @self.__router.put(f'/{self.__model.__name__.lower()}/' + 'id')
        def update_record(id: int, schema: self.__schema, session=Depends(self.__database.get_session)):
            session.query(self.__model).filter(self.__model.id == id).update(
                schema.__dict__
            )
            session.commit()
            return 200

        @self.__router.delete(f'/{self.__model.__name__.lower()}/' + 'id')
        def delete_record(id: int, session=Depends(self.__database.get_session)):
            session.query(self.__model).filter(self.__model.id == id).delete()
            session.commit()
            return 200

        return self.__router
