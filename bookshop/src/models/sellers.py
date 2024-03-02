from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship



from .base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement = True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    books: Mapped[list["Book"]] = relationship("Book", back_populates="sellers", cascade="all, delete", passive_deletes=True)

