"""Обработчики обновления записей."""
import os
import httpx
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import (
    get_back_keyboard,
    get_review_fields_keyboard,
    get_vacancy_fields_keyboard,
    get_article_fields_keyboard,
    get_case_fields_keyboard,
    get_stars_keyboard
)
from integrations.telegram.photo_handler import download_and_save_photo
from utils.logger import get_logger

logger = get_logger()

# Глобальная переменная для API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = "internal-bot-key-2026"

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


# FSM States для обновления
class UpdateVacancyForm(StatesGroup):
    entity_id = State()
    field = State()
    value = State()


class UpdateReviewForm(StatesGroup):
    entity_id = State()
    field = State()
    value = State()


class UpdateArticleForm(StatesGroup):
    entity_id = State()
    field = State()
    value = State()


class UpdateCaseForm(StatesGroup):
    entity_id = State()
    field = State()
    value = State()


async def handle_update_callback(callback: CallbackQuery, state: FSMContext):
    """Начало обновления записи - запрос ID."""
    entity_type = callback.data.replace("_update", "")
    await state.update_data(entity_type=entity_type)
    
    if entity_type == "vacancies":
        await state.set_state(UpdateVacancyForm.entity_id)
    elif entity_type == "reviews":
        await state.set_state(UpdateReviewForm.entity_id)
    elif entity_type == "articles":
        await state.set_state(UpdateArticleForm.entity_id)
    elif entity_type == "cases":
        await state.set_state(UpdateCaseForm.entity_id)
    
    await callback.message.edit_text(
        f"✏️ <b>Обновление записи</b>\n\nВведите ID записи:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(entity_type)
    )
    await callback.answer()


