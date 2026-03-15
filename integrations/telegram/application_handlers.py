"""Обработчики для работы с заявками."""
import os
import httpx
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import get_back_keyboard
from utils.logger import get_logger

logger = get_logger()

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# FSM States
class ApplicationStatusForm(StatesGroup):
    application_id = State()
    status = State()


# Просмотр всех заявок
async def handle_applications_list_callback(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/v1/applications", headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            applications = response.json()
        
        if not applications:
            await callback.message.edit_text(
                "📭 Нет заявок",
                reply_markup=get_back_keyboard("main")
            )
            await callback.answer()
            return
        
        # Группируем по статусу
        new_apps = [app for app in applications if app['status'] == 'new']
        read_apps = [app for app in applications if app['status'] == 'read']
        processed_apps = [app for app in applications if app['status'] == 'processed']
        
        text = f"📋 <b>Заявки ({len(applications)} шт.)</b>\n\n"
        
        if new_apps:
            text += f"🆕 <b>Новые ({len(new_apps)}):</b>\n"
            for app in new_apps[:5]:
                text += f"  • ID {app['id']}: {app['name']} ({app['email']})\n"
            if len(new_apps) > 5:
                text += f"  ... и еще {len(new_apps) - 5}\n"
            text += "\n"
        
        if read_apps:
            text += f"👁️ <b>Прочитанные ({len(read_apps)}):</b>\n"
            for app in read_apps[:3]:
                text += f"  • ID {app['id']}: {app['name']}\n"
            if len(read_apps) > 3:
                text += f"  ... и еще {len(read_apps) - 3}\n"
            text += "\n"
        
        if processed_apps:
            text += f"✅ <b>Обработанные ({len(processed_apps)}):</b>\n"
            for app in processed_apps[:3]:
                text += f"  • ID {app['id']}: {app['name']}\n"
            if len(processed_apps) > 3:
                text += f"  ... и еще {len(processed_apps) - 3}\n"
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard("main"))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await callback.message.edit_text("❌ Раздел не найден", reply_markup=get_back_keyboard("main"))
        elif e.response.status_code == 400:
            await callback.message.edit_text("❌ Некорректный запрос", reply_markup=get_back_keyboard("main"))
        else:
            await callback.message.edit_text(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("main"))
    except httpx.TimeoutException:
        await callback.message.edit_text("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("main"))
    except Exception as e:
        logger.error(f"Ошибка получения заявок: {e}")
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("main"))
    await callback.answer()


# Просмотр новых заявок
async def handle_applications_new_callback(callback: CallbackQuery):
    if not await admin_only(callback):
        await callback.answer()
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/applications",
                params={"status": "new"},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            applications = response.json()
        
        if not applications:
            await callback.message.edit_text(
                "📭 Нет новых заявок",
                reply_markup=get_back_keyboard("main")
            )
            await callback.answer()
            return
        
        text = f"🆕 <b>Новые заявки ({len(applications)} шт.)</b>\n\n"
        for app in applications:
            text += f"<b>ID {app['id']}</b>\n"
            text += f"👤 {app['name']}\n"
            text += f"📧 {app['email']}\n"
            if app.get('phone'):
                text += f"📱 {app['phone']}\n"
            text += f"💬 {app['message'][:100]}{'...' if len(app['message']) > 100 else ''}\n"
            text += f"📅 {app['created_at'][:10]}\n\n"
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard("main"))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await callback.message.edit_text("❌ Раздел не найден", reply_markup=get_back_keyboard("main"))
        elif e.response.status_code == 400:
            await callback.message.edit_text("❌ Некорректный запрос", reply_markup=get_back_keyboard("main"))
        else:
            await callback.message.edit_text(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("main"))
    except httpx.TimeoutException:
        await callback.message.edit_text("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("main"))
    except Exception as e:
        logger.error(f"Ошибка получения новых заявок: {e}")
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("main"))
    await callback.answer()


# Изменение статуса заявки
async def handle_application_status_callback(callback: CallbackQuery, state: FSMContext):
    if not await admin_only(callback):
        await callback.answer()
        return
    
    await state.set_state(ApplicationStatusForm.application_id)
    await callback.message.edit_text(
        "🔄 <b>Изменение статуса заявки</b>\n\nВведите ID заявки:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard("main")
    )
    await callback.answer()


async def process_application_id(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    
    try:
        app_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    await state.update_data(application_id=app_id)
    await state.set_state(ApplicationStatusForm.status)
    await message.answer(
        "Выберите новый статус:\n\n"
        "1 - new (новая)\n"
        "2 - read (прочитана)\n"
        "3 - processed (обработана)\n\n"
        "Введите номер:"
    )


async def process_application_status(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    
    status_map = {"1": "new", "2": "read", "3": "processed"}
    status = status_map.get(message.text)
    
    if not status:
        await message.answer("❌ Неверный номер. Введите 1, 2 или 3:")
        return
    
    data = await state.get_data()
    app_id = data["application_id"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{API_URL}/api/v1/applications/{app_id}/status",
                params={"status": status},
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        status_emoji = {"new": "🆕", "read": "👁️", "processed": "✅"}
        await message.answer(
            f"{status_emoji[status]} Статус заявки ID {app_id} изменен на '{status}'\n\n"
            f"👤 {result['name']}\n"
            f"📧 {result['email']}",
            reply_markup=get_back_keyboard("main")
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(f"❌ Заявка с ID {app_id} не найдена", reply_markup=get_back_keyboard("main"))
        elif e.response.status_code == 400:
            await message.answer("❌ Некорректный запрос", reply_markup=get_back_keyboard("main"))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("main"))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("main"))
    except Exception as e:
        logger.error(f"Ошибка изменения статуса: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("main"))
    
    await state.clear()


def set_api_url(url: str):
    global API_URL
    API_URL = url
