import asyncio
import logging

from aiogram import Dispatcher, types
from aiogram.fsm.strategy import FSMStrategy

from basic.bot_commands import group, private
from bot_instance import BOT
from database.engine import create_db, session_maker
from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from handlers.user_private import user_private_router
from middlewares.db import DataBaseSession
from extensions.parcer import build_anec_list

logging.basicConfig(
    level=logging.INFO,
    filename='bot_log.log',
    filemode='w',
    format="%(asctime)s %(levelname)s %(message)s"
)

ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']

dp = Dispatcher(fsm_strategy=FSMStrategy.GLOBAL_USER)

dp.include_routers(user_group_router, admin_router, user_private_router)

async def on_startup():
    await create_db()
    await build_anec_list()


async def main():
    dp.startup.register(on_startup)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await BOT.delete_webhook(drop_pending_updates=True)
    await BOT.set_my_commands(
        commands=private,
        scope=types.BotCommandScopeAllPrivateChats()
    )
    await BOT.set_my_commands(
        commands=group,
        scope=types.BotCommandScopeAllGroupChats()
    )
    await dp.start_polling(BOT, allowed_updates=ALLOWED_UPDATES)


if __name__ == "__main__":
    asyncio.run(main())
