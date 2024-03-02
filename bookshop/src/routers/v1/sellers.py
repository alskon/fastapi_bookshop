from fastapi import APIRouter

from typing import Annotated
import bcrypt

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configurations.database import get_async_session
from models.sellers import Seller
from schemas import RegisterSeller, ReturnSeller, ReturnAllSellers, ReturnSellerBook, BaseSeller
from auth.auth_token import get_auth_seller


seller_router = APIRouter(prefix='/sellers', tags=['sellers'])
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@seller_router.get('/', response_model=ReturnAllSellers)
async def get_all_sellers(
    session: DBSession
):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {'sellers': sellers}

@seller_router.get('/{seller_id}', response_model=ReturnSellerBook)
async def get_seller(
    seller_id: int, 
    session: DBSession,
    auth_seller: ReturnSeller = Depends(get_auth_seller)
    ):
    query = select(Seller).where(Seller.id == seller_id)
    seller = await session.scalar(query)
    if seller:
        await seller.awaitable_attrs.books
        return seller
    return Response(status_code=status.HTTP_404_NOT_FOUND)

@seller_router.post('/', response_model=ReturnSeller, status_code=status.HTTP_201_CREATED)
async def register_seller(
    seller:RegisterSeller, session: DBSession):
    seller.password = str(bcrypt.hashpw(seller.password.encode(), bcrypt.gensalt()), encoding='utf-8')
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password
    )
    session.add(new_seller)
    await session.flush()
    return new_seller
    
@seller_router.delete('/{seller_id}')
async def delete_seller(
    seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@seller_router.put('/{seller_id}', response_model=ReturnSeller)
async def put_seller(
    seller_id: int, new_data: BaseSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email
        await session.flush()
        return updated_seller
    return Response(status_code=status.HTTP_404_NOT_FOUND)


