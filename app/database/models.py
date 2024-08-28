from sqlalchemy import Text, String, BigInteger, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from config import DB_URL

engine = create_async_engine(url=DB_URL,
                             echo=True) 
    
AsyncSession = async_sessionmaker(bind=engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped [str]=mapped_column(String(15))
    username: Mapped [str]=mapped_column(String(255))
    is_duty: Mapped[bool] = mapped_column(Boolean, default=False)

class Question(Base):
    __tablename__ = 'questions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id_user: Mapped[int] = mapped_column(BigInteger)
    tg_username_user: Mapped[str] = mapped_column(String(255))
    id_message: Mapped[int] = mapped_column(BigInteger)
    text_question: Mapped[str] = mapped_column(String(255))
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_processed: Mapped[bool] = mapped_column(Boolean(), default=False)
    admin_username: Mapped[str] = mapped_column(String(255), nullable=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=True)
    is_spam: Mapped[bool] = mapped_column(Boolean, default=False)

    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
