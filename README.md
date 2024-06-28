# Телеграм бот с YandexGPT. 
Asyncio telegram bot with aiogram, redis, postgres  
Асинхронный телеграм бот на библиотеке aiogram с redis и postgres.  
Контейнеры с __postgresql__ и __redis__, к которым подключается данный бот, описаны в другом *docker-compose.yml* https://github.com/nikzubov/test-mission/blob/main/docker-compose.yml.

## Краткое описание
Данный бот использует две базы *redis*, одну для хранения сессий пользователя, вторую для хранения последних диалогов пользователя с *gpt*. Подключение осуществляется при помощи библиотеки __redis-py__ c использованием асинхронного модуля asyncio. В качестве основной базы данных используется posgresql c *asyncpg*, используемая orm - __sqlalchemy__.

## Запуск
Требуется создать файл `.env` с в директории __tgbot__, указав в нем следующие настройки:  
* __TOKEN__=<токен от botfather>
* __POSTGRES_USER__=<пользователь postgres>
* __POSTGRES_DB__=<имя базы postgres>
* __POSTGRES_PASSWORD__=<пароль пользователя postgres>
* __CATALOGUE_ID__=<id каталога yandexcloud>
* __KEY__=<ключ yandexcloud>
* __R_PASSWORD__=<пароль для redis>

После всего вышеперечисленного требуется выполнить команду `docker-compose up --build -d`  
Бот будет запущен.
