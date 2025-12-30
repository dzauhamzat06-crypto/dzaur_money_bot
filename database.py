from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from models import Base, User, Task, Transaction, CompletedTask, Withdrawal
from config import config
import string
import random
from datetime import datetime

class Database:
    def __init__(self):
        self.engine = create_async_engine(config.DB_URL, echo=True)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_or_create_user(self, telegram_id: int, username: str = None,
                                first_name: str = None, last_name: str = None,
                                referrer_id: int = None):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                referral_code = self.generate_referral_code()
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    referral_code=referral_code,
                    referrer_id=referrer_id
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

                if referrer_id:
                    await self.add_referral_bonus(referrer_id, config.REFERRAL_REWARD)

            return user

    async def add_referral_bonus(self, referrer_id: int, amount: float):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == referrer_id)
            )
            referrer = result.scalar_one_or_none()

            if referrer:
                referrer.balance += amount
                referrer.total_earned += amount
                transaction = Transaction(
                    user_id=referrer.id,
                    amount=amount,
                    type='referral',
                    description='Бонус за приглашение друга',
                    status='completed'
                )
                session.add(transaction)
                await session.commit()

    async def get_active_tasks(self, category: str = None):
        async with self.session_factory() as session:
            query = select(Task).where(Task.is_active == True)
            if category:
                query = query.where(Task.category == category)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_user_by_telegram_id(self, telegram_id: int):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    async def update_balance(self, user_id: int, amount: float, transaction_type: str, description: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.balance += amount
                if amount > 0:
                    user.total_earned += amount
                transaction = Transaction(
                    user_id=user.id,
                    amount=amount,
                    type=transaction_type,
                    description=description,
                    status='completed'
                )
                session.add(transaction)
                await session.commit()
                return True
            return False

    async def create_withdrawal_request(self, user_id: int, amount: float, method: str, details: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()

            if user and user.balance >= amount:
                user.balance -= amount
                withdrawal = Withdrawal(
                    user_id=user.id,
                    amount=amount,
                    method=method,
                    details=details,
                    status='pending'
                )
                session.add(withdrawal)
                await session.commit()
                return withdrawal.id
            return None

    async def get_user_referrals(self, user_id: int):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.referrer_id == user_id)
            )
            return result.scalars().all()

    def generate_referral_code(self, length=8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    async def add_task(self, title: str, description: str, reward: float,
                      category: str, url: str, max_completions: int = 0):
        async with self.session_factory() as session:
            task = Task(
                title=title,
                description=description,
                reward=reward,
                category=category,
                url=url,
                max_completions=max_completions
            )
            session.add(task)
            await session.commit()
            return task.id

    async def complete_task(self, user_id: int, task_id: int, screenshot: str = None):
        async with self.session_factory() as session:
            result = await session.execute(
                select(CompletedTask).where(
                    CompletedTask.user_id == user_id,
                    CompletedTask.task_id == task_id
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                return None

            task_result = await session.execute(
                select(Task).where(Task.id == task_id)
            )
            task = task_result.scalar_one_or_none()

            if not task or not task.is_active:
                return None

            if task.max_completions > 0 and task.current_completions >= task.max_completions:
                return None

            completed_task = CompletedTask(
                user_id=user_id,
                task_id=task_id,
                screenshot=screenshot,
                status='pending'
            )
            session.add(completed_task)
            task.current_completions += 1
            await session.commit()
            return completed_task.id

db = Database()
