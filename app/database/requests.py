from app.database.models import AsyncSession, User, Question
from sqlalchemy import select, update, delete
from config import Role
from datetime import datetime

##########################################
#                 User
##########################################

# Сохранить пользовтаеля
async def set_user(tg_id, username: str):
    async with AsyncSession() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id, role=Role.user, username=username))
        else:
            if user.username != username:
                stmt = update(User).where(User.tg_id == tg_id).values(username=username)
                await session.execute(stmt)

        await session.commit()

# Получить конертного пользователя
async def get_user(tg_id):  
    async with AsyncSession() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

# Получить всех пользователей   
async def get_users():  
    async with AsyncSession() as session:
        return await session.scalars(select(User))
    
# Получить всех админов   
async def get_admins():  
    async with AsyncSession() as session:
        result = await session.scalars(select(User).where(User.role==Role.admin))
        admins = result.all()
        return admins

# Удалить конкретного пользователя
async def remove_user(tg_id):  
    async with AsyncSession() as session:
        return await session.scalars(delete(User).where(User.tg_id == tg_id))

# Установить роль для пользователя по нику    
async def set_role(new_role, nickname):
    async with AsyncSession() as session:
        user = await session.scalar(select(User).where(User.username == nickname))
        
        if not user:
            return False
        else:
            stmt = update(User).where(User.username == nickname).values(role = new_role)
            await session.execute(stmt)
        
        await session.commit()
        return True

# Убрать роль у пользователя (устанавливается 'user' как по-умолчанию)
async def remove_role(nickname):
    async with AsyncSession() as session:
        user = await session.scalar(select(User).where(User.username == nickname))
        
        if not user:
            return False
        else:
            stmt = update(User).where(User.username == nickname).values(role = Role.user)
            await session.execute(stmt)

        await session.commit()
        return True

##########################################
#                Question
##########################################

# Получить дежурных пользователей
async def get_dutyes():
    async with AsyncSession() as session:
        result = await session.scalars(select(User).where(User.is_duty == True))
        dutys = result.all() 
        return dutys
    
async def remove_duty(tg_id):
    async with AsyncSession() as session:
        async with session.begin():
            await session.execute(update(User).where(User.tg_id == tg_id).values(is_duty = False))
            await session.commit()

async def remove_duty_by_username(username):
    async with AsyncSession() as session:
        async with session.begin():
            await session.execute(update(User).where(User.username == username).values(is_duty = False))
            await session.commit()

async def add_duty(username):
    async with AsyncSession() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.username == username))
            
            if not user:
                await session.commit()
                return 'Пользователя нет в базе'
            elif user.is_duty == True:
                await session.commit()
                return 'Пользователь уже дежурный'
            else:
                await session.execute(update(User).where(User.username == username).values(is_duty = True))
                await session.commit()
                return 'Дежурный добавлен'


# Создать вопрос в бд и вернуть его сгенерированный ID
async def create_question(tg_id_user, tg_username_user, id_message, text_question):
    async with AsyncSession() as session:
        question = Question(
            tg_id_user=tg_id_user,
            tg_username_user = tg_username_user,
            id_message=id_message,
            text_question=text_question,
            create_at=datetime.now()
        )
        session.add(question)
        await session.commit()

        stmt = select(Question).filter_by(
            tg_id_user=tg_id_user,
            tg_username_user = tg_username_user,
            id_message=id_message,
            text_question=text_question
        )
        result = await session.execute(stmt)
        added_question = result.scalar_one()

        return added_question.id
    
async def get_question_by_id(question_id):
    async with AsyncSession() as session:
        return await session.scalar(select(Question).where(Question.id==question_id))
    
async def get_wait_questions():
    async with AsyncSession() as session:
        result = await session.scalars(select(Question).where(Question.is_processed==False, Question.is_spam == False))
        questions = result.all()
        return questions

# Пометить вопрос как обработанный и сохранить ответ    
async def mark_question_as_processed(question_id: int, admin_username: str, answer_text: str):
    async with AsyncSession() as session:
        async with session.begin():
            stmt = (
                update(Question)
                .where(Question.id == question_id)
                .values(admin_username=admin_username, answer_text=answer_text, is_processed=True)
            )
            await session.execute(stmt) 
            await session.commit()

async def mark_as_spam(question_id):
    async with AsyncSession() as session:
        async with session.begin():
            stmt = (
                update(Question)
                .where(Question.id == question_id)
                .values(is_spam=True)
            )
            await session.execute(stmt) 
            await session.commit()
