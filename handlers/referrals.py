from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import db
from keyboards import get_referral_keyboard, get_main_menu
from config import config

router = Router()

@router.message(F.text == "👥 Рефералы")
@router.message(Command("referral"))
async def cmd_referral(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return

    referrals = await db.get_user_referrals(user.id)

    referral_text = f"""
    👥 Реферальная система

    💰 Вы получаете {config.REFERRAL_BONUS}% от заработка каждого приглашенного друга!

    📊 Ваша статистика:
    • Всего приглашено: {len(referrals)} чел.
    • Активных рефералов: {len(referrals)} чел.
    • Заработано на рефералах: 0 ₽

    🔗 Ваша реферальная ссылка:
    https://t.me/your_bot?start=ref{user.telegram_id}

    📝 Или реферальный код:
    {user.referral_code}

    📌 Как приглашать:
    1. Отправьте другу вашу ссылку
    2. Он должен нажать на нее и начать работу с ботом
    3. Вы будете получать % с его заработка!
    """

    await message.answer(
        referral_text,
        reply_markup=get_referral_keyboard(user.telegram_id, user.referral_code)
    )

@router.callback_query(F.data == "referrals_list")
async def referrals_list(callback: CallbackQuery):
    user = await db.get_user_by_telegram_id(callback.from_user.id)
    referrals = await db.get_user_referrals(user.id)

    if not referrals:
        await callback.message.edit_text("📭 У вас пока нет приглашенных друзей.")
        await callback.answer()
        return

    list_text = "📋 Ваши рефералы:\n\n"
    for i, ref in enumerate(referrals[:20], 1):
        name = ref.first_name or ref.username or f"Пользователь {ref.telegram_id}"
        list_text += f"{i}. {name}\n"
        list_text += f"   📅 Зарегистрирован: {ref.registered_at.strftime('%d.%m.%Y')}\n"
        list_text += f"   💰 Заработал: {ref.total_earned} ₽\n\n"

    if len(referrals) > 20:
        list_text += f"\n... и еще {len(referrals) - 20} рефералов"

    await callback.message.edit_text(list_text)
    await callback.answer()
