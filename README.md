# Телеграм бот с YandexGPT. 
Asyncio telegram bot with aiogram, redis, postgres  
Асинхронный телеграм бот на библиотеке aiogram с redis и postgres.  
Контейнеры с *postgresql* и *redis*, к которым подключается данный бот, описаны в другом __docker-compose.yml__ https://github.com/nikzubov/test-mission/blob/main/docker-compose.yml.

## Краткое описание
Данный бот использует две базы __redis__, одну для хранения сессий пользователя, вторую для хранения последних диалогов пользователя с __gpt__. Подключение осуществляется при помощи библиотеки *redis-py* c использованием асинхронного модуля asyncio. В качестве основной базы данных используется posgresql c __asyncpg__, используемая orm - *sqlalchemy*.

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
