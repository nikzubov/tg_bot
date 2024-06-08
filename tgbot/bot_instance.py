import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))

from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

BOT = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
