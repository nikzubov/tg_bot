from aiogram.types import KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_kb(
        *buttons: str,
        placeholder: str | None = None,
        request_contact: int | None = None,
        request_location: int | None = None,
        sizes: tuple[int] = (2,)
        ):
    keyboard = ReplyKeyboardBuilder()
    for idx, text in enumerate(buttons):
        if request_contact and request_contact == idx + 1:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == idx + 1:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )


del_kb = ReplyKeyboardRemove()


START_KB = get_kb(
        'gpt',
        'joke_bot',
        placeholder='Что вас интересует?'
)
JOKE_MENU_KB = get_kb(
        'Хочу анекдот😁', 'Добавить анекдот😃👍', 'Анекдоты пользователей🤣', '↩️ Назад',
        placeholder='Выберите один из вариантов:',
        sizes=(1, 1),
)
JOKE_KB = get_kb('Выйти без сохранения')
GPT_KB = get_kb(
    'Выйти из gpt', 'Информация',
    placeholder='Введите запрос'
)
