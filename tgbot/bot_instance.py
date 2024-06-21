from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings

BOT = Bot(
    token=settings.TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

SCHEDULER = AsyncIOScheduler()
