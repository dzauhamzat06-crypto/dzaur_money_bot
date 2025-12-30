from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import db
from keyboards import get_profile_keyboard, get_main_menu
from config import config

router = Router()

@router.message(F.text == "📊 Профиль")
@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return

    referrals = await db.get_user_referrals(user.id)

    profile_text = f"""
    👤 Ваш профиль:

    💰 Баланс: {user.balance} ₽
    📈 Всего заработано: {user.total_earned} ₽

    👥 Реферальная система:
    • Приглашено друзей: {len(referrals)}
    • Реферальный код: {user.referral_code}
    • Бонус за реферала: {config.REFERRAL_BONUS}%

    📅 Дата регистрации: {user.registered_at.strftime('%d.%m.%Y')}
    """

    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(F.data == "profile_stats")
async def profile_stats(callback: CallbackQuery):
    user = await db.get_user_by_telegram_id(callback.from_user.id)
    referrals = await db.get_user_referrals(user.id)

    stats_text = f"""
    📊 Детальная статистика:

    💰 Финансы:
    • Текущий баланс: {user.balance} ₽
    • Всего заработано: {user.total_earned} ₽
    • Доступно к выводу: {user.balance} ₽

    👥 Рефералы:
    • Всего приглашено: {len(referrals)}
    • Активных: {len([r for r in referrals])}
    • Заработано на рефералах: {user.total_earned * (config.REFERRAL_BONUS / 100)} ₽

    💼 Задания:
    • Выполнено заданий: {len(user.completed_tasks)}
    • На проверке: {len([t for t in user.completed_tasks if t.status == 'pending'])}
    """

    await callback.message.edit_text(stats_text)
    await callback.answer()

@router.callback_query(F.data == "transactions")
async def show_transactions(callback: CallbackQuery):
    user = await db.get_user_by_telegram_id(callback.from_user.id)
    transactions = user.transactions[:10] if user.transactions else []

    if not transactions:
        await callback.answer("У вас еще нет транзакций")
        return

    transactions_text = "📋 История операций:\n\n"
    for i, tx in enumerate(transactions[:10], 1):
        sign = "+" if tx.amount > 0 else "-"
        date = tx.created_at.strftime("%d.%m %H:%M")
        transactions_text += f"{i}. {date} - {sign}{abs(tx.amount)} ₽\n"
        transactions_text += f"   📝 {tx.description}\n\n"

    await callback.message.edit_text(transactions_text)
    await callback.answer()
