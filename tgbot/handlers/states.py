from aiogram.fsm.state import State, StatesGroup

#########################################--user_private--##########################################


class AddAnec(StatesGroup):
    category = State()
    text = State()


class GetQuery(StatesGroup):
    query = State()


#########################################--admin_private--##########################################

class DeleteAnec(StatesGroup):
    id = State()
