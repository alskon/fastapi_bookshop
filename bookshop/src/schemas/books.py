from pydantic import BaseModel, Field, field_validator, ValidationError

__all__ = [ 'IncomingBook', 'ReturnedBook', 'ReturnedAllBooks', 'ReturnedBookId' ]


class BaseBook(BaseModel):
    title: str
    author: str
    year: int
    seller_id: int


class IncomingBook(BaseBook):
    year: int = 2024
    count_pages: int = Field(
        default=300
    )

    @field_validator('year')
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise ValidationError('Validation Error', 'Year is wrong!')
        return val
    

class ReturnedBook(BaseBook):
    id: int
    count_pages: int
    seller_id: int = Field(exclude=True) 

class ReturnedBookId(ReturnedBook):
    id: int
    seller_id: int


class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBookId]