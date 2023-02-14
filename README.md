# HackPi
![logotype](docs/logo.svg)

HackPi - is a library for the FastAPI framework that adds additional functionality that simplifies development. 

## Introduction
### Features:
- Генерация endpoints по моделям SQLAlchemy и Pydantic
- Готовые методы регистрации, авторизации
- Система ролей с возможностью ограничения доступа

Библиотека может использоваться для быстрого прототипирования бекенда, либо для построения функционала для хакатонов.

### Installing
Чтобы установить библиотеку, выполните в терминале простую команду:
```bash
pip3 install hackpi
```

Чтобы проверить наличие библиотеки на компьютере, нужно ввести следующую команду:
```bash
pip3 list
```
И в выведенном вы увидите библиотеку hackpi с текущей версией (актуальная - 0.1.1).

Ура! Теперь вы можете пользоваться всеми возможностями HackPi.

## Usage
## Подключение к базе данных
Для подключения к базе данных используется класс `Database`. При содании объекта этого класса, нужно передать в конструктор расположение SQLite3 базы данных. Пока что HackPi может работать только с этой базой данных.
```python
# db.py
from hackpi.Database import Database

db = Database('sqlite:///database.sqlite3')
```

В последствии, мы можем передавать объект `db` в другие методы, которые будут записывать информацию в базу данных.

## Модели SQLAlchemy и Pydantic
В этом туториале вы увидите работу библиотеки на примере работы с пользователем. Нам всегда необходимо иметь две модели: модель SQLAlchemy и модель Pydantic. 

```python
# models.py
from hackpi.Database import Base
from sqlalchemy import Column, Integer, String
from db import db

class User(Base):
	__tablename__ = 'users'

	id: int = Column(Integer, primary_key=True)
	email: str = Column(String, unique=True)
	password: str = Column(String)

db.create_all()
```

Разберем файл `models.py`. Мы создали модель SQLAlchemy, наследовав ее от `Base`. Название таблицы - `users`. Таблица имеет следующие столбцы: `id`, `email`, `password`. Затем, мы вызвали метод для создания таблицы в базе данных.

```python
# schemas.py
from pydantic import BaseModel

class User(BaseModel):
	email: str
	password: str
```

Мы создали простую схему Pydantic, которая содержит в себе только `email` и `password`.

## Создание роутеров
Итак, чтобы сгенерировать эндпоинты, используя модели SQLAlchemy и Pydantic, необходимо создать `main.py` файл, и написать в нем следующее:
```python
# main.py
from fastapi import FastAPI
from hackpi.Router import Router
from models import User as UserModel
from schemas import User as UserSchema
from db import db

app = FastAPI()

router = Router(db, UserModel, UserSchema)

app.include_router(router.get_router())
```

## Регистрация и авторизация
Если вы хотите добавить в свое приложение регистрацию и авторизацию, для этого существует класс `Auth`. Введите следующий код, чтобы добавить это в свое приложение:
```python
# main.py
from fastapi import FastAPI
from hackpi.Auth import Auth
from hackpi.JWT import JWT
from db import db

app = FastAPI()

jwt = JWT('secret')

app.include_router(Auth(db, jwt)())
```

Это добавит следующие эндпоинты:
- `/sign-up`
- `/sign-in`
- `/get-users`
- `/get-user-by-id`
- `/userinfo-update`
- `/user-delete`

## Ролевая система
Чтобы к некоторым эндпоинтам доступ могло иметь только ограниченное количество пользователей, можно добавить ролевую систему:
```python
# main.py
from fastapi import FastAPI
from hackpi.Router import Router
from hackpi.JWT import JWT
from hackpi.Methods import Methods
from hackpi.Roles import StandartRoles
from models import User as UserModel
from schemas import User as UserSchema
from db import db

app = FastAPI()

jwt = JWT('secret')

router = Router(db, UserModel, UserSchema, jwt, {
    Methods.GET: [StandartRoles.MODER]
})

app.include_router(router.get_router())
```

Введя команду `uvicorn main:app --reload` в терминал, запустится бекенд. Можно перейти в документацию, и увидеть результат генерации эндпоинтов.

⚠️ Библиотека не является полностью безопасной и не должна быть использована на реальных продакшен решениях!