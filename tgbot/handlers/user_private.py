import logging
import re
from random import choice

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.logic import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import Bold, Text, as_list
from sqlalchemy.ext.asyncio import AsyncSession

from bot_instance import BOT
from database.orm import (orm_add_anek, orm_get_access, orm_get_anek,
                          orm_get_welcome, orm_set_rate)
from filters.chat_types import ChatTypeFilter
from gpt.yandex import get_query
from kb.inline import get_inline_kb
from kb.reply import get_kb
from parcer import anecdote_from_parce

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(('private')))


START_KB = get_kb(
        'gpt',
        'joke_bot',
        placeholder='Что вас интересует?'
    )


class AddAnek(StatesGroup):
    category = State()
    text = State()

    texts = {
        'AddAnek:category': 'Введите категорию',
        'AddAnek:text': 'Введите текст'
    }


class GetQuery(StatesGroup):
    query = State()

    texts = {
        'GetQuery:query': 'Введите запрос',
    }


@user_private_router.message(or_f(CommandStart(), (F.text == '↩️ Назад')))
async def start(message: types.Message):
    await message.answer('Начнём:', reply_markup=START_KB)


@user_private_router.message(or_f(Command('gpt'), (F.text == 'gpt')))
async def gpt(message: types.Message, state: FSMContext, session: AsyncSession):
    welcome_message = await orm_get_welcome(
        session=session,
        username=message.from_user.username
    )
    if welcome_message:
        hello = (f'Добро пожаловать *{message.from_user.first_name}*\!👋\n'
            'Меня зовут *Чопа*🐶\, я умный пёс\.\n'
            'Ниже вы можете задать ваш вопрос\.')
    else:
        hello = f'Снова здравствуйте, *{message.from_user.username}*\!'
    await message.answer(hello, parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer(
        'Введите запрос',
        reply_markup=get_kb('Выйти из gpt', 'Информация')
    )
    await state.set_state(GetQuery.query)


@user_private_router.message(GetQuery.query, F.text == 'Информация')
async def gpt_quit(message: types.Message, state: FSMContext):
    text = ('🐶Для генерации текста используется языковая модель YandexGPT\.\n\n'
        '🐶Каждому пользователю предоставляется по 2 ознакомительных запроса\n\n'
        '🐶По вопросам сотрудничества обращаться к @anakinnikita')

    await message.answer(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_kb('Выйти из gpt', 'Информация')
    )


@user_private_router.message(GetQuery.query, F.text == 'Выйти из gpt')
async def gpt_quit(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы вышли', reply_markup=START_KB)


@user_private_router.message(GetQuery.query, F.text)
async def gpt_query(message: types.Message, session: AsyncSession):
    logging.info(f'Text from query: {message.text}')
    user_access = await orm_get_access(
        session=session,
        data=message.from_user.username
    )
    if user_access:
        response_message = await message.answer('Печатает...')
        response = await get_query(message.text)
        pattern = (
            r'\[', r'\]', r'\(', r'\)', r'\~', r'\>', r'\#', r'\+',
            r'\-', r'\=', r'\|', r'\{', r'\}', r'\.', r'\!'
        )
        for char in pattern:
            response = re.sub(char, '\\' + char, response)
        logging.info(f'Text from answer: {response}...')
        await BOT.delete_message(
            message.chat.id,
            response_message.message_id
        )
        await message.answer(
            response,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=get_kb('Выйти из gpt', 'Информация')
        )
    else:
        await message.answer('У вас закончились пробные запросы, свяжитесь с @anakinnikita.')


@user_private_router.message(or_f(Command('joke_bot'), (F.text.lower() == 'joke_bot')))
async def menu(message: types.Message):
    await message.answer('Это меню👇', reply_markup=get_kb(
        'Хочу анекдот😁', 'Добавить анекдот😃👍', 'Анекдоты подписчиков🤣', '↩️ Назад',
        placeholder='Выберите один из вариантов:',
        sizes=(1, 1),
    ))


@user_private_router.message(F.text == 'Хочу анекдот😁')
async def anecdote(message: types.Message):
    await message.answer(choice(anecdote_from_parce))


@user_private_router.message(F.text == 'Анекдоты подписчиков🤣')
async def anecdote_from_users(message: types.Message, session: AsyncSession):
    anecdote, rate = await orm_get_anek(session)
    text = as_list(
        Bold('🐶Рейтинг:'),
        Text(str(rate)),
        Bold('🐶Автор:'),
        Text('@' + str(anecdote.users.username)),
        Bold('🐶 Категория'),
        Text(anecdote.category.name),
        Bold('🐶Текст:'),
        Text(anecdote.text),
    )
    await message.answer(
        text.as_html(),
        reply_markup=get_inline_kb(
            {'👍': f'rate_1_{anecdote.id}_{message.from_user.username}',
            '👎': f'rate_-1_{anecdote.id}_{message.from_user.username}'},
            sizes=(2,)
        )
    )


@user_private_router.callback_query(F.data.startswith('rate_'))
async def rate_anecdote(callback: types.CallbackQuery, session: AsyncSession):
    data = callback.data.split('_')
    _, rate, anecdote_id, user = data
    await orm_set_rate(session, int(anecdote_id), int(rate), user)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Ваша оценка учтена!')


@user_private_router.message(StateFilter(None), F.text == 'Добавить анекдот😃👍')
async def add_anek(message: types.Message, state: FSMContext, session: AsyncSession):
    welcome_message = await orm_get_welcome(
        session=session,
        username=message.from_user.username
    )
    if welcome_message:
        hello = (f'Добро пожаловать *{message.from_user.first_name}*\!👋\n'
            'Ниже вы можете создать любой анекдот\.')
    else:
        hello = f'Снова здравствуйте, *{message.from_user.username}*\!'
    await message.answer(hello, parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer("Введите категорию")
    await state.set_state(AddAnek.category)


@user_private_router.message(AddAnek.category, F.text)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(username=message.from_user.username, category=message.text)
    await message.answer("Введите текст")
    await state.set_state(AddAnek.text)


@user_private_router.message(AddAnek.text, F.text)
async def add_text(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(text=message.text)
    await message.answer("Успешно")
    data = await state.get_data()
    await orm_add_anek(session=session, data=data, message=message)
    await state.clear()
