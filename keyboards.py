from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="📊 Профиль"))
    keyboard.add(KeyboardButton(text="💼 Задания"))
    keyboard.add(KeyboardButton(text="👥 Рефералы"))
    keyboard.add(KeyboardButton(text="💰 Вывод средств"))
    keyboard.add(KeyboardButton(text="ℹ️ Помощь"))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)

def get_profile_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📈 Статистика", callback_data="profile_stats"))
    keyboard.add(InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="deposit"))
    keyboard.add(InlineKeyboardButton(text="🔄 История операций", callback_data="transactions"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_tasks_keyboard(categories):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=f"🎯 {category}",
            callback_data=f"tasks_{category}"
        ))
    keyboard.add(InlineKeyboardButton(text="📋 Все задания", callback_data="tasks_all"))
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_task_keyboard(task_id, url):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔗 Перейти к заданию", url=url))
    keyboard.add(InlineKeyboardButton(text="✅ Выполнил задание", callback_data=f"complete_{task_id}"))
    keyboard.add(InlineKeyboardButton(text="📤 Прикрепить скриншот", callback_data=f"screenshot_{task_id}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад к заданиям", callback_data="tasks_back"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_withdrawal_methods():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="💎 USDT (TRC-20)", callback_data="withdraw_crypto"))
    keyboard.add(InlineKeyboardButton(text="🥝 QIWI", callback_data="withdraw_qiwi"))
    keyboard.add(InlineKeyboardButton(text="💳 Карта РФ", callback_data="withdraw_card"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="withdraw_back"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_referral_keyboard(user_id, referral_code):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="📤 Пригласить друга",
        url=f"https://t.me/share/url?url=https://t.me/your_bot?start=ref{user_id}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="📋 Список рефералов",
        callback_data="referrals_list"
    ))
    keyboard.add(InlineKeyboardButton(
        text="📊 Статистика",
        callback_data="referrals_stats"
    ))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_admin_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📊 Статистика бота", callback_data="admin_stats"))
    keyboard.add(InlineKeyboardButton(text="➕ Добавить задание", callback_data="admin_add_task"))
    keyboard.add(InlineKeyboardButton(text="📋 Управление заданиями", callback_data="admin_manage_tasks"))
    keyboard.add(InlineKeyboardButton(text="⏳ Заявки на вывод", callback_data="admin_withdrawals"))
    keyboard.add(InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_confirmation_keyboard(action, data_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{action}_{data_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"cancel_{action}_{data_id}"))
    keyboard.adjust(2)
    return keyboard.as_markup()
