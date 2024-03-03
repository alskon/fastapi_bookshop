from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class BaseModel(DeclarativeBase, AsyncAttrs):
    pass