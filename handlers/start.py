from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from database import db
from keyboards import get_main_menu
from config import config

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split()
    referrer_id = None

    if len(args) > 1 and args[1].startswith('ref'):
        try:
            referrer_id = int(args[1][3:])
        except ValueError:
            pass

    user = await db.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        referrer_id=referrer_id
    )

    welcome_text = f"""
    🎉 Добро пожаловать в {config.BOT_NAME}!

    💰 Здесь вы можете зарабатывать деньги, выполняя простые задания:
    • Подписки на каналы
    • Просмотры видео
    • Комментарии и лайки
    • И многое другое!

    📊 Ваш баланс: {user.balance} ₽
    👥 Приглашайте друзей и получайте {config.REFERRAL_BONUS}% от их заработка!

    🚀 Начните прямо сейчас - нажмите "💼 Задания"
    """

    await message.answer(welcome_text, reply_markup=get_main_menu())

    if referrer_id:
        try:
            await message.bot.send_message(
                referrer_id,
                f"🎉 По вашей ссылке зарегистрировался новый пользователь!\n"
                f"Вам начислено {config.REFERRAL_REWARD} ₽ на баланс."
            )
        except:
            pass
