from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import db
from keyboards import get_tasks_keyboard, get_task_keyboard, get_main_menu
from config import config

router = Router()

@router.message(F.text == "💼 Задания")
@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    categories = ["subscribe", "like", "comment", "watch", "other"]
    await message.answer(
        "🎯 Выберите категорию заданий:",
        reply_markup=get_tasks_keyboard(categories)
    )

@router.callback_query(F.data.startswith("tasks_"))
async def show_category_tasks(callback: CallbackQuery):
    category = callback.data.split("_")[1]

    if category == "all":
        tasks = await db.get_active_tasks()
    else:
        tasks = await db.get_active_tasks(category)

    if not tasks:
        await callback.message.edit_text(
            "📭 В этой категории пока нет заданий. Загляните позже!"
        )
        await callback.answer()
        return

    tasks_text = f"📋 Доступные задания ({len(tasks)}):\n\n"
    keyboard = InlineKeyboardBuilder()

    for task in tasks:
        tasks_text += f"🔸 {task.title}\n"
        tasks_text += f"   💰 Награда: {task.reward} ₽\n"
        tasks_text += f"   📝 {task.description[:50]}...\n\n"

        keyboard.add(InlineKeyboardButton(
            text=f"🎯 {task.title} - {task.reward}₽",
            callback_data=f"view_task_{task.id}"
        ))

    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="tasks_back"))
    keyboard.adjust(1)

    await callback.message.edit_text(tasks_text, reply_markup=keyboard.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("view_task_"))
async def view_task(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[2])

    task_info = f"""
    🎯 Задание #1

    📝 Описание:
    Подпишитесь на наш канал и оставайтесь подписанным минимум 7 дней.

    💰 Награда: 5 ₽
    ⏱️ Время выполнения: 2 минуты
    🔄 Доступно раз: Без ограничений

    📌 Инструкция:
    1. Нажмите кнопку ниже
    2. Подпишитесь на канал
    3. Вернитесь в бота
    4. Нажмите "✅ Выполнил задание"
    5. Прикрепите скриншот подписки
    """

    await callback.message.edit_text(
        task_info,
        reply_markup=get_task_keyboard(task_id, "https://t.me/your_channel")
    )
    await callback.answer()

@router.callback_query(F.data.startswith("complete_"))
async def complete_task(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    completed_id = await db.complete_task(user_id, task_id)

    if completed_id:
        await callback.message.edit_text(
            "✅ Задание принято на проверку!\n\n"
            "📤 Вы можете прикрепить скриншот для быстрой проверки.\n"
            "⏱️ Проверка занимает до 24 часов."
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось принять задание.\n"
            "Возможные причины:\n"
            "• Вы уже выполняли это задание\n"
            "• Задание больше не доступно\n"
            "• Достигнут лимит выполнений"
        )
    await callback.answer()
