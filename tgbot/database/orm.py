from random import choice
from typing import List, Tuple

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Anecdote, Category, Rate, Users

CURRENT_LIMITLESS = ('anakinnikita', 'bogdaliz', 'denisiiss', 'vovans23')

#################################################--orm private--###########################################################

async def orm_get_welcome(session: AsyncSession, username: str) -> bool:
    user = await session.execute(
        select(Users)
        .where(Users.username == username)
    )
    if not user.first():
        user_add = Users(username=username)
        session.add(user_add)
        await session.commit()
        return True
    else:
        return False
    


async def orm_get_access(session: AsyncSession, data: str) -> bool:
    user_limit_query = await session.execute(
        select(Users.gpt_limit)
        .where(Users.username == data)
    )
    user_limit = user_limit_query.scalar_one()
    if user_limit < 2 or data in CURRENT_LIMITLESS:
        await session.execute(
            update(Users)
            .where(Users.username == data)
            .values(gpt_limit=user_limit + 1)
        )
        await session.commit()
        return True
    else:
        return False


async def orm_add_anek(
    session: AsyncSession,
    data: dict
) -> None:
    """Функция проверяет есть ли в базе пользователь и категория, в случае отсутствия добавляет"""

    category = await session.execute(
        select(Category)
        .where(Category.name == data['category'])
    )
    if not category.first():
        category = Category(name=data['category'])
        session.add(category)

    user = await session.execute(
        select(Users)
        .where(Users.username == data['username'])
    )
    category = await session.execute(
        select(Category)
        .where(Category.name == data['category'])
    )
    category_id = category.scalar().id
    user_id = user.scalar().id

    anecdote = Anecdote(
        category_id= category_id,
        text=data['text'],
        user_id=user_id
    )
    session.add(anecdote)

    await session.commit()


async def orm_get_anek(
    session: AsyncSession
) -> Tuple[Anecdote, int] | None:
    query_select_all = await session.execute(
        select(Anecdote.id)
    )
    all_id = query_select_all.scalars().all()
    if all_id:
        rand_id = choice(all_id)
    else:
        return None
    query = await session.execute(
        select(Anecdote)
        .where(Anecdote.id == rand_id)
        .options(
            selectinload(Anecdote.category), 
            selectinload(Anecdote.users)
        )
    )
    anek = query.scalar()

    query_rate = await session.execute(
        select(func.sum(Rate.rate))
        .where(Rate.anecdote_id == rand_id)
    )
    rate = query_rate.scalar()
    if not rate:
        rate = 0

    return anek, rate


async def orm_set_rate(
    session: AsyncSession,
    anecdote_id: int,
    rate: int,
    user: str
) -> None:

    query_user = await session.execute(
        select(Users)
        .where(Users.username == user)
    )
    if not query_user.first():
        user_add = Users(username=user)
        session.add(user_add)
    
    query_user_id = await session.execute(
        select(Users.id)
        .where(Users.username == user)
    )
    user_id = query_user_id.scalar()
    query_select = await session.execute(
        select(Rate)
        .where(Rate.anecdote_id == anecdote_id)
        .where(Rate.user_id == user_id)
    )

    if not query_select.first():
        session.add(Rate(
            rate=rate,
            anecdote_id=anecdote_id,
            user_id=user_id)
        )
    else:
        await session.execute(
            update(Rate)
            .where(Rate.anecdote_id == anecdote_id)
            .where(Rate.user_id == user_id)
            .values(
                rate = rate,
                anecdote_id=anecdote_id,
                user_id=user_id
            )
        )

    await session.commit()

################################################--orm private admin--#####################################################

async def orm_get_all_anecdote(
    session: AsyncSession,
    offset: int
) -> List[Anecdote]:
    query_list = await session.execute(
        select(Anecdote)
        .offset(offset=offset)
        .limit(5)
    )
    return query_list.scalars().all()


async def orm_del_anecdote(
    session: AsyncSession,
    data: int
) -> int:
    deletion = await session.execute(
        delete(Anecdote)
        .where(Anecdote.id == data)
    )
    await session.commit()

    return deletion.rowcount


########################################################--orm group--###########################################################
