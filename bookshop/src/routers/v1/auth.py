from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from typing import Annotated
import icecream as ic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.sellers import Seller
from configurations.database import get_async_session
from auth.auth_token import verify_password, create_token, get_auth_seller


token_router = APIRouter(prefix='/token', tags=['token'])
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@token_router.post('/', status_code=status.HTTP_201_CREATED)
async def gen_token(
    session: DBSession,
    auth_seller: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
    query = select(Seller).where(Seller.email == auth_seller.username)
    res = await session.execute(query)
    found_seller = res.scalars().first()

    if not found_seller:
        return Response('Seller not found', status_code=status.HTTP_401_UNAUTHORIZED)

    if not verify_password(auth_seller.password, found_seller.password):
        return Response('Password not correct', status_code=status.HTTP_401_UNAUTHORIZED)
    
    jwt_token = create_token({
        'email': found_seller.email,
        'token_type': 'bearer'
        })
    print(get_auth_seller(jwt_token))
    return jwt_token
