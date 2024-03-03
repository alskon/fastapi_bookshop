import pytest
from copy import copy
from fastapi import status
from sqlalchemy import select

from models import books, sellers, base

from .examples_data import test_sellers, test_books, tokens



# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    test_seller = copy(test_sellers['seller_1'])
    seller = sellers.Seller(**test_seller)
    headers = {
          'Authorization': 
          f"Bearer {tokens['seller_1']}"
    }
    db_session.add(seller) 
    await db_session.flush() 
    data = copy(test_books['book_1'])
    data['seller_id'] = seller.id
    response = await async_client.post("/api/v1/books/", json=data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        'id': 1,
        'title': 'Eugeny Onegin', 
        'author': 'Pushkin', 
        'year': 2001, 
        'count_pages': 104,
        'seller_id': 1
    }


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    test_seller = copy(test_sellers['seller_2'])
    seller = sellers.Seller(**test_seller)
    db_session.add(seller) 
    await db_session.flush()
    query = select(sellers.Seller).where(sellers.Seller.email == test_seller['email'])
    seller_db = await db_session.scalar(query)

    test_book_1, test_book_2 = copy(test_books['book_1']), copy(test_books['book_2'])
    test_book_1['seller_id'], test_book_2['seller_id'] = seller_db.id, seller_db.id
    book_1 = books.Book(**test_book_1)
    book_2 = books.Book(**test_book_2)
    headers = {
          'Authorization': 
          f"Bearer {tokens['seller_1']}"
    }

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        'books': [
            {       
                'id': 1, 
                'title': 'Eugeny Onegin', 
                'author': 'Pushkin', 
                'year': 2001, 
                'count_pages': 104,
                'seller_id': 1
            },
            
            {        
                'id': 2,
                'title': 'Mziri', 
                'author': 'Lermontov', 
                'year': 1997, 
                'count_pages': 104,
                'seller_id': 1
            }
        ]
    }
    
#Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    test_seller = copy(test_sellers['seller_2'])
    seller = sellers.Seller(**test_seller)
    db_session.add(seller) 
    await db_session.flush()
    query = select(sellers.Seller).where(sellers.Seller.email == test_seller['email'])
    seller_db = await db_session.scalar(query)

    test_book_1, test_book_2 = copy(test_books['book_1']), copy(test_books['book_2'])
    test_book_1['seller_id'], test_book_2['seller_id'] = seller_db.id, seller_db.id
    book_1 = books.Book(**test_book_1)
    book_2 = books.Book(**test_book_2)
    db_session.add_all([book_1, book_2])
    await db_session.flush()

    headers = {
          'Authorization': 
          f"Bearer {tokens['seller_1']}"
    }

    response = await async_client.get(f"/api/v1/books/{book_1.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
            'id': 1, 
            'title': 'Eugeny Onegin', 
            'author': 'Pushkin', 
            'year': 2001, 
            'count_pages': 104,
            'seller_id': 1
        }

# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    test_seller = copy(test_sellers['seller_3'])
    seller = sellers.Seller(**test_seller)
    db_session.add(seller) 
    await db_session.flush()
    query = select(sellers.Seller).where(sellers.Seller.email == test_seller['email'])
    seller_db = await db_session.scalar(query)

    test_book_1 = copy(test_books['book_1'])
    test_book_1['seller_id']= seller_db.id
    book_1 = books.Book(**test_book_1)
    db_session.add(book_1)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book_1.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    test_seller = copy(test_sellers['seller_3'])
    seller = sellers.Seller(**test_seller)
    db_session.add(seller) 
    await db_session.flush()
    query = select(sellers.Seller).where(sellers.Seller.email == test_seller['email'])
    seller_db = await db_session.scalar(query)

    test_book = copy(test_books['book_2'])
    test_book['seller_id']= seller_db.id
    book = books.Book(**test_book)

    db_session.add(book)
    await db_session.flush()

    headers = {
          'Authorization': 
          f"Bearer {tokens['seller_1']}"
    }

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={'title': 'Mziri', 'author': 'Lermontov', 'count_pages': 400, 'year': 2007, 'id': book.id, 'seller_id': 1},
        headers=headers
        )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books.Book, book.id)
    assert res.id == 1
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 400
    assert res.year == 2007
    assert res.seller_id == 1