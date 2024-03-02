from pydantic import BaseModel, Field, EmailStr
from .books import ReturnedBook

__all__ = [ 'RegisterSeller', 'ReturnSeller', 'ReturnAllSellers', 'ReturnSellerBook', 'BaseSeller' ] 


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class RegisterSeller(BaseSeller):
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    email: str = EmailStr
    password: str 


class ReturnSeller(BaseSeller):
    id: int
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    email: str = EmailStr


class ReturnSellerBook(ReturnSeller):
    books: list[ReturnedBook] = Field(None)


class ReturnAllSellers(BaseModel):
    sellers: list[ReturnSeller]

