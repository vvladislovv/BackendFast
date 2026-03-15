"""Обработчики действий с записями (get, delete, rating, hide, mark_fresh)."""
import httpx
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import get_back_keyboard
from utils.logger import get_logger

logger = get_logger()

API_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# FSM States
class GetByIdForm(StatesGroup):
    entity_id = State()


class UpdateRatingForm(StatesGroup):
    entity_id = State()
    rating_value = State()


class HideForm(StatesGroup):
    entity_id = State()


class DeleteForm(StatesGroup):
    entity_id = State()


class MarkFreshForm(StatesGroup):
    case_id = State()


# Поиск по ID
async def handle_get_callback(callback: CallbackQuery, state: FSMContext):
    entity_type = callback.data.replace("_get", "")
    await state.update_data(entity_type=entity_type, action="get")
    await state.set_state(GetByIdForm.entity_id)
    await callback.message.edit_text(
        f"🔍 <b>Поиск по ID</b>\n\nВведите ID записи:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(entity_type)
    )
    await callback.answer()


async def process_get_by_id(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        entity_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    data = await state.get_data()
    entity_type = data["entity_type"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/v1/{entity_type}/{entity_id}", headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            item = response.json()
        
        if entity_type == "vacancies":
            text = (f"💼 <b>{item['title']}</b>\n\nID: {item['id']}\nURL: {item['url']}\n"
                   f"Тип: {item['employment_type']}\nРейтинг: {item['rating']}\n"
                   f"Скрыта: {'Да' if item['is_hidden'] else 'Нет'}")
            if item.get('description'):
                text += f"\n\nОписание: {item['description']}"
        elif entity_type == "reviews":
            text = (f"⭐ <b>{item['name']}</b>\n\nID: {item['id']}\nКомпания: {item['company']}\n"
                   f"Звезды: {'⭐' * item['stars']}\nРейтинг: {item['rating']}\n"
                   f"Скрыт: {'Да' if item['is_hidden'] else 'Нет'}\n\nОтзыв: {item['review']}")
        elif entity_type == "articles":
            text = (f"📰 <b>{item['title']}</b>\n\nID: {item['id']}\nURL: {item['url']}\n"
                   f"Рейтинг: {item['rating']}\nСкрыта: {'Да' if item['is_hidden'] else 'Нет'}")
        elif entity_type == "cases":
            text = (f"💡 <b>{item['name']}</b>\n\nID: {item['id']}\nРейтинг: {item['rating']}\n"
                   f"Свежий: {'Да' if item.get('is_fresh') else 'Нет'}\n"
                   f"Скрыт: {'Да' if item['is_hidden'] else 'Нет'}\n"
                   f"Теги: {', '.join(item['tags'])}\n\nОписание: {item['about']}")
        
        await message.answer(text, parse_mode="HTML", reply_markup=get_back_keyboard(entity_type))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await message.answer(f"❌ Некорректный ID {entity_id}", reply_markup=get_back_keyboard(entity_type))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка получения записи: {e}")
        await message.answer(f"❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    await state.clear()


# Изменение рейтинга
async def handle_rating_callback(callback: CallbackQuery, state: FSMContext):
    entity_type = callback.data.replace("_rating", "")
    await state.update_data(entity_type=entity_type)
    await state.set_state(UpdateRatingForm.entity_id)
    await callback.message.edit_text(
        f"⭐ <b>Изменение рейтинга</b>\n\nВведите ID записи:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(entity_type)
    )
    await callback.answer()


async def process_rating_id(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        entity_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    await state.update_data(entity_id=entity_id)
    await state.set_state(UpdateRatingForm.rating_value)
    await message.answer("Введите новое значение рейтинга (число >= 0):")


async def process_rating_value(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        rating = int(message.text)
        if rating < 0:
            await message.answer("❌ Рейтинг должен быть >= 0. Попробуйте снова:")
            return
    except ValueError:
        await message.answer("❌ Введите число >= 0:")
        return
    
    data = await state.get_data()
    entity_type = data["entity_type"]
    entity_id = data["entity_id"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}/rating",
                params={"rating": rating},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        await message.answer(
            f"✅ Рейтинг обновлен!\n\nID: {result['id']}\nНовый рейтинг: {result['rating']}",
            reply_markup=get_back_keyboard(entity_type)
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await message.answer(f"❌ Некорректное значение рейтинга", reply_markup=get_back_keyboard(entity_type))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка обновления рейтинга: {e}")
        await message.answer(f"❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    await state.clear()


# Скрытие/показ
async def handle_hide_callback(callback: CallbackQuery, state: FSMContext):
    entity_type = callback.data.replace("_hide", "")
    await state.update_data(entity_type=entity_type)
    await state.set_state(HideForm.entity_id)
    await callback.message.edit_text(
        f"👁️ <b>Скрыть/Показать запись</b>\n\nВведите ID записи:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(entity_type)
    )
    await callback.answer()


async def process_hide_toggle(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        entity_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    data = await state.get_data()
    entity_type = data["entity_type"]
    
    try:
        # Сначала получаем текущее состояние записи
        async with httpx.AsyncClient() as client:
            get_response = await client.get(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}",
                headers=HEADERS,
                timeout=10.0
            )
            get_response.raise_for_status()
            current_item = get_response.json()
            
            # Переключаем состояние
            new_hidden_state = not current_item.get('is_hidden', False)
            
            # Отправляем запрос на изменение
            response = await client.patch(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}/hide",
                json={"is_hidden": new_hidden_state},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        status = "скрыта" if result['is_hidden'] else "показана"
        await message.answer(f"✅ Запись {status}!\n\nID: {result['id']}", reply_markup=get_back_keyboard(entity_type))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
        elif e.response.status_code == 400:
            await message.answer(f"❌ Некорректный запрос. Проверьте ID {entity_id}", reply_markup=get_back_keyboard(entity_type))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard(entity_type))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка переключения видимости: {e}")
        await message.answer(f"❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard(entity_type))
    await state.clear()


# Удаление
async def handle_delete_callback(callback: CallbackQuery, state: FSMContext):
    entity_type = callback.data.replace("_delete", "")
    await state.update_data(entity_type=entity_type)
    await state.set_state(DeleteForm.entity_id)
    await callback.message.edit_text(
        f"🗑️ <b>Удаление записи</b>\n\nВведите ID записи для удаления:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(entity_type)
    )
    await callback.answer()


async def process_delete_id(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        entity_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    data = await state.get_data()
    entity_type = data["entity_type"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_URL}/api/v1/{entity_type}/{entity_id}", headers=HEADERS, timeout=10.0)
            response.raise_for_status()
        await message.answer(f"✅ Запись удалена!\n\nID: {entity_id}", reply_markup=get_back_keyboard(entity_type))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Запись с ID {entity_id} не найдена", reply_markup=get_back_keyboard(entity_type))
        else:
            await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=get_back_keyboard(entity_type))
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=get_back_keyboard(entity_type))
    await state.clear()


# Пометка кейса свежим
async def handle_mark_fresh_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MarkFreshForm.case_id)
    await callback.message.edit_text(
        f"🌟 <b>Пометить кейс свежим</b>\n\nВведите ID кейса:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard("cases")
    )
    await callback.answer()


async def process_mark_fresh(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        case_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    try:
        # Сначала получаем текущее состояние кейса
        async with httpx.AsyncClient() as client:
            get_response = await client.get(
                f"{API_URL}/api/v1/cases/{case_id}",
                headers=HEADERS,
                timeout=10.0
            )
            get_response.raise_for_status()
            current_case = get_response.json()
            
            # Переключаем состояние is_fresh
            new_fresh_state = not current_case.get('is_fresh', False)
            
            # Отправляем запрос на изменение
            response = await client.patch(
                f"{API_URL}/api/v1/cases/{case_id}/fresh",
                json={"is_fresh": new_fresh_state},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        status = "свежим" if result['is_fresh'] else "обычным"
        await message.answer(
            f"✅ Кейс помечен {status}!\n\nID: {result['id']}\nНазвание: {result['name']}",
            reply_markup=get_back_keyboard("cases")
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Кейс с ID {case_id} не найден", reply_markup=get_back_keyboard("cases"))
        elif e.response.status_code == 400:
            await message.answer(f"❌ Некорректный ID {case_id}", reply_markup=get_back_keyboard("cases"))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("cases"))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("cases"))
    except Exception as e:
        logger.error(f"Ошибка пометки кейса: {e}")
        await message.answer(f"❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("cases"))
    await state.clear()


def set_api_url(url: str):
    global API_URL
    API_URL = url


async def handle_quick_visibility_toggle(callback: CallbackQuery):
    """Быстрое переключение видимости элемента."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    # Формат: hide_reviews_1 или show_reviews_1
    parts = callback.data.split("_")
    action = parts[0]  # hide или show
    entity_type = parts[1]  # reviews, vacancies, etc.
    entity_id = int(parts[2])
    
    # Определяем новое значение is_hidden
    new_hidden_value = (action == "hide")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_URL}/api/v1/{entity_type}/{entity_id}",
                json={"is_hidden": new_hidden_value},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        status_text = "скрыт" if new_hidden_value else "показан"
        await callback.message.edit_text(
            f"✅ Элемент ID {entity_id} теперь {status_text}!",
            reply_markup=get_back_keyboard(entity_type)
        )
        
        logger.info(f"Изменена видимость {entity_type}/{entity_id}: is_hidden={new_hidden_value}")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при изменении видимости: {e.response.status_code}")
        if e.response.status_code == 404:
            await callback.message.edit_text(
                f"❌ Запись с ID {entity_id} не найдена",
                reply_markup=get_back_keyboard(entity_type)
            )
        elif e.response.status_code == 400:
            await callback.message.edit_text(
                "❌ Некорректные данные",
                reply_markup=get_back_keyboard(entity_type)
            )
        else:
            await callback.message.edit_text(
                f"❌ Ошибка сервера (код {e.response.status_code})",
                reply_markup=get_back_keyboard(entity_type)
            )
    except Exception as e:
        logger.error(f"Ошибка изменения видимости: {e}", exc_info=True)
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте позже",
            reply_markup=get_back_keyboard(entity_type)
        )
    
    await callback.answer()
