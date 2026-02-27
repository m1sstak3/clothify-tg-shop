from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.admin import IsAdmin
from states.user_states import AdminState
from database.db import add_product, get_stats, get_orders, update_order_status
from utils.wait_states import show_loading_animation, finish_loading_animation
from locales.manager import get_text
import logging

router = Router()
router.message.filter(IsAdmin())

def get_admin_lang(event: Message | CallbackQuery) -> str:
    return "ru" # For admin we can fix it to RU or use user lang


@router.message(Command("admin"))
@router.message(F.text.in_(["⚙️ Админ панель", "⚙️ Admin Panel"]))
async def admin_panel(message: Message):
    await message.answer(
        "🔧 <b>Панель администратора</b>\n\n"
        "/add_product - Добавить новый товар\n"
        "/orders - Список последних заказов\n"
        "/stats - Статистика продаж",
        parse_mode="HTML"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    stats = await get_stats()
    await message.answer(
        f"📊 <b>Статистика магазина:</b>\n\n"
        f"📦 Всего заказов: <b>{stats['total_orders']}</b>\n"
        f"💰 Общая сумма: <b>{stats['total_sales']}$</b>",
        parse_mode="HTML"
    )

@router.message(Command("orders"))
async def cmd_orders(message: Message):
    orders = await get_orders(limit=10)
    if not orders:
        await message.answer("Заказов пока нет.")
        return
        
    for order in orders:
        # order: (id, user_id, username, product_id, size, address, status, created_at)
        text = (
            f"📦 <b>Заказ #{order[0]}</b>\n"
            f"👤 Покупатель: @{order[2]}\n"
            f"🏠 Адрес: {order[5]}\n"
            f"👕 Товар ID: {order[3]} (Размер {order[4]})\n"
            f"🕒 Дата: {order[7]}\n"
            f"🔄 Статус: <b>{order[6]}</b>"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Завершить", callback_data=f"status_{order[0]}_Завершён")
        builder.button(text="❌ Отменить", callback_data=f"status_{order[0]}_Отменён")
        builder.adjust(2)
        
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("status_"))
async def change_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_id = int(parts[1])
    new_status = parts[2]
    
    await update_order_status(order_id, new_status)
    await callback.answer(f"Статус заказа #{order_id} изменен на {new_status}")
    
    # Обновляем сообщение
    text = callback.message.text
    # Очень простой способ обновить статус в тексте (для MVP)
    if "Статус:" in text:
        text = text.split("Статус:")[0] + f"Статус: <b>{new_status}</b>"
    
    await callback.message.edit_text(text, parse_mode="HTML")

@router.message(Command("add_product"))
async def cmd_add_product(message: Message, state: FSMContext):
    await message.answer("📝 Введите <b>название товара</b>:", parse_mode="HTML")
    await state.set_state(AdminState.waiting_for_name)

@router.message(AdminState.waiting_for_name)
async def admin_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📝 Введите <b>описание товара</b>:", parse_mode="HTML")
    await state.set_state(AdminState.waiting_for_desc)

@router.message(AdminState.waiting_for_desc)
async def admin_add_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("💰 Введите <b>цену товара</b> (только число):", parse_mode="HTML")
    await state.set_state(AdminState.waiting_for_price)

@router.message(AdminState.waiting_for_price)
async def admin_add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
        await state.update_data(price=price)
        await message.answer("📏 Введите <b>доступные размеры</b> через запятую (например: S, M, L):", parse_mode="HTML")
        await state.set_state(AdminState.waiting_for_sizes)
    except ValueError:
        await message.answer("❌ Ошибка! Цена должна быть числом (например, 1500 или 1500.50).\nПопробуйте ещё раз:")

@router.message(AdminState.waiting_for_sizes)
async def admin_add_sizes(message: Message, state: FSMContext):
    await state.update_data(sizes=message.text)
    await message.answer("📸 Отправьте <b>фото товара</b> (или отправьте текст 'none', если фото нет):", parse_mode="HTML")
    await state.set_state(AdminState.waiting_for_photo)

@router.message(AdminState.waiting_for_photo, F.photo)
async def admin_add_photo(message: Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    await _save_product(message, state, bot, photo_id)

@router.message(AdminState.waiting_for_photo, F.text == "none")
async def admin_add_no_photo(message: Message, state: FSMContext, bot: Bot):
    await _save_product(message, state, bot, "none")

async def _save_product(message: Message, state: FSMContext, bot: Bot, photo_id: str):
    data = await state.get_data()
    
    loading_id = await show_loading_animation(bot, message.chat.id, "⏳ <i>Сохраняем товар в базу данных...</i>")
    
    await add_product(
        name=data['name'], 
        description=data['desc'], 
        price=data['price'], 
        sizes=data['sizes'], 
        photo_id=photo_id
    )
    
    await finish_loading_animation(bot, message.chat.id, loading_id)
    
    await message.answer("✅ <b>Товар успешно добавлен в каталог!</b>", parse_mode="HTML")
    await state.clear()
