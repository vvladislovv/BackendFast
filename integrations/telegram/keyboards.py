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
    ])
    return keyboard


def get_entity_menu(entity_type: str) -> InlineKeyboardMarkup:
    """Меню действий для сущности."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Список", callback_data=f"{entity_type}_list"),
            InlineKeyboardButton(text="🔒 Скрытые", callback_data=f"{entity_type}_hidden"),
        ],
        [
            InlineKeyboardButton(text="➕ Создать", callback_data=f"{entity_type}_create"),
            InlineKeyboardButton(text="🔍 Найти по ID", callback_data=f"{entity_type}_get"),
        ],
        [
            InlineKeyboardButton(text="✏️ Обновить", callback_data=f"{entity_type}_update"),
            InlineKeyboardButton(text="⭐ Рейтинг", callback_data=f"{entity_type}_rating"),
        ],
        [
            InlineKeyboardButton(text="👁️ Скрыть/Показать", callback_data=f"{entity_type}_hide"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"{entity_type}_delete"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
        ],
    ])
    return keyboard


def get_cases_menu() -> InlineKeyboardMarkup:
    """Меню для кейсов (с дополнительной кнопкой)."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Список", callback_data="cases_list"),
            InlineKeyboardButton(text="🔒 Скрытые", callback_data="cases_hidden"),
        ],
        [
            InlineKeyboardButton(text="🆕 Свежие", callback_data="cases_fresh"),
            InlineKeyboardButton(text="➕ Создать", callback_data="cases_create"),
        ],
        [
            InlineKeyboardButton(text="🔍 Найти по ID", callback_data="cases_get"),
            InlineKeyboardButton(text="✏️ Обновить", callback_data="cases_update"),
        ],
        [
            InlineKeyboardButton(text="⭐ Рейтинг", callback_data="cases_rating"),
            InlineKeyboardButton(text="🌟 Пометить свежим", callback_data="cases_mark_fresh"),
        ],
        [
            InlineKeyboardButton(text="👁️ Скрыть/Показать", callback_data="cases_hide"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data="cases_delete"),
        ],
        [
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
    
    buttons.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"{entity_type}_page_{page+1}"))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="🔙 Назад к меню", callback_data=f"{entity_type}_menu")],
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


def get_review_fields_keyboard(review_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования отзыва."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Имя", callback_data=f"review_edit_{review_id}_name")],
        [InlineKeyboardButton(text="🏢 Компания", callback_data=f"review_edit_{review_id}_company")],
        [InlineKeyboardButton(text="📝 Текст отзыва", callback_data=f"review_edit_{review_id}_review")],
        [InlineKeyboardButton(text="⭐ Звезды (1-5)", callback_data=f"review_edit_{review_id}_stars")],
        [InlineKeyboardButton(text="📷 Фото", callback_data=f"review_edit_{review_id}_photo")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="reviews_menu")],
    ])
    return keyboard


def get_vacancy_fields_keyboard(vacancy_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования вакансии."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Название", callback_data=f"vacancy_edit_{vacancy_id}_title")],
        [InlineKeyboardButton(text="🔗 Ссылка", callback_data=f"vacancy_edit_{vacancy_id}_url")],
        [InlineKeyboardButton(text="💼 Тип занятости", callback_data=f"vacancy_edit_{vacancy_id}_employment_type")],
        [InlineKeyboardButton(text="📄 Описание", callback_data=f"vacancy_edit_{vacancy_id}_description")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="vacancies_menu")],
    ])
    return keyboard


def get_article_fields_keyboard(article_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования статьи."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Название", callback_data=f"article_edit_{article_id}_title")],
        [InlineKeyboardButton(text="🔗 Ссылка", callback_data=f"article_edit_{article_id}_url")],
        [InlineKeyboardButton(text="📷 Фото", callback_data=f"article_edit_{article_id}_photo")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="articles_menu")],
    ])
    return keyboard


def get_case_fields_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования кейса."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Название", callback_data=f"case_edit_{case_id}_name")],
        [InlineKeyboardButton(text="📄 Описание", callback_data=f"case_edit_{case_id}_about")],
        [InlineKeyboardButton(text="🏷️ Теги", callback_data=f"case_edit_{case_id}_tags")],
        [InlineKeyboardButton(text="🖼️ Изображение", callback_data=f"case_edit_{case_id}_image")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="cases_menu")],
    ])
    return keyboard


def get_stars_keyboard(review_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора количества звезд."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 1", callback_data=f"review_stars_{review_id}_1"),
            InlineKeyboardButton(text="⭐⭐ 2", callback_data=f"review_stars_{review_id}_2"),
            InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data=f"review_stars_{review_id}_3"),
        ],
        [
            InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data=f"review_stars_{review_id}_4"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data=f"review_stars_{review_id}_5"),
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"review_edit_back_{review_id}")],
    ])
    return keyboard


def get_create_stars_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора количества звезд при создании."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 1", callback_data="create_stars_1"),
            InlineKeyboardButton(text="⭐⭐ 2", callback_data="create_stars_2"),
            InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data="create_stars_3"),
        ],
        [
            InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data="create_stars_4"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data="create_stars_5"),
        ],
    ])
    return keyboard








def get_photo_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска фото."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="create_photo_skip")],
        [InlineKeyboardButton(text="📷 Загрузить фото", callback_data="create_photo_upload")],
    ])
    return keyboard


def get_visibility_keyboard(entity_type: str, entity_id: int, is_hidden: bool) -> InlineKeyboardMarkup:
    """Клавиатура для изменения видимости."""
    if is_hidden:
        action_text = "👁️ Показать"
        action_data = f"show_{entity_type}_{entity_id}"
    else:
        action_text = "🔒 Скрыть"
        action_data = f"hide_{entity_type}_{entity_id}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=action_text, callback_data=action_data)],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"{entity_type}_menu")],
    ])
    return keyboard
