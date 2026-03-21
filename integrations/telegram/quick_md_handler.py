"""Quick MD file upload handler for articles."""
import os
import httpx
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import get_back_keyboard
from utils.logger import get_logger

logger = get_logger()

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


class QuickArticleForm(StatesGroup):
    """States for quick article creation from MD."""
    waiting_for_details = State()
    waiting_for_file = State()  # New state for waiting MD file after button click


async def handle_md_file(message: Message, state: FSMContext):
    """Automatic article creation from MD file."""
    if not await admin_only(message):
        return
    
    # Check if this is an MD file
    if not message.document or not message.document.file_name or not message.document.file_name.endswith('.md'):
        # If we're waiting for file, show error
        current_state = await state.get_state()
        if current_state == QuickArticleForm.waiting_for_file:
            await message.answer("❌ Пожалуйста, отправьте файл с расширением .md")
        return
    
    try:
        # Download file
        file = await message.bot.get_file(message.document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        
        # Read content
        content = file_content.read().decode('utf-8')
        
        logger.info(f"MD file received: {message.document.file_name}, size: {len(content)} chars")
        
        # Extract title from first MD line (if has #)
        lines = content.split('\n')
        suggested_title = ""
        for line in lines:
            if line.strip().startswith('#'):
                suggested_title = line.strip().lstrip('#').strip()
                break
        
        # Send message with preview
        preview = content[:200] + "..." if len(content) > 200 else content
        
        response_text = f"📄 <b>MD файл получен!</b>\n\n"
        response_text += f"📁 Файл: {message.document.file_name}\n"
        response_text += f"📊 Размер: {len(content)} символов\n"
        if suggested_title:
            response_text += f"💡 Найден заголовок: <b>{suggested_title}</b>\n"
        response_text += f"\n<b>Предпросмотр:</b>\n<code>{preview}</code>\n\n"
        response_text += "📝 Выберите действие:\n\n"
        response_text += "1️⃣ Отправьте данные в формате:\n"
        response_text += "<code>Название статьи\n"
        response_text += "https://url-статьи.ru\n"
        response_text += "https://url-фото.jpg</code>\n\n"
        response_text += "2️⃣ Или отправьте <code>/auto</code> для автоматического создания"
        if suggested_title:
            response_text += f" с заголовком:\n<b>{suggested_title}</b>"
        
        await message.answer(response_text, parse_mode="HTML")
        
        # Save content to state
        await state.set_state(QuickArticleForm.waiting_for_details)
        await state.update_data(
            md_content=content, 
            filename=message.document.file_name,
            suggested_title=suggested_title
        )
        
    except Exception as e:
        logger.error(f"Error processing MD file: {e}", exc_info=True)
        await message.answer("❌ Ошибка обработки файла. Попробуйте снова")


async def process_article_details(message: Message, state: FSMContext):
    """Process article details after MD upload."""
    if not await admin_only(message):
        return
    
    data = await state.get_data()
    md_content = data.get('md_content')
    suggested_title = data.get('suggested_title', '')
    filename = data.get('filename', '')
    
    if not md_content:
        await message.answer("❌ MD контент не найден. Отправьте файл заново")
        await state.clear()
        return
    
    # Check for auto command
    if message.text.strip().lower() == '/auto':
        if not suggested_title:
            await message.answer("❌ Не удалось найти заголовок в MD файле. Отправьте данные вручную:\n<code>Название\nURL</code>", parse_mode="HTML")
            return
        
        # Auto-generate URL from title
        import re
        url_slug = re.sub(r'[^a-zA-Z0-9а-яА-Я\s-]', '', suggested_title)
        url_slug = re.sub(r'\s+', '-', url_slug.strip()).lower()
        url = f"https://hacktaika.ru/articles/{url_slug}"
        
        # Create article automatically
        payload = {
            "title": suggested_title,
            "url": url,
            "content": md_content,
            "photo": None
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/api/v1/articles",
                    json=payload,
                    headers=HEADERS,
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
            
            logger.info(f"Article auto-created from MD file! ID: {result['id']}")
            
            await message.answer(
                f"✅ <b>Статья создана автоматически!</b>\n\n"
                f"📄 ID: {result['id']}\n"
                f"📝 Название: {result['title']}\n"
                f"🔗 URL: {result['url']}\n"
                f"📊 Контент: {len(result['content'])} символов\n"
                f"🖼 Фото: ❌ Нет\n\n"
                f"Статья успешно добавлена!",
                parse_mode="HTML",
                reply_markup=get_back_keyboard("articles")
            )
            await state.clear()
            return
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Error creating article: {e.response.status_code}, {e.response.text}")
            await message.answer(
                f"❌ Ошибка создания статьи (код {e.response.status_code})",
                reply_markup=get_back_keyboard("articles")
            )
            await state.clear()
            return
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("articles"))
            await state.clear()
            return
    
    # Parse input data
    lines = message.text.strip().split('\n')
    
    if len(lines) < 2:
        await message.answer("❌ Неверный формат. Отправьте:\n<code>Название\nURL\nФото (опционально)</code>\n\nИли <code>/auto</code> для автоматического создания", parse_mode="HTML")
        return
    
    title = lines[0].strip()
    url = lines[1].strip()
    photo = lines[2].strip() if len(lines) > 2 else None
    
    # Create article
    payload = {
        "title": title,
        "url": url,
        "content": md_content,
        "photo": photo
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/v1/articles",
                json=payload,
                headers=HEADERS,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        logger.info(f"Article created from MD file! ID: {result['id']}")
        
        await message.answer(
            f"✅ <b>Статья создана из MD файла!</b>\n\n"
            f"📄 ID: {result['id']}\n"
            f"📝 Название: {result['title']}\n"
            f"🔗 URL: {result['url']}\n"
            f"📊 Контент: {len(result['content'])} символов\n"
            f"🖼 Фото: {'✅ Есть' if result.get('photo') else '❌ Нет'}\n\n"
            f"Статья успешно добавлена!",
            parse_mode="HTML",
            reply_markup=get_back_keyboard("articles")
        )
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Error creating article: {e.response.status_code}, {e.response.text}")
        await message.answer(
            f"❌ Ошибка создания статьи (код {e.response.status_code})",
            reply_markup=get_back_keyboard("articles")
        )
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("articles"))
    
    await state.clear()


def set_api_url(url: str):
    global API_URL
    API_URL = url


async def handle_upload_md_button(callback_query, state: FSMContext):
    """Handle upload MD button click."""
    from integrations.telegram.admin_check import admin_only
    
    if not await admin_only(callback_query):
        await callback_query.answer()
        return
    
    await callback_query.message.edit_text(
        "📤 <b>Загрузка MD файла</b>\n\n"
        "Отправьте .md файл со статьей.\n\n"
        "Бот автоматически извлечет заголовок из первой строки (если есть #).\n\n"
        "После загрузки вы сможете:\n"
        "• Отправить <code>/auto</code> для автоматического создания\n"
        "• Или указать данные вручную в формате:\n"
        "  <code>Название\nURL\nФото (опционально)</code>",
        parse_mode="HTML"
    )
    
    await state.set_state(QuickArticleForm.waiting_for_file)
    await callback_query.answer()
