# Tg_bot
Asyncio telegram bot with aiogram, redis, postgres
Асинхронный телеграм бот на библиотеке aiogram с redis и postgres

## Запуск
Требуется создать файл `.env` с в директории tgbot, указав в нем следующие настройки:
* TOKEN=<токен от botfather>
* POSTGRES_USER=<пользователь postgres>
* POSTGRES_DB=<имя базы postgres>
* POSTGRES_PASSWORD=<пароль пользователя postgres>
* CATALOGUE_ID=<id каталога yandexcloud>
* KEY=<ключ yandexcloud>
* R_PASSWORD=<пароль для redis>

После всего вышеперечисленного требуется выполнить команду `docker-compose up --build -d`
Бот будет запущен.