import pytest
from copy import copy
from fastapi import status
from sqlalchemy import select

from .examples_data import test_sellers, test_books, tokens

from models import sellers, books


# Тест на ручку регистрации продавца
@pytest.mark.asyncio
async def test_register_seller(async_client):
    test_seller = copy(test_sellers['seller_1'])

    response = await async_client.post('/api/v1/sellers/', json=test_seller)
    assert response.status_code == status.HTTP_201_CREATED
    result_data = response.json()
    assert result_data == {
        'first_name': 'Alex',
        'last_name': 'Ivanov',
        'email': 'alex_iv@mail.ru',
        'id': 1
        }

# Тест на ручку получения всех продавцов
@pytest.mark.asyncio
async def test_get_all_sellers(db_session, async_client):
    #Создаем записи в БД
    test_seller_1 = copy(test_sellers['seller_1'])
    test_seller_2 = copy(test_sellers['seller_2'])
    test_seller_3 = copy(test_sellers['seller_3'])
    seller_1 = sellers.Seller(**test_seller_1)
    seller_2 = sellers.Seller(**test_seller_2)
    seller_3 = sellers.Seller(**test_seller_3)

    db_session.add_all([seller_1, seller_2, seller_3]) 
    await db_session.flush() 

    response = await async_client.get('/api/v1/sellers/')
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['sellers']) == 3
    assert response.json() == {
        'sellers': [
            {'id': 1, 'first_name': 'Alex', 'last_name': 'Ivanov', 'email': 'alex_iv@mail.ru'},
            {'id': 2, 'first_name': 'John', 'last_name': 'Petrov', 'email': 'dj_pet@gmail.com'},
            {'id': 3, 'first_name': 'Ivan', 'last_name': 'Jones', 'email': 'ivan_jon@mail.ru'}
        ]
    }

# Тест на ручку получения одного конкретного продавца
@pytest.mark.asyncio
async def test_get_seller(db_session, async_client):
    #Создаем записи в БД
    #Добавляем Продавцов
    test_seller_1 = copy(test_sellers['seller_1'])
    test_seller_2 = copy(test_sellers['seller_2'])
    test_seller_3 = copy(test_sellers['seller_3'])
    seller_1 = sellers.Seller(**test_seller_1)
    seller_2 = sellers.Seller(**test_seller_2)
    seller_3 = sellers.Seller(**test_seller_3)
    db_session.add_all([seller_1, seller_2, seller_3]) 
    await db_session.flush() 
    seller_db = {}
    for i, email in zip(range(1, 4), [ test_seller_1['email'], test_seller_2['email'], test_seller_3['email'] ]):
        query = select(sellers.Seller).where(sellers.Seller.email == email)
        seller_db[f'seller_db_{i}'] = await db_session.scalar(query)

    db_session.add_all([seller_1, seller_2, seller_3]) 
    await db_session.flush() 
    #Добавляем Книги
    test_book_1 = copy(test_books['book_1'])
    test_book_2 = copy(test_books['book_2'])
    test_book_3 = copy(test_books['book_3'])
    test_book_1['seller_id'] = seller_db['seller_db_1'].id
    test_book_2['seller_id'] = seller_db['seller_db_1'].id
    test_book_3['seller_id'] = seller_db['seller_db_2'].id
    book_1 = books.Book(**test_book_1)
    book_2 = books.Book(**test_book_2)
    book_3 = books.Book(**test_book_3)
    db_session.add_all([book_1, book_2, book_3]) 

    await db_session.flush()

    headers = {
          'Authorization': 
          f"Bearer {tokens['seller_1']}"
    }

    response = await async_client.get(f"/api/v1/sellers/{seller_1.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа
    assert response.json() == {
        'id': 1,
        'first_name': 'Alex', 
        'last_name': 'Ivanov', 
        'email': 'alex_iv@mail.ru',
        'books': [
            {
                'title': 'Eugeny Onegin', 
                'author': 'Pushkin', 
                'year': 2001, 
                'count_pages': 104,
                'id': 1
            },
            {
                'title': 'Mziri', 
                'author': 'Lermontov', 
                'year': 1997, 
                'count_pages': 104,
                'id': 2
            }   
        ]
    }


# Тест на ручку удаления Продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    #Создаем записи в БД
    test_seller = copy(test_sellers['seller_1'])
    seller = sellers.Seller(**test_seller)
    db_session.add(seller) 
    await db_session.flush()
    query = select(sellers.Seller).where(sellers.Seller.email == test_seller['email'])
    seller_db = await db_session.scalar(query)
    #Добавляем Книги
    test_book_1 = copy(test_books['book_1'])
    test_book_2 = copy(test_books['book_2'])
    test_book_1['seller_id'] = seller_db.id
    test_book_2['seller_id'] = seller_db.id
    book_1 = books.Book(**test_book_1)
    book_2 = books.Book(**test_book_2)
    db_session.add_all([ book_1, book_2 ]) 

    await db_session.flush()
    response = await async_client.delete(f"/api/v1/sellers/{seller_db.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    all_sellers = await db_session.execute(select(sellers.Seller))
    res_books = all_books.scalars().all()
    assert len(res_books) == 0
    res_sellers = all_sellers.scalars().all()
    assert len(res_sellers) == 0

# Тест на ручку обновления даных о продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    #Создаем записи в БД
    test_seller = copy(test_sellers['seller_1'])
    seller = sellers.Seller(**test_seller)

    db_session.add(seller) 
    await db_session.flush()

    query = select(sellers.Seller).where(sellers.Seller.email == test_seller['email'])
    seller_db = await db_session.scalar(query)

    response = await async_client.put(
        f"/api/v1/sellers/{seller_db.id}",
        json={'first_name': 'Alex', 'last_name': 'Sergeev', 'email': 'alex_iv@mail.ru'},
    )

    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller_db.id)
    assert res.first_name == "Alex"
    assert res.last_name == "Sergeev"
    assert res.email == 'alex_iv@mail.ru'