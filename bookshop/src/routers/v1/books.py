from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configurations.database import get_async_session
from models.books import Book
from models.sellers import Seller
from schemas import IncomingBook, ReturnedAllBooks, ReturnedBookId, ReturnSeller
from auth.auth_token import get_auth_seller 

book_router = APIRouter(prefix='/books', tags=['books'])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@book_router.get('/', response_model=ReturnedAllBooks)
async def get_books(
    session: DBSession
    ):
    query = select(Book)
    res = await session.execute(query)
    books = res.scalars().all()
    return {'books': books}

@book_router.get('/{book_id}', response_model=ReturnedBookId)
async def get_book(book_id: int, session: DBSession):
    res = await session.get(Book, book_id)
    return res

@book_router.post('/', response_model=ReturnedBookId, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: IncomingBook, 
    session: DBSession,
    auth_seller: ReturnSeller = Depends(get_auth_seller)
    ):
    #Поиск id продавца в базе, если отсутствует, то данные не зааписываем в БД 
    db_seller = await session.get(Seller, book.seller_id) 
    if not db_seller:
        Response('Seller not found', status_code=status.HTTP_404_NOT_FOUND)
    if db_seller:
        new_book = Book(
            title=book.title,
            author=book.author,
            year=book.year,
            count_pages=book.count_pages,
            seller_id=book.seller_id
        )
    

    session.add(new_book)
    await session.flush()
    return new_book

@book_router.delete('/{book_id}', status_code=status.HTTP_201_CREATED)
async def delete_book(
    book_id: int, session: DBSession
    ):
    deleted_book = await session.get(Book, book_id)
    ic(deleted_book)
    if deleted_book:
        await session.delete(deleted_book)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
@book_router.put('/{book_id}')
async def put_book(
    book_id: int, 
    new_data: ReturnedBookId, 
    session:DBSession,
    auth_seller: ReturnSeller = Depends(get_auth_seller)
    ):
    
    updated_book = await session.get(Book, book_id)
    
    if updated_book and new_data.seller_id == updated_book.seller_id:
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages
        await session.flush()
        return updated_book
    return Response(status_code=status.HTTP_404_NOT_FOUND)
