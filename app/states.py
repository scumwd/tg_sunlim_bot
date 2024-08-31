from aiogram.fsm.state import StatesGroup, State

class NewsLetter(StatesGroup):
    message = State()

class QuestionStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_admin_response = State()

class DutyAdd(StatesGroup):
    username = State()

class DutyRemove(StatesGroup):
    username = State()

class AdminRemove(StatesGroup):
    username = State()

class AdminAdd(StatesGroup):
    username = State()