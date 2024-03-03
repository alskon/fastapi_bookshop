from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from routers import v1_router
from contextlib import asynccontextmanager

from configurations.database import create_db_and_tables, delete_db_and_tables, global_init

@asynccontextmanager
async def lifespan(app: FastAPI):  # Рекомендуется теперь вместо @app.on_event()
    # Запускается при старте приложения
    global_init()
    await create_db_and_tables()
    yield
    # Запускается при остановке приложения
    await delete_db_and_tables()

def create_application():
    return FastAPI(
        title='Bookshop App',
        description='Учебное приложение для группы MTS Shad',
        version='0.0.1',
        responses={404: {'description': 'Not Found'}},
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

def _configure():
    app.include_router(v1_router)

app = create_application()

_configure()
