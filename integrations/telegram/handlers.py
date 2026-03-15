"""Главный файл обработчиков Telegram бота."""
import httpx
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import (
    get_main_menu, get_entity_menu, get_cases_menu, 
    get_applications_menu, get_back_keyboard, get_pagination_keyboard
)
from integrations.telegram import create_handlers, update_handlers, action_handlers, application_handlers
from utils.logger import get_logger

logger = get_logger()

API_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


async def cmd_start(message: Message):
    """Обработчик команды /start."""
    if not await admin_only(message):
        return
    await message.answer(
        "👋 Добро пожаловать в панель управления контентом!\n\nВыберите раздел для работы:",
        reply_markup=get_main_menu()
    )


async def cmd_help(message: Message):
    """Обработчик команды /help."""
    if not await admin_only(message):
        return
    help_text = """
ℹ️ <b>Помощь по боту</b>

<b>Основные разделы:</b>
💼 Вакансии - управление вакансиями
⭐ Отзывы - управление отзывами клиентов
📰 Статьи - управление статьями и публикациями
💡 Кейсы - управление портфолио проектов

<b>Доступные действия:</b>
• Просмотр списка
• Создание новых записей
• Поиск по ID
• Обновление данных
• Изменение рейтинга
• Скрытие/показ записей
• Удаление

<b>Команды:</b>
/start - Главное меню
/help - Эта справка

Используйте кнопки для навигации!
    """
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu())


