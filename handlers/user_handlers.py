from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
import os
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards.user_kbs import get_main_kb, get_catalog_kb, get_product_sizes_kb, get_buy_kb
from database.db import get_products, get_product, create_order
from utils.wait_states import show_loading_animation, finish_loading_animation
from states.user_states import OrderState
from filters.admin import IsAdmin
from locales.manager import get_text
import logging

router = Router()

def get_lang(event: Message | CallbackQuery) -> str:
    """Helper to get user language."""
    if event.from_user.language_code == "en":
        return "en"
    return "ru"

@router.message(CommandStart())
async def cmd_start(message: Message):
    lang = get_lang(message)
    is_admin = IsAdmin()(message)
    await message.answer(
        get_text("welcome", lang),
        reply_markup=get_main_kb(is_admin, lang),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["🛍 Каталог", "🛍 Catalog"]))
@router.callback_query(F.data == "catalog")
async def show_catalog(event: Message | CallbackQuery, bot: Bot):
    lang = get_lang(event)
    products = await get_products()
    
    text = get_text("catalog_title", lang)
    kb = get_catalog_kb(products, lang)
    
    if isinstance(event, Message):
        if not products:
            await event.answer(get_text("catalog_empty", lang))
            return
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        # Если это callback (нажатие кнопки)
        if not products:
            await event.message.edit_text(get_text("catalog_empty", lang))
            await event.answer()
            return
        
        # Если сообщение содержит фото, его нельзя редактировать в текст - нужно удалить и отправить заново
        if event.message.photo:
            try:
                await event.message.delete()
            except Exception as e:
                logging.error(f"Error deleting photo message: {e}")
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        else:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            
        await event.answer()

@router.message(F.text.in_(["ℹ️ Помощь", "ℹ️ Help"]))
async def cmd_help(message: Message):
    lang = get_lang(message)
    await message.answer(get_text("help_text", lang), parse_mode="HTML")

@router.message(F.text.in_(["📞 Менеджер", "📞 Manager"]))
async def cmd_manager(message: Message):
    lang = get_lang(message)
    await message.answer(get_text("manager_text", lang), parse_mode="HTML")

@router.callback_query(F.data == "close_catalog")
async def close_catalog(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        logging.error(f"Error deleting message in close_catalog: {e}")
    await callback.answer()

@router.callback_query(F.data.startswith("prod_"))
async def show_product(callback: CallbackQuery, bot: Bot):
    lang = get_lang(callback)
    product_id = int(callback.data.split("_")[1])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer(get_text("product_not_found", lang), show_alert=True)
        return
        
    _, name, desc, price, sizes, photo_id = product
    price_text = get_text("price", lang)
    text = f"👕 <b>{name}</b>\n\n📝 <i>{desc}</i>\n\n💰 <b>{price_text}:</b> {price}$"
    
    kb = get_product_sizes_kb(product_id, sizes, lang)
    
    if photo_id and photo_id != "none":
        # Удаляем предыдущее сообщение с текстом (если было) для чистоты UI
        try:
            await callback.message.delete()
        except Exception as e:
            logging.error(f"Error deleting message in show_product: {e}")
            
        # Определяем, это путь к файлу или URL/file_id
        photo = photo_id
        if os.path.exists(photo_id):
            photo = FSInputFile(photo_id)
            
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo,
            caption=text + f"\n\n{get_text('select_size', lang)}",
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
        await callback.message.edit_text(
            text + f"\n\n{get_text('select_size', lang)}", 
            reply_markup=kb,
            parse_mode="HTML"
        )
    await callback.answer()

@router.callback_query(F.data.startswith("size_"))
async def select_size(callback: CallbackQuery):
    lang = get_lang(callback)
    parts = callback.data.split("_")
    product_id = int(parts[1])
    size = parts[2]
    
    product = await get_product(product_id)
    if not product:
        await callback.answer(get_text("product_not_found", lang), show_alert=True)
        return
        
    _, name, desc, price, sizes, photo_id = product
    price_text = get_text("price", lang)
    sel_size_text = get_text("selected_size", lang, size=size)
    text = f"👕 <b>{name}</b>\n\n📝 <i>{desc}</i>\n💰 <b>{price_text}:</b> {price}$\n\n{sel_size_text}"
    
    kb = get_buy_kb(product_id, size, lang)
    
    # Обновляем сообщение (показываем кнопку купить и выбранный размер)
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
        
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback)
    parts = callback.data.split("_")
    product_id = int(parts[1])
    size = parts[2]
    
    await state.update_data(product_id=product_id, size=size, lang=lang)
    
    # Удаляем карточку с кнопками, чтобы очистить чат
    await callback.message.delete()
    
    await callback.message.answer(
        get_text("enter_address", lang), 
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_address)
    await callback.answer()

@router.message(OrderState.waiting_for_address)
async def process_address(message: Message, state: FSMContext, bot: Bot):
    address = message.text
    data = await state.get_data()
    product_id = data['product_id']
    size = data['size']
    lang = data.get('lang', 'ru')
    
    loading_id = await show_loading_animation(bot, message.chat.id, get_text("loading_order", lang))
    
    username = message.from_user.username or "Unknown"
    user_id = message.from_user.id
    
    order_id = await create_order(user_id, username, product_id, size, address)
    
    await finish_loading_animation(bot, message.chat.id, loading_id)
    
    is_admin = IsAdmin()(message)
    await message.answer(
        get_text("order_success", lang, order_id=order_id), 
        parse_mode="HTML",
        reply_markup=get_main_kb(is_admin, lang)
    )
    
    await state.clear()
