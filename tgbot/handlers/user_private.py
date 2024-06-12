import logging
import re
from random import choice

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.logic import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_instance import BOT
from database.orm import (orm_add_anek, orm_get_access, orm_get_anek,
                          orm_get_welcome, orm_set_rate)
from filters.chat_types import ChatTypeFilter
from extensions.yandex import get_response
from kb.inline import get_inline_kb
from kb.reply import get_kb
from extensions.parcer import get_anec_list
from .states import AddAnec, GetQuery

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(('private')))


START_KB = get_kb(
        'gpt',
        'joke_bot',
        placeholder='Что вас интересует?'
    )


@user_private_router.message(or_f(CommandStart(), (F.text == '↩️ Назад')))
async def start(message: types.Message):
    hello_msg = 'Выбери, чем хочешь заняться🐶'
    if message.text == '/start':
        hello_msg = (f'Привет, *{message.from_user.full_name}*!\n\n'
                    'Меня зовут *Чопа*, я генератор шуток и мыслей. ') + hello_msg

    await message.answer(hello_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=START_KB)


@user_private_router.message(or_f(Command('gpt'), (F.text == 'gpt')))
async def gpt(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    # Функциия проверяет есть ли пользователь в базе и запускает FSM
    welcome_message = await orm_get_welcome(
        session=session,
        username=message.from_user.username
    )
    if welcome_message:
        hello = (f'Добро пожаловать *{message.from_user.first_name}*!👋\n'
            'Меня зовут *Чопа*🐶, я умный пёс.\n'
            'Ниже вы можете задать свой вопрос.')
    else:
        hello = f'Снова здравствуйте, *{message.from_user.username}*!'
    await message.answer(hello, parse_mode=ParseMode.MARKDOWN)
    await message.answer(
        'Введите запрос',
        reply_markup=get_kb('Выйти из gpt', 'Информация')
    )
    await state.set_state(GetQuery.query)


@user_private_router.message(GetQuery.query, F.text == 'Информация')
async def gpt_quit(message: types.Message):
    text = ('🐶Для генерации текста используется языковая модель *YandexGPT*.\n\n'
        '🐶Каждому пользователю предоставляется по *2* ознакомительных запроса\n\n'
        '🐶По вопросам сотрудничества обращаться к @anakinnikita')

    await message.answer(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_kb('Выйти из gpt', 'Информация')
    )


@user_private_router.message(GetQuery.query, F.text == 'Выйти из gpt')
async def gpt_quit(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы вышли', reply_markup=START_KB)


@user_private_router.message(GetQuery.query, F.text)
async def gpt_query(message: types.Message, session: AsyncSession):
    logging.info(f'Text from query: {message.text}')
    # Проверка, закончились ли у пользователя пробные запросы
    user_access = await orm_get_access(
        session=session,
        data=message.from_user.username
    )
    if user_access:
        response_message = await message.answer('Печатает...')
        # Запрос к gpt
        response = await get_response(message.text)
        # Так как markdown gpt отличается, требуется замена '**' на '*
        response = re.sub(r'(?<!\*)\*(?!\*)', '\*', response)
        response = re.sub(r'\*\*', '\\*', response)
        logging.info(f'Text from answer: {response}...')
        await BOT.delete_message(
            message.chat.id,
            response_message.message_id
        )
        await message.answer(
            response,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_kb('Выйти из gpt', 'Информация')
        )
    else:
        await message.answer('У вас закончились пробные запросы, свяжитесь с @anakinnikita.')


@user_private_router.message(or_f(
    Command('joke_bot'),
    (F.text.lower() == 'joke_bot')
))
async def menu(message: types.Message):
    await message.answer('Это меню👇', reply_markup=get_kb(
        'Хочу анекдот😁', 'Добавить анекдот😃👍', 'Анекдоты подписчиков🤣', '↩️ Назад',
        placeholder='Выберите один из вариантов:',
        sizes=(1, 1),
    ))


@user_private_router.message(F.text == 'Хочу анекдот😁')
async def anecdote(message: types.Message):
    anec_list = await get_anec_list()
    await message.answer(choice(anec_list))


@user_private_router.message(F.text == 'Анекдоты пользователей🤣')
async def anecdote_from_users(message: types.Message, session: AsyncSession):
    result = await orm_get_anek(session)
    if result:
        anecdote, rate = result
        text = ('🐶Рейтинг:\n'
            f'{str(rate)}\n\n'
            '🐶Автор:\n'
            f'@{str(anecdote.users.username)}\n\n'
            '🐶 Категория\n'
            f'{anecdote.category.name}\n\n'
            '🐶Текст:\n'
            f'{anecdote.text}'
        )
        await message.answer(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_inline_kb(
                {'👍': f'rate_1_{anecdote.id}_{message.from_user.username}',
                '👎': f'rate_-1_{anecdote.id}_{message.from_user.username}'},
                sizes=(2,)
            )
        )
    else:
        await message.answer('Здесь пока ничего нет.😞')


@user_private_router.callback_query(F.data.startswith('rate_'))
async def rate_anecdote(callback: types.CallbackQuery, session: AsyncSession):
    data = callback.data.split('_')
    _, rate, anecdote_id, user = data
    await orm_set_rate(session, int(anecdote_id), int(rate), user)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Ваша оценка учтена!')


@user_private_router.message(
    StateFilter(None),
    F.text == 'Добавить анекдот😃👍'
)
async def add_anek(message: types.Message, state: FSMContext, session: AsyncSession):
    # Функциия проверяет есть ли пользователь в базе и запускает FSM
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
    await state.set_state(AddAnec.category)


@user_private_router.message(AddAnec.category, F.text)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(username=message.from_user.username, category=message.text)
    await message.answer("Введите текст")
    await state.set_state(AddAnec.text)


@user_private_router.message(AddAnec.text, F.text)
async def add_text(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(text=message.text)
    await message.answer("Успешно")
    data = await state.get_data()
    await orm_add_anek(session=session, data=data)
    await state.clear()
