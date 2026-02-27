from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from locales.manager import get_text

def get_main_kb(is_admin: bool = False, lang: str = "ru") -> ReplyKeyboardMarkup:
    """Главное меню с Reply-кнопками."""
    keyboard=[
        [KeyboardButton(text=get_text("catalog", lang))],
        [KeyboardButton(text=get_text("help", lang)), KeyboardButton(text=get_text("manager", lang))]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text=get_text("admin_panel", lang))])
        
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def get_catalog_kb(products, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура с товарами из БД (inline)."""
    builder = InlineKeyboardBuilder()
    for prod in products:
        # prod: (id, name, desc, price, sizes, photo_id)
        builder.button(text=prod[1], callback_data=f"prod_{prod[0]}")
    builder.button(text=get_text("close", lang), callback_data="close_catalog")
    builder.adjust(1)
    return builder.as_markup()

def get_product_sizes_kb(product_id: int, sizes: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Генерация Inline-кнопок для выбора размера."""
    builder = InlineKeyboardBuilder()
    for size in sizes.split(','):
        size = size.strip()
        builder.button(text=size, callback_data=f"size_{product_id}_{size}")
    builder.button(text=get_text("back_to_catalog", lang), callback_data="catalog")
    builder.adjust(2) # Размеры по 2 в ряд
    return builder.as_markup()

def get_buy_kb(product_id: int, size: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка покупки после выбора размера."""
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("buy", lang), callback_data=f"buy_{product_id}_{size}")
    builder.button(text=get_text("back", lang), callback_data=f"prod_{product_id}")
    builder.adjust(1)
    return builder.as_markup()
