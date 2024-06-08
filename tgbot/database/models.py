from sqlalchemy import (BigInteger, Boolean, DateTime, ForeignKey, Integer,
                        String, Text, func)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    on_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    anecdote: Mapped['Anecdote'] = relationship(back_populates='category')

    def __repr__(self) -> str:
        return f'<Category(id={self.id}, Category(name={self.name}))>'


class Anecdote(Base):
    __tablename__ = 'anecdote'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'))

    category: Mapped['Category'] = relationship(back_populates='anecdote')
    users: Mapped['Users'] = relationship(back_populates='anecdote')

    def __repr__(self) -> str:
        return f'<Anecdote(id={self.id})>'


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    gpt_limit: Mapped[int] = mapped_column(Integer, default=0)

    anecdote: Mapped['Anecdote'] = relationship(back_populates='users')

    def __repr__(self) -> str:
        return f'<Users(user={self.username}))>'


class Rate(Base):
    __tablename__ = 'rate'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rate: Mapped[int] = mapped_column(Integer, default=0)
    anecdote_id: Mapped[int] = mapped_column(ForeignKey('anecdote.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f'<Rate(id={self.id})>'