async def process_update_id(message: Message, state: FSMContext):
    """Показ кнопок выбора поля для обновления."""
    if not await admin_only(message):
        return
    
    try:
        entity_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    data = await state.get_data()
    entity_type = data["entity_type"]
    
    # Проверяем существование записи
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}",
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            entity_data = response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await message.answer(f"❌ Некорректный ID {entity_id}", reply_markup=get_back_keyboard(entity_type))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
        await state.clear()
        return
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
        await state.clear()
        return
    except Exception as e:
        logger.error(f"Ошибка проверки записи: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
        await state.clear()
        return
    
    await state.clear()
    
    # Показываем кнопки выбора поля
    if entity_type == "reviews":
        text = f"✏️ <b>Редактирование отзыва #{entity_id}</b>\n\n"
        text += f"👤 Имя: {entity_data.get('name', 'N/A')}\n"
        text += f"🏢 Компания: {entity_data.get('company', 'N/A')}\n"
        text += f"📝 Отзыв: {entity_data.get('review', 'N/A')[:50]}...\n"
        text += f"⭐ Звезды: {entity_data.get('stars', 'N/A')}\n"
        text += f"📷 Фото: {entity_data.get('photo', 'Нет')}\n\n"
        text += "Выберите поле для изменения:"
        await message.answer(text, parse_mode="HTML", reply_markup=get_review_fields_keyboard(entity_id))
    elif entity_type == "vacancies":
        text = f"✏️ <b>Редактирование вакансии #{entity_id}</b>\n\n"
        text += f"📌 Название: {entity_data.get('title', 'N/A')}\n"
        text += f"🔗 Ссылка: {entity_data.get('url', 'N/A')}\n"
        text += f"💼 Тип: {entity_data.get('employment_type', 'N/A')}\n"
        text += f"📄 Описание: {entity_data.get('description', 'N/A')[:50]}...\n\n"
        text += "Выберите поле для изменения:"
        await message.answer(text, parse_mode="HTML", reply_markup=get_vacancy_fields_keyboard(entity_id))
    elif entity_type == "articles":
        text = f"✏️ <b>Редактирование статьи #{entity_id}</b>\n\n"
        text += f"📌 Название: {entity_data.get('title', 'N/A')}\n"
        text += f"🔗 Ссылка: {entity_data.get('url', 'N/A')}\n"
        text += f"📝 Контент: {entity_data.get('content', 'N/A')[:50]}...\n"
        text += f"📷 Фото: {entity_data.get('photo', 'Нет')}\n\n"
        text += "Выберите поле для изменения:"
        await message.answer(text, parse_mode="HTML", reply_markup=get_article_fields_keyboard(entity_id))
    elif entity_type == "cases":
        text = f"✏️ <b>Редактирование кейса #{entity_id}</b>\n\n"
        text += f"📌 Название: {entity_data.get('name', 'N/A')}\n"
        text += f"📄 Описание: {entity_data.get('about', 'N/A')[:50]}...\n"
        text += f"🏷️ Теги: {', '.join(entity_data.get('tags', []))}\n"
        text += f"🖼️ Изображение: {entity_data.get('image', 'Нет')}\n\n"
        text += "Выберите поле для изменения:"
        await message.answer(text, parse_mode="HTML", reply_markup=get_case_fields_keyboard(entity_id))


async def handle_field_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора поля для редактирования через кнопку."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    # Формат: {entity}_edit_{id}_{field}
    parts = callback.data.split("_")
    
    logger.info(f"handle_field_edit_callback: callback_data={callback.data}, parts={parts}")
    
    if len(parts) == 4:  # review_edit_1_name
        entity_type = parts[0] + "s"  # review -> reviews
        entity_id = int(parts[2])
        field = parts[3]
    else:
        await callback.answer("❌ Ошибка формата данных")
        return
    
    logger.info(f"Редактирование: entity_type={entity_type}, entity_id={entity_id}, field={field}")
    
    # Для звезд показываем специальную клавиатуру
    if field == "stars":
        await callback.message.edit_text(
            f"⭐ Выберите количество звезд:",
            reply_markup=get_stars_keyboard(entity_id)
        )
        await callback.answer()
        return
    
    # Для остальных полей запрашиваем ввод
    field_names = {
        "name": "👤 Имя",
        "company": "🏢 Компания",
        "review": "📝 Текст отзыва",
        "photo": "📷 Фото (URL)",
        "title": "📌 Название",
        "url": "🔗 Ссылка",
        "content": "📝 Контент (Markdown)",
        "employment_type": "💼 Тип занятости",
        "description": "📄 Описание",
        "about": "📄 Описание",
        "tags": "🏷️ Теги (через запятую)",
        "image": "🖼️ Изображение (URL)"
    }
    
    await state.update_data(entity_type=entity_type, entity_id=entity_id, field=field)
    
    # Проверяем, что данные сохранились
    saved_data = await state.get_data()
    logger.info(f"Данные сохранены в state: {saved_data}")
    
    if entity_type == "reviews":
        await state.set_state(UpdateReviewForm.value)
    elif entity_type == "vacancies":
        await state.set_state(UpdateVacancyForm.value)
    elif entity_type == "articles":
        await state.set_state(UpdateArticleForm.value)
    elif entity_type == "cases":
        await state.set_state(UpdateCaseForm.value)
    
    current_state = await state.get_state()
    logger.info(f"Установлено состояние FSM: {current_state}")
    
    await callback.message.edit_text(
        f"✏️ Введите новое значение для поля {field_names.get(field, field)}:\n\n" +
        ("📷 Вы можете отправить фото или ввести URL\nВведите '-' чтобы удалить фото" if field in ["photo", "image"] else "") +
        ("📄 Вы можете отправить .md файл или ввести текст вручную" if field == "content" else "")
    )
    await callback.answer()


async def handle_update_stars_selection(callback: CallbackQuery):
    """Обработка выбора количества звезд при редактировании."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    # Формат: review_stars_{id}_{stars}
    parts = callback.data.split("_")
    entity_id = int(parts[2])
    stars = int(parts[3])
    
    logger.info(f"Обновление звезд: entity_id={entity_id}, stars={stars}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_URL}/api/v1/reviews/{entity_id}",
                json={"stars": stars},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        logger.info(f"Звезды успешно обновлены: {result}")
        await callback.message.edit_text(
            f"✅ Количество звезд обновлено на {stars}!",
            reply_markup=get_back_keyboard("reviews")
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при обновлении звезд: {e.response.status_code}")
        if e.response.status_code == 404:
            await callback.message.edit_text(
                f"❌ Отзыв с ID {entity_id} не найден",
                reply_markup=get_back_keyboard("reviews")
            )
        elif e.response.status_code == 400:
            await callback.message.edit_text(
                "❌ Некорректные данные",
                reply_markup=get_back_keyboard("reviews")
            )
        elif e.response.status_code == 422:
            await callback.message.edit_text(
                "❌ Ошибка валидации данных",
                reply_markup=get_back_keyboard("reviews")
            )
        else:
            await callback.message.edit_text(
                f"❌ Ошибка сервера (код {e.response.status_code})",
                reply_markup=get_back_keyboard("reviews")
            )
    except httpx.TimeoutException:
        logger.error("Timeout при обновлении звезд")
        await callback.message.edit_text(
            "❌ Превышено время ожидания. Попробуйте позже",
            reply_markup=get_back_keyboard("reviews")
        )
    except Exception as e:
        logger.error(f"Ошибка обновления звезд: {e}", exc_info=True)
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте позже",
            reply_markup=get_back_keyboard("reviews")
        )
    
    await callback.answer()


async def handle_edit_back_callback(callback: CallbackQuery):
    """Возврат к выбору поля."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    # Формат: review_edit_back_{id}
    parts = callback.data.split("_")
    entity_id = int(parts[3])
    entity_type = parts[0] + "s"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}",
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            entity_data = response.json()
    except Exception as e:
        logger.error(f"Ошибка получения данных: {e}")
        await callback.message.edit_text(
            "❌ Ошибка получения данных",
            reply_markup=get_back_keyboard(entity_type)
        )
        await callback.answer()
        return
    
    if entity_type == "reviews":
        text = f"✏️ <b>Редактирование отзыва #{entity_id}</b>\n\n"
        text += f"👤 Имя: {entity_data.get('name', 'N/A')}\n"
        text += f"🏢 Компания: {entity_data.get('company', 'N/A')}\n"
        text += f"📝 Отзыв: {entity_data.get('review', 'N/A')[:50]}...\n"
        text += f"⭐ Звезды: {entity_data.get('stars', 'N/A')}\n"
        text += f"📷 Фото: {entity_data.get('photo', 'Нет')}\n\n"
        text += "Выберите поле для изменения:"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_review_fields_keyboard(entity_id))
    
    await callback.answer()


