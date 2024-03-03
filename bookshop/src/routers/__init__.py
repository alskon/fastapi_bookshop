from fastapi import APIRouter
from .v1.books import book_router
from .v1.sellers import seller_router
from .v1.auth import token_router

v1_router = APIRouter(prefix='/api/v1', tags=['v1'])

v1_router.include_router(book_router)
v1_router.include_router(seller_router)
v1_router.include_router(token_router)