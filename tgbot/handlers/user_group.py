import logging
from random import choice

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm import get_users
from filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(('supergroup', 'group')))


@user_group_router.message(Command('surprise'))
async def surprise(message: types.Message):
    input_file = types.FSInputFile('/Users/nikitazubov/Dev/tg_bot/tgbot/static/audio/voice.ogg')
    gif = types.FSInputFile('/Users/nikitazubov/Dev/tg_bot/tgbot/static/gif/vin-diesal-nodding.gif')
    await message.answer_document(document=gif)
    await message.answer_voice(voice=input_file)
