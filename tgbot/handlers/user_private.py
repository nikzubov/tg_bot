import logging
import re
from random import choice

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.logic import or_f
from aiogram.fsm.context import FSMContext
from bot_instance import BOT
from database.orm import (orm_add_anek, orm_get_access, orm_get_anek,
                          orm_get_welcome, orm_set_rate)
from database.redis_client import redis_client_gpt
from extensions.parcer import get_anec_list
from extensions.yandex import ya_client
from filters.chat_types import ChatTypeFilter
from kb.inline import get_inline_kb
from kb.reply import GPT_KB, JOKE_KB, START_KB
from sqlalchemy.ext.asyncio import AsyncSession

from .states import AddAnec, GetQuery

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(('private')))


@user_private_router.message(
    or_f(GetQuery.query, AddAnec.category, AddAnec.text),
    or_f(F.text == 'Выйти из gpt', CommandStart())
)
async def gpt_quit(message: types.Message, state: FSMContext):
    """Отчистка состояний FSM и возврат стартовой клавиатуры"""

    await state.clear()
    await message.answer('Вы вышли', reply_markup=START_KB)


@user_private_router.message(or_f(CommandStart(), (F.text == '↩️ Назад')))
async def start(message: types.Message):
    hello_msg = 'Выбери, чем хочешь заняться🐶'
    if message.text == '/start':
        hello_msg = (f'Привет, *{message.from_user.full_name}*!\n\n'
                     'Меня зовут *Чопа*, '
                     'я генератор шуток и мыслей. ') + hello_msg

    await message.answer(
        hello_msg,
        reply_markup=START_KB,
    )


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
    await message.answer(hello)
    await message.answer(
        'Введите запрос',
        reply_markup=GPT_KB
    )
    await state.set_state(GetQuery.query)


@user_private_router.message(GetQuery.query, F.text == 'Информация')
async def gpt_info(message: types.Message):
    text = ('🐶Для генерации текста используется '
            'языковая модель *YandexGPT*.\n\n'
            '🐶Каждому пользователю предоставляется '
            'по *2* ознакомительных запроса\n\n'
            '🐶По вопросам сотрудничества обращаться к @anakinnikita')

    await message.answer(
        text,
        reply_markup=GPT_KB
    )


@user_private_router.message(GetQuery.query, F.text)
async def gpt_query(
    message: types.Message,
    session: AsyncSession
):
    """Обработка запроса к gpt"""

    logging.info(f'Text from query: {message.text}')
    # Проверка, закончились ли у пользователя пробные запросы
    user_access = await orm_get_access(
        session=session,
        data=message.from_user.username
    )
    if user_access:
        response_message = await message.answer('Печатает...')
        key = f'messages:{message.from_user.username}'
        # Получение истории диалога с gpt
        user_messages = await redis_client_gpt.messages_get(key)
        # Запрос к gpt
        response = await ya_client.get_response(message.text, user_messages)
        key = f'messages:{message.from_user.username}'
        # Добавление последних сообщений в историю диалога с gpt
        await redis_client_gpt.messages_post(key, message.text, response)
        # Экранирование одиночных '*'
        response_re = re.sub(r'(?<!\*)\*(?!\*)', '\\*', response)
        # Так как markdown gpt отличается, требуется замена '**' на '*
        response_re = re.sub(r'\*\*', '*', response_re)
        logging.info(f'Text from answer: {response}...')
        await BOT.delete_message(
            message.chat.id,
            response_message.message_id
        )
        try:
            await message.answer(
                response_re,
                reply_markup=get_kb('Выйти из gpt', 'Информация')
            )
        except TelegramBadRequest:
            logging.error('Mardown сброшен, плохой запрос к telegram.')
            await message.answer(
                response,
                reply_markup=get_kb('Выйти из gpt', 'Информация'),
                parse_mode=None
            )
    else:
        await message.answer(
            'У вас закончились пробные запросы, свяжитесь с @anakinnikita.'
        )


@user_private_router.message(or_f(
    Command('joke_bot'),
    (F.text.lower() == 'joke_bot'),
    (F.text.lower() == 'выйти без сохранения')
))
async def menu(message: types.Message, state: FSMContext = None):
    """Меню шуток бота"""

    if state:
        await state.clear()
    await message.answer('Это меню👇', reply_markup=JOKE_KB)


@user_private_router.message(F.text == 'Хочу анекдот😁')
async def anecdote(message: types.Message):
    anec_list = await get_anec_list()
    await message.answer(choice(anec_list))


@user_private_router.message(F.text == 'Анекдоты пользователей🤣')
async def anecdote_from_users(
    message: types.Message,
    session: AsyncSession
):
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
                f'{anecdote.text}')
        await message.answer(
            text,
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
async def add_anek(
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
                 'Ниже вы можете создать любой анекдот.')
    else:
        hello = f'Снова здравствуйте, *{message.from_user.username}*!'
    await message.answer(hello)
    await message.answer(
        "Введите категорию",
        reply_markup=get_kb('Выйти без сохранения')
    )
    await state.set_state(AddAnec.category)


@user_private_router.message(AddAnec.category, F.text)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(
        username=message.from_user.username,
        category=message.text
    )
    await message.answer("Введите текст")
    await state.set_state(AddAnec.text)


@user_private_router.message(AddAnec.text, F.text)
async def add_text(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    await state.update_data(text=message.text)
    await message.answer("Успешно", reply_markup=JOKE_KB)
    data = await state.get_data()
    await orm_add_anek(session=session, data=data)
    await state.clear()