async def process_update_value(message: Message, state: FSMContext):
    """Обновление записи."""
    if not await admin_only(message):
        return
    
    data = await state.get_data()
    
    # Проверяем наличие необходимых данных
    if not data or "entity_type" not in data or "entity_id" not in data or "field" not in data:
        logger.error(f"Отсутствуют данные в state: {data}")
        await message.answer("❌ Ошибка: данные не найдены. Попробуйте снова начать редактирование.")
        await state.clear()
        return
    
    entity_type = data["entity_type"]
    entity_id = data["entity_id"]
    field = data["field"]
    
    # Обработка MD файла для контента статьи
    if field == "content" and message.document and message.document.file_name and message.document.file_name.endswith('.md'):
        try:
            # Скачиваем MD файл
            file = await message.bot.get_file(message.document.file_id)
            file_content = await message.bot.download_file(file.file_path)
            value = file_content.read().decode('utf-8')
            logger.info(f"📄 MD файл загружен для обновления: {message.document.file_name}, размер: {len(value)} символов")
        except Exception as e:
            logger.error(f"Ошибка загрузки MD файла: {e}")
            await message.answer("❌ Ошибка загрузки MD файла. Попробуйте снова")
            return
    # Обработка фото
    elif field == "photo" and message.photo:
        # Если отправлено фото, берем самое большое
        photo = message.photo[-1]
        # Скачиваем и сохраняем фото
        value = await download_and_save_photo(message.bot, photo.file_id)
        logger.info(f"📷 ФОТО ОБРАБОТАНО для обновления {entity_type}/{entity_id}:")
        logger.info(f"   File ID: {photo.file_id}")
        logger.info(f"   Размер: {photo.width}x{photo.height}")
        logger.info(f"   Размер файла: {photo.file_size} байт")
        logger.info(f"   🔗 HTTP URL: {value}")
    elif field == "image" and message.photo:
        # Для кейсов
        photo = message.photo[-1]
        # Скачиваем и сохраняем фото
        value = await download_and_save_photo(message.bot, photo.file_id)
        logger.info(f"🖼️ ИЗОБРАЖЕНИЕ ОБРАБОТАНО для обновления {entity_type}/{entity_id}:")
        logger.info(f"   File ID: {photo.file_id}")
        logger.info(f"   Размер: {photo.width}x{photo.height}")
        logger.info(f"   Размер файла: {photo.file_size} байт")
        logger.info(f"   🔗 HTTP URL: {value}")
    elif message.text:
        value = message.text
        # Если пользователь ввел "-" для фото, устанавливаем None
        if field in ["photo", "image"] and value == "-":
            value = None
            logger.info(f"📷 Фото/изображение удалено для {entity_type}/{entity_id}")
        elif field in ["photo", "image"]:
            logger.info(f"📷 URL фото/изображения получен для {entity_type}/{entity_id}: {value}")
    else:
        await message.answer("❌ Отправьте текст или фото")
        return
    
    logger.info(f"Обновление {entity_type}/{entity_id}, поле {field}, значение: {value}")
    
    # Специальная обработка для некоторых полей
    if field == "stars":
        try:
            value = int(value)
            if value < 1 or value > 5:
                await message.answer("❌ Звезды должны быть от 1 до 5. Попробуйте снова:")
                return
        except ValueError:
            await message.answer("❌ Введите число от 1 до 5:")
            return
    elif field == "tags":
        value = [tag.strip() for tag in value.split(",")]
    
    # Формируем payload
    payload = {field: value}
    
    logger.info(f"Отправка PUT запроса: {API_URL}/api/v1/{entity_type}/{entity_id}, payload: {payload}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}",
                json=payload,
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        logger.info(f"Успешно обновлено: {result}")
        
        # Формируем сообщение об успехе
        success_msg = f"✅ Запись обновлена!\n\nID: {result['id']}\nПоле '{field}' обновлено"
        if field in ["photo", "image"] and value:
            success_msg += f"\n\n{'📷 Фото' if field == 'photo' else '🖼️ Изображение'} добавлено!"
        
        await message.answer(success_msg, reply_markup=get_back_keyboard(entity_type))
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при обновлении: {e.response.status_code}, {e.response.text}")
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await message.answer("❌ Некорректные данные. Проверьте введенную информацию", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 422:
            await message.answer("❌ Ошибка валидации данных", reply_markup=get_back_keyboard(entity_type))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
    except httpx.TimeoutException:
        logger.error("Timeout при обновлении")
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка обновления: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    
    await state.clear()


def set_api_url(url: str):
    """Установить API URL."""
    global API_URL
    API_URL = url