# Обработчики callback для главного меню
async def handle_menu_vacancies(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    await callback.message.edit_text(
        "💼 <b>Управление вакансиями</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_entity_menu("vacancies")
    )
    await callback.answer()


async def handle_menu_reviews(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    await callback.message.edit_text(
        "⭐ <b>Управление отзывами</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_entity_menu("reviews")
    )
    await callback.answer()


async def handle_menu_articles(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    await callback.message.edit_text(
        "📰 <b>Управление статьями</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_entity_menu("articles")
    )
    await callback.answer()


async def handle_menu_cases(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    await callback.message.edit_text(
        "💡 <b>Управление кейсами</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_cases_menu()
    )
    await callback.answer()


async def handle_menu_applications(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    await callback.message.edit_text(
        "📨 <b>Управление заявками</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_applications_menu()
    )
    await callback.answer()


async def handle_menu_help(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    help_text = """
ℹ️ <b>Помощь по боту</b>

<b>Основные разделы:</b>
💼 Вакансии - управление вакансиями
⭐ Отзывы - управление отзывами клиентов
📰 Статьи - управление статьями и публикациями
💡 Кейсы - управление портфолио проектов

<b>Доступные действия:</b>
• Просмотр списка
• Создание новых записей
• Поиск по ID
• Обновление данных
• Изменение рейтинга
• Скрытие/показ записей
• Удаление

<b>Команды:</b>
/start - Главное меню
/help - Эта справка

Используйте кнопки для навигации!
    """
    await callback.message.edit_text(help_text, parse_mode="HTML", reply_markup=get_main_menu())
    await callback.answer()


# Обработчики callback для списков
async def handle_list_callback(callback: CallbackQuery):
    """Обработка просмотра списка с пагинацией."""
    # Проверяем, есть ли номер страницы в callback_data
    if "_page_" in callback.data:
        parts = callback.data.split("_page_")
        entity_type = parts[0]
        page = int(parts[1])
    else:
        entity_type = callback.data.replace("_list", "")
        page = 1
    
    items_per_page = 7  # Показываем 7 элементов на странице
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/v1/{entity_type}", headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            items = response.json()
        
        if not items:
            await callback.message.edit_text("📭 Список пуст", reply_markup=get_back_keyboard(entity_type))
            await callback.answer()
            return
        
        # Вычисляем пагинацию
        total_items = len(items)
        total_pages = (total_items + items_per_page - 1) // items_per_page  # Округление вверх
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        page_items = items[start_idx:end_idx]
        
        text = f"📋 <b>Список ({total_items} шт.) - Страница {page}/{total_pages}</b>\n\n"
        
        for item in page_items:
            if entity_type == "vacancies":
                hidden = "🔒 Скрыто" if item.get('is_hidden') else "👁 Видно"
                desc = item.get('description') or 'Нет описания'
                desc_short = (desc[:100] + '...') if desc and len(desc) > 100 else desc
                text += f"🔹 <b>{item['title']}</b>\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']} | {hidden}\n"
                text += f"   Тип: {item['employment_type']}\n"
                text += f"   URL: {item['url']}\n"
                text += f"   Описание: {desc_short}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
            elif entity_type == "reviews":
                hidden = "🔒 Скрыто" if item.get('is_hidden') else "👁 Видно"
                review_text = item.get('review') or ''
                review_short = (review_text[:100] + '...') if review_text and len(review_text) > 100 else review_text
                text += f"🔹 <b>{item['name']}</b> ({item['company']})\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']} | Звезды: {'⭐' * item['stars']} | {hidden}\n"
                text += f"   Отзыв: {review_short}\n"
                text += f"   Фото: {'✅ Есть' if item.get('photo') else '❌ Нет'}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
            elif entity_type == "articles":
                hidden = "🔒 Скрыто" if item.get('is_hidden') else "👁 Видно"
                text += f"🔹 <b>{item['title']}</b>\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']} | {hidden}\n"
                text += f"   URL: {item['url']}\n"
                text += f"   Фото: {'✅ Есть' if item.get('photo') else '❌ Нет'}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
            elif entity_type == "cases":
                hidden = "🔒 Скрыто" if item.get('is_hidden') else "👁 Видно"
                fresh = "🆕 Свежий" if item.get('is_fresh') else ""
                about_text = item.get('about') or ''
                about_short = (about_text[:100] + '...') if about_text and len(about_text) > 100 else about_text
                text += f"🔹 <b>{item['name']}</b> {fresh}\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']} | {hidden}\n"
                text += f"   Описание: {about_short}\n"
                text += f"   Теги: {', '.join(item.get('tags', []))}\n"
                text += f"   Изображение: {item.get('image', 'Нет')}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
        
        # Используем пагинацию если больше 7 элементов
        if total_pages > 1:
            keyboard = get_pagination_keyboard(entity_type, page, total_pages)
        else:
            keyboard = get_back_keyboard(entity_type)
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await callback.message.edit_text("❌ Раздел не найден", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await callback.message.edit_text("❌ Некорректный запрос", reply_markup=get_back_keyboard(entity_type))
        else:
            await callback.message.edit_text(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
    except httpx.TimeoutException:
        await callback.message.edit_text("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка получения списка {entity_type}: {e}")
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    await callback.answer()


async def handle_hidden_callback(callback: CallbackQuery):
    """Обработка просмотра скрытых элементов."""
    entity_type = callback.data.replace("_hidden", "")
    
    try:
        # Получаем все элементы
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/v1/{entity_type}", headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            all_items = response.json()
        
        # Фильтруем только скрытые
        hidden_items = [item for item in all_items if item.get('is_hidden', False)]
        
        if not hidden_items:
            await callback.message.edit_text("📭 Нет скрытых элементов", reply_markup=get_back_keyboard(entity_type))
            await callback.answer()
            return
        
        text = f"🔒 <b>Скрытые элементы ({len(hidden_items)} шт.)</b>\n\n"
        
        for item in hidden_items[:10]:  # Показываем первые 10
            if entity_type == "vacancies":
                desc = item.get('description') or 'Нет описания'
                desc_short = (desc[:100] + '...') if desc and len(desc) > 100 else desc
                text += f"🔹 <b>{item['title']}</b> 🔒\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']}\n"
                text += f"   Тип: {item['employment_type']}\n"
                text += f"   URL: {item['url']}\n"
                text += f"   Описание: {desc_short}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
            elif entity_type == "reviews":
                review_text = item.get('review') or ''
                review_short = (review_text[:100] + '...') if review_text and len(review_text) > 100 else review_text
                text += f"🔹 <b>{item['name']}</b> ({item['company']}) 🔒\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']} | Звезды: {'⭐' * item['stars']}\n"
                text += f"   Отзыв: {review_short}\n"
                text += f"   Фото: {'✅ Есть' if item.get('photo') else '❌ Нет'}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
            elif entity_type == "articles":
                text += f"🔹 <b>{item['title']}</b> 🔒\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']}\n"
                text += f"   URL: {item['url']}\n"
                text += f"   Фото: {'✅ Есть' if item.get('photo') else '❌ Нет'}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
            elif entity_type == "cases":
                fresh = "🆕 Свежий" if item.get('is_fresh') else ""
                about_text = item.get('about') or ''
                about_short = (about_text[:100] + '...') if about_text and len(about_text) > 100 else about_text
                text += f"🔹 <b>{item['name']}</b> {fresh} 🔒\n"
                text += f"   ID: {item['id']} | Рейтинг: {item['rating']}\n"
                text += f"   Описание: {about_short}\n"
                text += f"   Теги: {', '.join(item.get('tags', []))}\n"
                text += f"   Изображение: {item.get('image', 'Нет')}\n"
                text += f"   Создано: {item['created_at'][:10]}\n\n"
        
        if len(hidden_items) > 10:
            text += f"\n... и еще {len(hidden_items) - 10} скрытых записей"
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard(entity_type))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await callback.message.edit_text("❌ Раздел не найден", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await callback.message.edit_text("❌ Некорректный запрос", reply_markup=get_back_keyboard(entity_type))
        else:
            await callback.message.edit_text(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
    except httpx.TimeoutException:
        await callback.message.edit_text("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка получения скрытых {entity_type}: {e}")
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    await callback.answer()


async def handle_fresh_cases_callback(callback: CallbackQuery):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/v1/cases/fresh", headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            items = response.json()
        
        if not items:
            await callback.message.edit_text("📭 Нет свежих кейсов", reply_markup=get_back_keyboard("cases"))
            return
        
        text = f"🆕 <b>Свежие кейсы ({len(items)} шт.)</b>\n\n"
        for item in items:
            hidden = "🔒 Скрыто" if item.get('is_hidden') else "👁 Видно"
            about_text = item.get('about') or ''
            about_short = (about_text[:100] + '...') if about_text and len(about_text) > 100 else about_text
            text += f"🔹 <b>{item['name']}</b> 🆕\n"
            text += f"   ID: {item['id']} | Рейтинг: {item['rating']} | {hidden}\n"
            text += f"   Описание: {about_short}\n"
            text += f"   Теги: {', '.join(item.get('tags', []))}\n"
            text += f"   Изображение: {item.get('image', 'Нет')}\n"
            text += f"   Создано: {item['created_at'][:10]}\n\n"
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard("cases"))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await callback.message.edit_text("❌ Раздел не найден", reply_markup=get_back_keyboard("cases"))
        elif e.response.status_code == 400:
            await callback.message.edit_text("❌ Некорректный запрос", reply_markup=get_back_keyboard("cases"))
        else:
            await callback.message.edit_text(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("cases"))
    except httpx.TimeoutException:
        await callback.message.edit_text("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("cases"))
    except Exception as e:
        logger.error(f"Ошибка получения свежих кейсов: {e}")
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("cases"))
    await callback.answer()


async def handle_main_menu_callback(callback: CallbackQuery):
    await callback.message.edit_text("🏠 Главное меню\n\nВыберите раздел:", reply_markup=get_main_menu())
    await callback.answer()


async def handle_entity_menu_callback(callback: CallbackQuery):
    entity_type = callback.data.replace("_menu", "")
    menus = {
        "vacancies": ("💼 <b>Управление вакансиями</b>", get_entity_menu("vacancies")),
        "reviews": ("⭐ <b>Управление отзывами</b>", get_entity_menu("reviews")),
        "articles": ("📰 <b>Управление статьями</b>", get_entity_menu("articles")),
        "cases": ("💡 <b>Управление кейсами</b>", get_cases_menu())
    }
    if entity_type in menus:
        text, keyboard = menus[entity_type]
        await callback.message.edit_text(f"{text}\n\nВыберите действие:", parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


def register_handlers(dp: Dispatcher, api_url: str):
    """Регистрация всех обработчиков."""
    global API_URL
    API_URL = api_url
    create_handlers.set_api_url(api_url)
    update_handlers.set_api_url(api_url)
    action_handlers.set_api_url(api_url)
    application_handlers.set_api_url(api_url)
    
    # Команды
    dp.message.register(cmd_start, Command("start"))
    
    # Callback для главного меню
    dp.callback_query.register(handle_menu_vacancies, F.data == "menu_vacancies")
    dp.callback_query.register(handle_menu_reviews, F.data == "menu_reviews")
    dp.callback_query.register(handle_menu_articles, F.data == "menu_articles")
    dp.callback_query.register(handle_menu_cases, F.data == "menu_cases")
    dp.callback_query.register(handle_menu_applications, F.data == "menu_applications")
    dp.callback_query.register(handle_menu_help, F.data == "menu_help")
    
    # Callback handlers для создания отзывов через кнопки (ДОЛЖНЫ БЫТЬ ПЕРЕД ОБЩИМИ!)
    dp.callback_query.register(create_handlers.handle_name_selection, F.data.startswith("create_name_"))
    dp.callback_query.register(create_handlers.handle_company_selection, F.data.startswith("create_company_"))
    dp.callback_query.register(create_handlers.handle_review_template_selection, F.data.startswith("create_review_"))
    dp.callback_query.register(create_handlers.handle_create_stars_selection, F.data.startswith("create_stars_"))
    dp.callback_query.register(create_handlers.handle_photo_skip, F.data.startswith("create_photo_"))
    
    # Callback handlers для редактирования полей через кнопки (ДОЛЖНЫ БЫТЬ ПЕРЕД ОБЩИМИ!)
    dp.callback_query.register(update_handlers.handle_update_stars_selection, F.data.startswith("review_stars_"))
    dp.callback_query.register(update_handlers.handle_edit_back_callback, F.data.contains("_edit_back_"))
    dp.callback_query.register(update_handlers.handle_field_edit_callback, F.data.contains("_edit_"))
    
    # Callback handlers (общие)
    dp.callback_query.register(handle_list_callback, F.data.endswith("_list"))
    dp.callback_query.register(handle_list_callback, F.data.contains("_page_"))  # Для пагинации
    dp.callback_query.register(handle_hidden_callback, F.data.endswith("_hidden"))  # Для скрытых элементов
    dp.callback_query.register(handle_fresh_cases_callback, F.data == "cases_fresh")
    dp.callback_query.register(handle_main_menu_callback, F.data == "main_menu")
    dp.callback_query.register(handle_entity_menu_callback, F.data.endswith("_menu"))
    dp.callback_query.register(create_handlers.handle_create_callback, F.data.endswith("_create"))
    dp.callback_query.register(action_handlers.handle_get_callback, F.data.endswith("_get"))
    dp.callback_query.register(action_handlers.handle_rating_callback, F.data.endswith("_rating"))
    dp.callback_query.register(action_handlers.handle_hide_callback, F.data.endswith("_hide"))
    dp.callback_query.register(action_handlers.handle_delete_callback, F.data.endswith("_delete"))
    dp.callback_query.register(action_handlers.handle_mark_fresh_callback, F.data == "cases_mark_fresh")
    dp.callback_query.register(action_handlers.handle_quick_visibility_toggle, F.data.startswith(("hide_", "show_")))  # Быстрое переключение видимости
    dp.callback_query.register(update_handlers.handle_update_callback, F.data.endswith("_update"))
    
    # FSM handlers для создания
    dp.message.register(create_handlers.process_vacancy_title, create_handlers.VacancyForm.title)
    dp.message.register(create_handlers.process_vacancy_url, create_handlers.VacancyForm.url)
    dp.message.register(create_handlers.process_vacancy_employment, create_handlers.VacancyForm.employment_type)
    dp.message.register(create_handlers.process_vacancy_description, create_handlers.VacancyForm.description)
    
    dp.message.register(create_handlers.process_review_name, create_handlers.ReviewForm.name)
    dp.message.register(create_handlers.process_review_company, create_handlers.ReviewForm.company)
    dp.message.register(create_handlers.process_review_text, create_handlers.ReviewForm.review)
    dp.message.register(create_handlers.process_review_stars, create_handlers.ReviewForm.stars)
    dp.message.register(create_handlers.process_review_photo, create_handlers.ReviewForm.photo)
    
    dp.message.register(create_handlers.process_article_title, create_handlers.ArticleForm.title)
    dp.message.register(create_handlers.process_article_url, create_handlers.ArticleForm.url)
    dp.message.register(create_handlers.process_article_photo, create_handlers.ArticleForm.photo)
    
    dp.message.register(create_handlers.process_case_name, create_handlers.CaseForm.name)
    dp.message.register(create_handlers.process_case_about, create_handlers.CaseForm.about)
    dp.message.register(create_handlers.process_case_tags, create_handlers.CaseForm.tags)
    dp.message.register(create_handlers.process_case_image, create_handlers.CaseForm.image)
    
    # FSM handlers для действий
    dp.message.register(action_handlers.process_get_by_id, action_handlers.GetByIdForm.entity_id)
    dp.message.register(action_handlers.process_rating_id, action_handlers.UpdateRatingForm.entity_id)
    dp.message.register(action_handlers.process_rating_value, action_handlers.UpdateRatingForm.rating_value)
    dp.message.register(action_handlers.process_hide_toggle, action_handlers.HideForm.entity_id)
    dp.message.register(action_handlers.process_delete_id, action_handlers.DeleteForm.entity_id)
    dp.message.register(action_handlers.process_mark_fresh, action_handlers.MarkFreshForm.case_id)
    
    # FSM handlers для обновления
    dp.message.register(update_handlers.process_update_id, update_handlers.UpdateVacancyForm.entity_id)
    dp.message.register(update_handlers.process_update_id, update_handlers.UpdateReviewForm.entity_id)
    dp.message.register(update_handlers.process_update_id, update_handlers.UpdateArticleForm.entity_id)
    dp.message.register(update_handlers.process_update_id, update_handlers.UpdateCaseForm.entity_id)
    
    dp.message.register(update_handlers.process_update_value, update_handlers.UpdateVacancyForm.value)
    dp.message.register(update_handlers.process_update_value, update_handlers.UpdateReviewForm.value)
    dp.message.register(update_handlers.process_update_value, update_handlers.UpdateArticleForm.value)
    dp.message.register(update_handlers.process_update_value, update_handlers.UpdateCaseForm.value)

    # Callback handlers для заявок
    dp.callback_query.register(application_handlers.handle_applications_list_callback, F.data == "applications_list")
    dp.callback_query.register(application_handlers.handle_applications_new_callback, F.data == "applications_new")
    dp.callback_query.register(application_handlers.handle_application_status_callback, F.data == "applications_status")
    
    # FSM handlers для заявок
    dp.message.register(application_handlers.process_application_id, application_handlers.ApplicationStatusForm.application_id)
    dp.message.register(application_handlers.process_application_status, application_handlers.ApplicationStatusForm.status)
