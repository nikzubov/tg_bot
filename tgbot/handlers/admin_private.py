from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.orm import orm_del_anecdote, orm_get_all_anecdote
from filters.chat_types import ChatTypeFilter, IsAdmin
from kb.inline import get_inline_kb
from kb.reply import get_kb
from sqlalchemy.ext.asyncio import AsyncSession

from .states import DeleteAnec

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(('private')), IsAdmin())


ADMIN_KB = get_kb(
    'Удалить анекдот',
    'Посмотреть все анекдоты',
    placeholder='Выберите действие',
    sizes=(1,),
)


@admin_router.message(F.text == 'Посмотреть все анекдоты')
async def watch_anecdote(message: types.Message, session: AsyncSession):
    anecdote_list = await orm_get_all_anecdote(session=session, offset=0)
    text = ''
    for row in anecdote_list:
        text += (f'*id:* {str(row.id)}\n\n'
                 f'*Текст:*\n\n'
                 f'{row.text}\n\n')
    await message.answer(text, reply_markup=get_inline_kb(
            {'след.': 'next_0', 'Выход': 'quit'},
            sizes=(1,)
        )
    )


@admin_router.callback_query(F.data == 'quit')
async def quit(callback: types.CallbackQuery):
    await callback.message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.callback_query(F.data.startswith('next_'))
async def next_page(callback: types.CallbackQuery, session: AsyncSession):
    _, last_offset = callback.data.split('_')
    offset = int(last_offset) + 5
    row_list = await orm_get_all_anecdote(session=session, offset=offset)
    text = ''
    for row in row_list:
        text += (f'*id:* {str(row.id)}\n\n'
                 f'*Текст:*\n\n'
                 f'{row.text}\n\n')
        await callback.message.answer(
            text,
            reply_markup=get_inline_kb(
                {'след.': f'next_{offset}', 'Выход': 'quit'},
                sizes=(2,)
            )
        )


@admin_router.message(F.text == 'Удалить анекдот')
async def delete_anecdote(message: types.Message, state: FSMContext):
    await message.answer('Введите id анекдота')
    await state.set_state(DeleteAnec.id)


@admin_router.message(DeleteAnec.id, F.text)
async def set_id(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    await state.update_data(id=message.text)
    data = await state.get_data()
    result = await orm_del_anecdote(session, int(data['id']))
    if result:
        await message.answer('Успешно')
    else:
        await message.answer('Ошибка')
    await state.clear()


@admin_router.message(Command('admin'))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)
