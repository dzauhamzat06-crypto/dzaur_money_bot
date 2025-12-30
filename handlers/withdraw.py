from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards import get_withdrawal_methods, get_main_menu
from config import config

router = Router()

class WithdrawalForm(StatesGroup):
    choosing_method = State()
    entering_amount = State()
    entering_details = State()

@router.message(F.text == "💰 Вывод средств")
@router.message(Command("withdraw"))
async def cmd_withdraw(message: Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return

    if user.balance < config.MIN_WITHDRAW:
        await message.answer(
            f"❌ Минимальная сумма для вывода: {config.MIN_WITHDRAW} ₽\n"
            f"💰 Ваш текущий баланс: {user.balance} ₽\n\n"
            f"💼 Выполняйте больше заданий, чтобы набрать нужную сумму!"
        )
        return

    await message.answer(
        f"💰 Доступно для вывода: {user.balance} ₽\n"
        f"📊 Минимальная сумма: {config.MIN_WITHDRAW} ₽\n\n"
        "💳 Выберите способ вывода:",
        reply_markup=get_withdrawal_methods()
    )
    await state.set_state(WithdrawalForm.choosing_method)

@router.callback_query(F.data.startswith("withdraw_"))
async def process_withdrawal_method(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split("_")[1]

    if method == "back":
        await state.clear()
        await callback.message.delete()
        return

    await state.update_data(method=method)

    methods_info = {
        "crypto": "💎 USDT (TRC-20)\n\nВведите сумму для вывода в рублях:",
        "qiwi": "🥝 QIWI\n\nВведите сумму для вывода в рублях:",
        "card": "💳 Карта РФ\n\nВведите сумму для вывода в рублях:"
    }

    await callback.message.edit_text(methods_info.get(method, "Введите сумму:"))
    await state.set_state(WithdrawalForm.entering_amount)
    await callback.answer()

@router.message(WithdrawalForm.entering_amount)
async def process_withdrawal_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        user = await db.get_user_by_telegram_id(message.from_user.id)

        if amount < config.MIN_WITHDRAW:
            await message.answer(
                f"❌ Сумма должна быть не менее {config.MIN_WITHDRAW} ₽\n"
                f"Попробуйте еще раз:"
            )
            return

        if amount > user.balance:
            await message.answer(
                f"❌ Недостаточно средств на балансе\n"
                f"💰 Доступно: {user.balance} ₽\n"
                f"Введите другую сумму:"
            )
            return

        await state.update_data(amount=amount)

        data = await state.get_data()
        method = data.get('method')

        prompts = {
            "crypto": "💎 Введите адрес вашего USDT кошелька (TRC-20):",
            "qiwi": "🥝 Введите номер вашего QIWI кошелька:",
            "card": "💳 Введите номер банковской карты:"
        }

        await message.answer(prompts.get(method, "Введите реквизиты:"))
        await state.set_state(WithdrawalForm.entering_details)

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму (только цифры):")

@router.message(WithdrawalForm.entering_details)
async def process_withdrawal_details(message: Message, state: FSMContext):
    details = message.text.strip()
    data = await state.get_data()

    withdrawal_id = await db.create_withdrawal_request(
        user_id=message.from_user.id,
        amount=data['amount'],
        method=data['method'],
        details=details
    )

    if withdrawal_id:
        await message.answer(
            f"✅ Заявка на вывод #{withdrawal_id} создана!\n\n"
            f"📊 Детали:\n"
            f"• Сумма: {data['amount']} ₽\n"
            f"• Способ: {data['method']}\n"
            f"• Реквизиты: {details[:15]}...\n\n"
            f"⏱️ Заявка будет обработана в течение 24 часов.\n"
            f"📞 По вопросам обращайтесь в поддержку."
        )

        for admin_id in config.ADMINS:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"🆕 Новая заявка на вывод #{withdrawal_id}\n"
                    f"👤 Пользователь: @{message.from_user.username or message.from_user.id}\n"
                    f"💰 Сумма: {data['amount']} ₽\n"
                    f"💳 Способ: {data['method']}\n"
                    f"📝 Реквизиты: {details}"
                )
            except:
                pass
    else:
        await message.answer(
            "❌ Не удалось создать заявку на вывод.\n"
            "Возможно, недостаточно средств на балансе."
        )

    await state.clear()
