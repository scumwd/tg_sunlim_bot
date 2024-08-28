from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Filter
from app.database.requests import (get_user, set_role, 
                                   remove_role, get_users, 
                                   remove_user, get_question_by_id, 
                                   mark_question_as_processed,
                                   mark_as_spam, get_wait_questions,
                                   get_dutyes, remove_duty,
                                   add_duty)
from aiogram.fsm.context import FSMContext

from app.states import NewsLetter, QuestionStates, DutyAdd
from config import Role
from main import bot

import app.keyboards as kb

adminRouter = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        user = await get_user(message.from_user.id)
        return user.role == Role.admin
    
@adminRouter.message(Admin(), Command('admin_menu'))
async def show_admin_menu(message: Message):
    await message.answer('Меню для администратора',reply_markup= kb.admin_keyboard)


@adminRouter.callback_query(F.data == "question_list_btn")
async def question_list_clicked(callback: CallbackQuery):
    await callback.answer('Ждут ответа')
    await show_question_list(callback.message)

@adminRouter.message(Admin(), Command('question_list'))
async def question_list_command(message: Message):
    await message.answer('Ждут ответа')
    await show_question_list(message)

@adminRouter.callback_query(F.data == "duty_list_btn")
async def duty_list_clicked(callback: CallbackQuery):
    await callback.answer('')
    await show_duty_list(callback.message)

@adminRouter.message(Admin(), Command('duty_list'))
async def duty_list_command(message: Message):
    await message.answer('')
    await show_duty_list(message)

@adminRouter.callback_query(F.data.startswith("remove_duty_btn:"))
async def remove_duty_clicked(callback: CallbackQuery):
    duty_id = int(callback.data.split(":")[1])
    await remove_duty(duty_id)
    await callback.message.delete()
    await callback.answer('Дежурный удален.')
    

async def show_duty_list(message: Message):
    dutys = await get_dutyes()
    if len(dutys.all()) > 0:
        await message.answer('Список дежурных')
        for duty in dutys:
            try:
               await message.answer(f"Дежурный @{duty.username}", reply_markup=kb.create_delete_duty_btn(duty_id=duty.tg_id))
            except Exception as e:
                await remove_user(duty.tg_id)
                print(e)
    else:
        await message.answer('Список дежурных пуст.')

@adminRouter.callback_query(F.data == 'add_duty_btn')
async def add_duty_clicked(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Введите ник нового дежурного:')
    await state.set_state(DutyAdd.username)

@adminRouter.message(DutyAdd.username)
async def news_message(message: Message, state: FSMContext):
    await state.clear()
    new_duty_username = message.text.split()[1].lstrip('@')
    message_text = add_duty(new_duty_username)
    await message.answer(message_text)
    
async def show_question_list(message: Message):
    questions = await get_wait_questions()
    for question in questions:
        try:
            await message.answer(f"Вопрос #{question.id} от @{question.tg_username_user}: {question.text_question}",  reply_markup=kb.create_answer_question_keyboard(question.id))
        except Exception as e:
            print(e)
           
@adminRouter.message(Admin(), Command('news'))
async def news(message: Message, state: FSMContext):
    await state.set_state(NewsLetter.message)
    await message.answer('Введите сообщение для рассылки.')

@adminRouter.message(NewsLetter.message)
async def news_message(message: Message, state: FSMContext):
    await state.clear
    users = await get_users()
    for user in users:
        try:
            if user.role != Role.admin:
                await message.send_copy(chat_id=user.tg_id)
        except Exception as e:
            print(e)
            await remove_user(user.tg_id)

    await message.answer('Рассылка завершена.')
    

@adminRouter.message(Admin(), Command(commands=["add_admin"]))
async def add_admin(message: Message):
        new_admin_username = message.text.split()[1].lstrip('@')
        if (await set_role(Role.admin, new_admin_username)):
            await message.answer(f"Пользователь @{new_admin_username} был добавлен как администратор.")
        else:
            await message.answer(f"Пользователь @{new_admin_username} не был найден.")

@adminRouter.message(Admin(), Command(commands=["add_admin"]))
async def remove_admin(message: Message):
        admin_username = message.text.split()[1].lstrip('@')
        if (await remove_role(admin_username)):
            await message.answer(f"Пользователь @{admin_username} больше не администратор.")
        else:
            await message.answer(f"Администратор @{admin_username} не был найден.")

@adminRouter.callback_query(F.data.startswith("answer_question:"))
async def process_answer_question(callback_query: CallbackQuery, state: FSMContext):
    question_id = int(callback_query.data.split(":")[1])
    
    question = await get_question_by_id(question_id)
    if question.is_processed:
         await callback_query.answer('')
         await callback_query.message.answer('Этот вопрос уже обработан.')
         await state.clear()
    else:
        await callback_query.answer('')
        await callback_query.message.answer(
            f"Вы выбрали #{question_id}:\n{question.text_question}\n\nНапишите ваш ответ.",
            reply_markup= kb.cancel_question
        )
        await state.set_state(QuestionStates.waiting_for_admin_response)
        await state.update_data(question_id=question_id)

@adminRouter.callback_query(F.data == "cancel_question")
async def cancel_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Ответ отменен.')
    await state.clear()

@adminRouter.message(QuestionStates.waiting_for_admin_response)
async def process_admin_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question_id = data['question_id']
    question = await get_question_by_id(question_id=question_id)

    if question.is_processed | question.is_spam:
        await message.answer("На вопрос уже ответили.")
    else:
        await mark_question_as_processed(question_id, message.from_user.username, message.text)
        await message.answer("Ответ был отправлен пользователю.")
    await state.clear()
    

    # Отправляем ответ пользователю
    question = await get_question_by_id(question_id)
    await bot.send_message(chat_id=question.tg_id_user, text=message.text, reply_to_message_id=question.id_message)

@adminRouter.callback_query(F.data.startswith("spam:"))
async def mark_question_spam(callback_query: CallbackQuery, state: FSMContext):
    question_id = int(callback_query.data.split(":")[1])
    
    await mark_as_spam(question_id)
    await callback_query.answer('')
    await callback_query.message.answer('Сообщение помечено как спам.')
    await state.clear()

# Новый обработчик для кнопки "Список админов"
@adminRouter.callback_query(F.data == 'admin_list_btn')
async def show_admin_submenu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.create_admin_submenu())

# Новый обработчик для кнопки "Назад"
@adminRouter.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=kb.admin_keyboard)