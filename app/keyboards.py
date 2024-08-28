from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from app.wiki import wiki_kb_question, wiki_kb_subscribe, wiki_kb_menu_placeholder, wiki_subscribe_btn_text, wiki_url_tg, wiki_kb_answer_question

keyboardList = [[KeyboardButton(text=wiki_kb_subscribe), 
                KeyboardButton(text=wiki_kb_question)]]

main = ReplyKeyboardMarkup(keyboard=keyboardList, resize_keyboard=True, input_field_placeholder=wiki_kb_menu_placeholder)

subscribe_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=wiki_subscribe_btn_text, callback_data='subscribe', url=wiki_url_tg)]])

cancel_question = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отменить", callback_data='cancel_question')]])

def create_answer_question_keyboard(question_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Ответить на вопрос",
                callback_data=f"answer_question:{question_id}"
            ),
            InlineKeyboardButton(
                text="Спам",
                callback_data=f"spam:{question_id}"
            )
        ]
    ])
    return keyboard

def create_delete_duty_btn(duty_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup ( inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Удалить дежурного',
                callback_data=f'remove_duty_btn:{duty_id}'   
            )
        ]
    ])
    return keyboard


admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Ожидают ответа*',
            callback_data='question_list_btn'
        )
    ],
    [
        InlineKeyboardButton(
            text='Список дежурных',
            callback_data='duty_list_btn'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавить дежурного',
            callback_data='add_duty_btn'
        ),
        InlineKeyboardButton(
            text='Удалить дежурного',
            callback_data='remove_duty_menu'
        )
    ],
    [
        InlineKeyboardButton(
            text='Список админов',
            callback_data='admin_list_btn'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавить админа',
            callback_data='add_admin_btn'
        ),
        InlineKeyboardButton(
            text='Удалить админа',
            callback_data='remove_admin_btn'
        )
    ]
])

# Подменю для работы с администраторами
def create_admin_submenu() -> InlineKeyboardMarkup:
    submenu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить админа',
                callback_data='add_admin_btn'
            ),
            InlineKeyboardButton(
                text='Удалить админа',
                callback_data='remove_admin_btn'
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='back_to_main_menu'
            )
        ]
    ])
    
    return submenu