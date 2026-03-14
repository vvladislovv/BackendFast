"""Обработчики обновления записей."""
import httpx
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import get_back_keyboard
from utils.logger import get_logger

logger = get_logger()

# Глобальная переменная для API URL
API_URL = "http://localhost:8000"
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
    """Начало обновления записи."""
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
    """Запрос поля для обновления."""
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
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
            await state.clear()
            return
    
    await state.update_data(entity_id=entity_id)
    
    # Переходим к выбору поля
    if entity_type == "vacancies":
        await state.set_state(UpdateVacancyForm.field)
        fields_text = "title - название\nurl - ссылка\nemployment_type - тип занятости\ndescription - описание"
    elif entity_type == "reviews":
        await state.set_state(UpdateReviewForm.field)
        fields_text = "name - имя\ncompany - компания\nreview - текст отзыва\nstars - звезды (1-5)\nphoto - фото"
    elif entity_type == "articles":
        await state.set_state(UpdateArticleForm.field)
        fields_text = "title - название\nurl - ссылка\nphoto - фото"
    elif entity_type == "cases":
        await state.set_state(UpdateCaseForm.field)
        fields_text = "name - название\nabout - описание\ntags - теги (через запятую)\nimage - изображение"
    
    await message.answer(
        f"Выберите поле для обновления:\n\n{fields_text}\n\nВведите название поля:"
    )


async def process_update_field(message: Message, state: FSMContext):
    """Запрос нового значения."""
    if not await admin_only(message):
        return
    
    field = message.text.strip().lower()
    data = await state.get_data()
    entity_type = data["entity_type"]
    
    # Валидация поля
    valid_fields = {
        "vacancies": ["title", "url", "employment_type", "description"],
        "reviews": ["name", "company", "review", "stars", "photo"],
        "articles": ["title", "url", "photo"],
        "cases": ["name", "about", "tags", "image"]
    }
    
    if field not in valid_fields.get(entity_type, []):
        await message.answer(f"❌ Неверное поле. Доступные поля: {', '.join(valid_fields[entity_type])}")
        return
    
    await state.update_data(field=field)
    
    if entity_type == "vacancies":
        await state.set_state(UpdateVacancyForm.value)
    elif entity_type == "reviews":
        await state.set_state(UpdateReviewForm.value)
    elif entity_type == "articles":
        await state.set_state(UpdateArticleForm.value)
    elif entity_type == "cases":
        await state.set_state(UpdateCaseForm.value)
    
    await message.answer(f"Введите новое значение для поля '{field}':")


async def process_update_value(message: Message, state: FSMContext):
    """Обновление записи."""
    if not await admin_only(message):
        return
    
    data = await state.get_data()
    entity_type = data["entity_type"]
    entity_id = data["entity_id"]
    field = data["field"]
    value = message.text
    
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
        
        await message.answer(
            f"✅ Запись обновлена!\n\nID: {result['id']}\nПоле '{field}' обновлено",
            reply_markup=get_back_keyboard(entity_type)
        )
    except Exception as e:
        logger.error(f"Ошибка обновления: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=get_back_keyboard(entity_type))
    
    await state.clear()


def set_api_url(url: str):
    """Установить API URL."""
    global API_URL
    API_URL = url
