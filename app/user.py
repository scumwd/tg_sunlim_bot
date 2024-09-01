from aiogram import F, Router
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import CommandStart
from app.database.requests import set_user
from aiogram.fsm.context import FSMContext
from app.states import QuestionStates
from app.wiki import wiki_start_message, wiki_kb_menu_text, wiki_kb_question
import app.keyboards as kb
from app.database.requests import create_question, get_dutyes
from main import bot
from config import Role

userRouter = Router()

# START
@userRouter.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id, username=message.from_user.username)
    image = FSInputFile('app/img/start-img.jpg')
    await message.answer_photo(photo=image, caption=wiki_start_message, reply_markup=kb.subscribe_btn, parse_mode="HTML")
    await message.answer(text=wiki_kb_menu_text, reply_markup=kb.main)
    await state.clear()

# Задать вопрос
@userRouter.message(F.text == wiki_kb_question)
async def ask_question(message: Message, state: FSMContext):
    response_message = await message.answer("Пожалуйста, задайте ваш вопрос:", reply_markup=kb.cancel_ask)
    await state.set_state(QuestionStates.waiting_for_question)
    await state.update_data(question_message_id=response_message.message_id)

# Ожидание вопроса
@userRouter.message(QuestionStates.waiting_for_question)
async def receive_question(message: Message, state: FSMContext):
    data = await state.get_data()
    question_message_id = data.get('question_message_id')
    
    if question_message_id:
        try:
            await message.chat.delete_message(question_message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения с ID {question_message_id}: {e}")
    
    # Создание вопроса и отправка его администраторам
    question_id = await create_question(tg_id_user=message.from_user.id, tg_username_user=message.from_user.username,
                          id_message=message.message_id, 
                          text_question=message.text)
    dutyes = await get_dutyes()
    for duty in dutyes:
        try:
            await bot.send_message(duty.tg_id, 
                               f"Вопрос #{question_id} от @{message.from_user.username}: {message.text}", 
                               reply_markup=kb.create_answer_question_keyboard(question_id))
            print("Сообщение отправлено")
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору с ID {duty.tg_id}: {e}")
    
    await message.answer("Ваш вопрос был отправлен. Ожидайте ответа.")
    await state.clear()


# Отменить вопрос
@userRouter.callback_query(F.data == "cancel_ask")
async def cancle_ask_clicked(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    question_message_id = data.get('question_message_id')
    
    if question_message_id:
        try:
            await callback.message.chat.delete_message(question_message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения с ID {question_message_id}: {e}")

    await callback.message.answer('Вопрос отменен.')
    await state.clear()
