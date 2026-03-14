"""Клавиатуры для Telegram бота."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💼 Вакансии", callback_data="menu_vacancies"),
            InlineKeyboardButton(text="⭐ Отзывы", callback_data="menu_reviews"),
        ],
        [
            InlineKeyboardButton(text="📰 Статьи", callback_data="menu_articles"),
            InlineKeyboardButton(text="💡 Кейсы", callback_data="menu_cases"),
        ],
        [
            InlineKeyboardButton(text="📨 Заявки", callback_data="menu_applications"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu_help"),
        ],
    ])
    return keyboard


def get_entity_menu(entity_type: str) -> InlineKeyboardMarkup:
    """Меню действий для сущности."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Список", callback_data=f"{entity_type}_list"),
            InlineKeyboardButton(text="➕ Создать", callback_data=f"{entity_type}_create"),
        ],
        [
            InlineKeyboardButton(text="🔍 Найти по ID", callback_data=f"{entity_type}_get"),
            InlineKeyboardButton(text="✏️ Обновить", callback_data=f"{entity_type}_update"),
        ],
        [
            InlineKeyboardButton(text="⭐ Рейтинг", callback_data=f"{entity_type}_rating"),
            InlineKeyboardButton(text="👁️ Скрыть/Показать", callback_data=f"{entity_type}_hide"),
        ],
        [
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"{entity_type}_delete"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
        ],
    ])
    return keyboard


def get_cases_menu() -> InlineKeyboardMarkup:
    """Меню для кейсов (с дополнительной кнопкой)."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Список", callback_data="cases_list"),
            InlineKeyboardButton(text="🆕 Свежие", callback_data="cases_fresh"),
        ],
        [
            InlineKeyboardButton(text="➕ Создать", callback_data="cases_create"),
            InlineKeyboardButton(text="🔍 Найти по ID", callback_data="cases_get"),
        ],
        [
            InlineKeyboardButton(text="✏️ Обновить", callback_data="cases_update"),
            InlineKeyboardButton(text="⭐ Рейтинг", callback_data="cases_rating"),
        ],
        [
            InlineKeyboardButton(text="🌟 Пометить свежим", callback_data="cases_mark_fresh"),
            InlineKeyboardButton(text="👁️ Скрыть/Показать", callback_data="cases_hide"),
        ],
        [
            InlineKeyboardButton(text="🗑️ Удалить", callback_data="cases_delete"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
        ],
    ])
    return keyboard


def get_applications_menu() -> InlineKeyboardMarkup:
    """Меню для заявок."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Все заявки", callback_data="applications_list"),
            InlineKeyboardButton(text="🆕 Новые", callback_data="applications_new"),
        ],
        [
            InlineKeyboardButton(text="🔄 Изменить статус", callback_data="applications_status"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
        ],
    ])
    return keyboard


def get_pagination_keyboard(entity_type: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура пагинации."""
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{entity_type}_page_{page-1}"))
    
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"{entity_type}_page_{page+1}"))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])
    return keyboard


def get_item_actions_keyboard(entity_type: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с конкретным элементом."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"{entity_type}_edit_{item_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"{entity_type}_del_{item_id}"),
        ],
        [
            InlineKeyboardButton(text="⭐ Рейтинг", callback_data=f"{entity_type}_rate_{item_id}"),
            InlineKeyboardButton(text="👁️ Скрыть", callback_data=f"{entity_type}_hide_{item_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data=f"{entity_type}_list"),
        ],
    ])
    return keyboard


def get_confirm_keyboard(entity_type: str, action: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"{entity_type}_{action}_confirm_{item_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"{entity_type}_list"),
        ],
    ])
    return keyboard


def get_back_keyboard(entity_type: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"{entity_type}_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])
    return keyboard
