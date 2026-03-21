"""Экспорт статей в MD формат."""
import os
import httpx
from pathlib import Path
from aiogram.types import FSInputFile, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import get_back_keyboard
from utils.logger import get_logger

logger = get_logger()

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Директория для временных MD файлов
MD_TEMP_DIR = Path("uploads/md_temp")
MD_TEMP_DIR.mkdir(parents=True, exist_ok=True)


class ExportMDForm(StatesGroup):
    """States for MD export."""
    waiting_for_id = State()


async def handle_export_md_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик экспорта статьи в MD."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    await state.set_state(ExportMDForm.waiting_for_id)
    await callback.message.edit_text(
        "📥 <b>Экспорт статьи в MD</b>\n\n"
        "Введите ID статьи для экспорта:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard("articles")
    )
    await callback.answer()


async def process_export_md_id(message: Message, state: FSMContext):
    """Обработка ID для экспорта."""
    if not await admin_only(message):
        return
    
    try:
        article_id = int(message.text)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return
    
    try:
        # Получаем статью
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/articles/{article_id}",
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            article = response.json()
        
        # Создаем MD файл
        md_content = f"# {article['title']}\n\n"
        md_content += f"**URL:** {article['url']}\n\n"
        if article.get('photo'):
            md_content += f"**Фото:** {article['photo']}\n\n"
        md_content += "---\n\n"
        md_content += article['content']
        
        # Генерируем имя файла
        import re
        safe_title = re.sub(r'[^a-zA-Z0-9а-яА-Я\s-]', '', article['title'])
        safe_title = re.sub(r'\s+', '_', safe_title.strip())[:50]
        filename = f"{safe_title}_{article_id}.md"
        filepath = MD_TEMP_DIR / filename
        
        # Сохраняем файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"📄 MD файл создан: {filepath}")
        
        # Отправляем файл
        document = FSInputFile(filepath, filename=filename)
        await message.answer_document(
            document=document,
            caption=f"📄 <b>Статья #{article_id}</b>\n\n"
                    f"📝 {article['title']}\n"
                    f"📊 {len(article['content'])} символов",
            parse_mode="HTML",
            reply_markup=get_back_keyboard("articles")
        )
        
        # Удаляем временный файл
        filepath.unlink()
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer(
                f"❌ Статья с ID {article_id} не найдена",
                reply_markup=get_back_keyboard("articles")
            )
        else:
            await message.answer(
                f"❌ Ошибка сервера (код {e.response.status_code})",
                reply_markup=get_back_keyboard("articles")
            )
    except Exception as e:
        logger.error(f"Ошибка экспорта MD: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при экспорте",
            reply_markup=get_back_keyboard("articles")
        )
    
    await state.clear()


def set_api_url(url: str):
    """Установить API URL."""
    global API_URL
    API_URL = url
