"""Обработчики создания записей."""
import httpx
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from integrations.telegram.admin_check import admin_only
from integrations.telegram.keyboards import (
    get_back_keyboard,
    get_names_keyboard,
    get_companies_keyboard,
    get_review_templates_keyboard,
    get_create_stars_keyboard,
    get_photo_skip_keyboard
)
from utils.logger import get_logger

logger = get_logger()

API_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# FSM States
class VacancyForm(StatesGroup):
    title = State()
    url = State()
    employment_type = State()
    description = State()


class ReviewForm(StatesGroup):
    name = State()
    company = State()
    review = State()
    stars = State()
    photo = State()


class ArticleForm(StatesGroup):
    title = State()
    url = State()
    photo = State()


class CaseForm(StatesGroup):
    name = State()
    about = State()
    tags = State()
    image = State()


async def handle_create_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик создания новой записи."""
    entity_type = callback.data.replace("_create", "")
    await state.update_data(entity_type=entity_type)
    
    if entity_type == "vacancies":
        await state.set_state(VacancyForm.title)
        text = "➕ <b>Создание вакансии</b>\n\nШаг 1/4: Введите название вакансии:"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard(entity_type))
    elif entity_type == "reviews":
        await state.set_state(ReviewForm.name)
        text = "➕ <b>Создание отзыва</b>\n\nШаг 1/5: Выберите имя автора отзыва:"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_names_keyboard())
    elif entity_type == "articles":
        await state.set_state(ArticleForm.title)
        text = "➕ <b>Создание статьи</b>\n\nШаг 1/3: Введите название статьи:"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard(entity_type))
    elif entity_type == "cases":
        await state.set_state(CaseForm.name)
        text = "➕ <b>Создание кейса</b>\n\nШаг 1/4: Введите название кейса:"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard(entity_type))
    
    await callback.answer()


# Вакансии
async def process_vacancy_title(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(title=message.text)
    await state.set_state(VacancyForm.url)
    await message.answer("Шаг 2/4: Введите URL вакансии:")


async def process_vacancy_url(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(url=message.text)
    await state.set_state(VacancyForm.employment_type)
    await message.answer("Шаг 3/4: Введите тип занятости (Full-time/Part-time/Remote):")


async def process_vacancy_employment(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(employment_type=message.text)
    await state.set_state(VacancyForm.description)
    await message.answer("Шаг 4/4: Введите описание (или '-' чтобы пропустить):")


async def process_vacancy_description(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    data = await state.get_data()
    payload = {
        "title": data["title"],
        "url": data["url"],
        "employment_type": data["employment_type"],
        "description": None if message.text == "-" else message.text
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/v1/vacancies", json=payload, headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            result = response.json()
        await message.answer(
            f"✅ Вакансия создана!\n\nID: {result['id']}\nНазвание: {result['title']}\nТип: {result['employment_type']}",
            reply_markup=get_back_keyboard("vacancies")
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer("❌ Некорректные данные. Проверьте введенную информацию", reply_markup=get_back_keyboard("vacancies"))
        elif e.response.status_code == 422:
            await message.answer("❌ Ошибка валидации данных", reply_markup=get_back_keyboard("vacancies"))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("vacancies"))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("vacancies"))
    except Exception as e:
        logger.error(f"Ошибка создания вакансии: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("vacancies"))
    await state.clear()


# Отзывы
async def handle_name_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора имени через кнопку."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    if callback.data == "create_name_custom":
        await callback.message.edit_text("Введите имя автора отзыва:")
        await callback.answer()
        return
    
    # Извлекаем имя из callback_data
    name = callback.data.replace("create_name_", "")
    await state.update_data(name=name)
    await state.set_state(ReviewForm.company)
    await callback.message.edit_text(
        f"✅ Имя: {name}\n\nШаг 2/5: Выберите компанию:",
        reply_markup=get_companies_keyboard()
    )
    await callback.answer()


async def handle_company_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора компании через кнопку."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    if callback.data == "create_company_custom":
        await callback.message.edit_text("Введите название компании:")
        await callback.answer()
        return
    
    # Извлекаем компанию из callback_data
    company = callback.data.replace("create_company_", "")
    await state.update_data(company=company)
    await state.set_state(ReviewForm.review)
    
    data = await state.get_data()
    await callback.message.edit_text(
        f"✅ Имя: {data['name']}\n✅ Компания: {company}\n\nШаг 3/5: Выберите шаблон отзыва или напишите свой:",
        reply_markup=get_review_templates_keyboard()
    )
    await callback.answer()


async def handle_review_template_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора шаблона отзыва."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    if callback.data == "create_review_custom":
        await callback.message.edit_text("Введите текст отзыва:")
        await callback.answer()
        return
    
    # Шаблоны отзывов
    templates = {
        "create_review_template_1": "Отличная компания с прекрасным коллективом! Работать здесь - одно удовольствие. Руководство всегда идет навстречу сотрудникам.",
        "create_review_template_2": "Профессиональная команда, интересные проекты и возможности для роста. Рекомендую эту компанию как работодателя!",
        "create_review_template_3": "Быстрый карьерный рост, современные технологии и дружелюбная атмосфера. Здесь ценят каждого сотрудника.",
        "create_review_template_4": "Отличный баланс между работой и личной жизнью. Гибкий график, удаленная работа, адекватное руководство.",
        "create_review_template_5": "Достойная зарплата, своевременные выплаты, социальный пакет. Компания заботится о своих сотрудниках."
    }
    
    review_text = templates.get(callback.data, "")
    await state.update_data(review=review_text)
    await state.set_state(ReviewForm.stars)
    
    data = await state.get_data()
    await callback.message.edit_text(
        f"✅ Имя: {data['name']}\n✅ Компания: {data['company']}\n✅ Отзыв: {review_text[:50]}...\n\nШаг 4/5: Выберите количество звезд:",
        reply_markup=get_create_stars_keyboard()
    )
    await callback.answer()


async def handle_create_stars_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора количества звезд при создании."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    stars = int(callback.data.replace("create_stars_", ""))
    await state.update_data(stars=stars)
    await state.set_state(ReviewForm.photo)
    
    data = await state.get_data()
    await callback.message.edit_text(
        f"✅ Имя: {data['name']}\n✅ Компания: {data['company']}\n✅ Отзыв: {data['review'][:50]}...\n✅ Звезды: {'⭐' * stars}\n\nШаг 5/5: Добавить фото?",
        reply_markup=get_photo_skip_keyboard()
    )
    await callback.answer()


async def handle_photo_skip(callback: CallbackQuery, state: FSMContext):
    """Обработка пропуска фото."""
    if not await admin_only(callback):
        await callback.answer()
        return
    
    if callback.data == "create_photo_skip":
        # Создаем отзыв без фото
        data = await state.get_data()
        payload = {
            "name": data["name"],
            "company": data["company"],
            "review": data["review"],
            "stars": data["stars"],
            "photo": None
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_URL}/api/v1/reviews", json=payload, headers=HEADERS, timeout=10.0)
                response.raise_for_status()
                result = response.json()
            await callback.message.edit_text(
                f"✅ Отзыв создан!\n\nID: {result['id']}\nАвтор: {result['name']}\nКомпания: {result['company']}\nЗвезды: {'⭐' * result['stars']}",
                reply_markup=get_back_keyboard("reviews")
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                await callback.message.edit_text("❌ Некорректные данные. Проверьте введенную информацию", reply_markup=get_back_keyboard("reviews"))
            elif e.response.status_code == 422:
                await callback.message.edit_text("❌ Ошибка валидации данных", reply_markup=get_back_keyboard("reviews"))
            else:
                await callback.message.edit_text(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("reviews"))
        except httpx.TimeoutException:
            await callback.message.edit_text("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("reviews"))
        except Exception as e:
            logger.error(f"Ошибка создания отзыва: {e}")
            await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("reviews"))
        await state.clear()
        await callback.answer()
    elif callback.data == "create_photo_upload":
        await callback.message.edit_text("Отправьте фото или введите URL:")
        await callback.answer()


async def process_review_name(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(name=message.text)
    await state.set_state(ReviewForm.company)
    await message.answer("Шаг 2/5: Выберите компанию:", reply_markup=get_companies_keyboard())


async def process_review_company(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(company=message.text)
    await state.set_state(ReviewForm.review)
    data = await state.get_data()
    await message.answer(
        f"✅ Имя: {data['name']}\n✅ Компания: {message.text}\n\nШаг 3/5: Выберите шаблон отзыва или напишите свой:",
        reply_markup=get_review_templates_keyboard()
    )


async def process_review_text(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(review=message.text)
    await state.set_state(ReviewForm.stars)
    data = await state.get_data()
    await message.answer(
        f"✅ Имя: {data['name']}\n✅ Компания: {data['company']}\n✅ Отзыв: {message.text[:50]}...\n\nШаг 4/5: Выберите количество звезд:",
        reply_markup=get_create_stars_keyboard()
    )


async def process_review_stars(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    try:
        stars = int(message.text)
        if stars < 1 or stars > 5:
            await message.answer("❌ Звезды должны быть от 1 до 5. Попробуйте снова:")
            return
    except ValueError:
        await message.answer("❌ Введите число от 1 до 5:")
        return
    await state.update_data(stars=stars)
    await state.set_state(ReviewForm.photo)
    data = await state.get_data()
    await message.answer(
        f"✅ Имя: {data['name']}\n✅ Компания: {data['company']}\n✅ Отзыв: {data['review'][:50]}...\n✅ Звезды: {'⭐' * stars}\n\nШаг 5/5: Добавить фото?",
        reply_markup=get_photo_skip_keyboard()
    )


async def process_review_photo(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    
    # Проверяем, отправлено ли фото
    photo_url = None
    if message.photo:
        # Берем самое большое фото
        photo = message.photo[-1]
        photo_url = f"tg://photo/{photo.file_id}"
        logger.info(f"Получено фото: {photo_url}")
    elif message.text and message.text != "-":
        photo_url = message.text
    
    data = await state.get_data()
    payload = {
        "name": data["name"],
        "company": data["company"],
        "review": data["review"],
        "stars": data["stars"],
        "photo": photo_url
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/v1/reviews", json=payload, headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            result = response.json()
        await message.answer(
            f"✅ Отзыв создан!\n\nID: {result['id']}\nАвтор: {result['name']}\nКомпания: {result['company']}\nЗвезды: {'⭐' * result['stars']}",
            reply_markup=get_back_keyboard("reviews")
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer("❌ Некорректные данные. Проверьте введенную информацию", reply_markup=get_back_keyboard("reviews"))
        elif e.response.status_code == 422:
            await message.answer("❌ Ошибка валидации данных", reply_markup=get_back_keyboard("reviews"))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("reviews"))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("reviews"))
    except Exception as e:
        logger.error(f"Ошибка создания отзыва: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("reviews"))
    await state.clear()


# Статьи
async def process_article_title(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(title=message.text)
    await state.set_state(ArticleForm.url)
    await message.answer("Шаг 2/3: Введите URL статьи:")


async def process_article_url(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(url=message.text)
    await state.set_state(ArticleForm.photo)
    await message.answer("Шаг 3/3: Отправьте фото или введите URL (или '-' чтобы пропустить):")


async def process_article_photo(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    
    # Проверяем, отправлено ли фото
    photo_url = None
    if message.photo:
        # Берем самое большое фото
        photo = message.photo[-1]
        photo_url = f"tg://photo/{photo.file_id}"
        logger.info(f"Получено фото: {photo_url}")
    elif message.text and message.text != "-":
        photo_url = message.text
    
    data = await state.get_data()
    payload = {
        "title": data["title"],
        "url": data["url"],
        "photo": photo_url
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/v1/articles", json=payload, headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            result = response.json()
        await message.answer(
            f"✅ Статья создана!\n\nID: {result['id']}\nНазвание: {result['title']}",
            reply_markup=get_back_keyboard("articles")
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer("❌ Некорректные данные. Проверьте введенную информацию", reply_markup=get_back_keyboard("articles"))
        elif e.response.status_code == 422:
            await message.answer("❌ Ошибка валидации данных", reply_markup=get_back_keyboard("articles"))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("articles"))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("articles"))
    except Exception as e:
        logger.error(f"Ошибка создания статьи: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("articles"))
    await state.clear()


# Кейсы
async def process_case_name(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(name=message.text)
    await state.set_state(CaseForm.about)
    await message.answer("Шаг 2/4: Введите описание кейса:")


async def process_case_about(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.update_data(about=message.text)
    await state.set_state(CaseForm.tags)
    await message.answer("Шаг 3/4: Введите теги через запятую (например: Web,Python,React):")


async def process_case_tags(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    tags = [tag.strip() for tag in message.text.split(",")]
    await state.update_data(tags=tags)
    await state.set_state(CaseForm.image)
    await message.answer("Шаг 4/4: Отправьте фото или введите URL изображения:")


async def process_case_image(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    
    # Проверяем, отправлено ли фото
    image_url = None
    if message.photo:
        # Берем самое большое фото
        photo = message.photo[-1]
        image_url = f"tg://photo/{photo.file_id}"
        logger.info(f"Получено фото: {image_url}")
    elif message.text:
        image_url = message.text
    else:
        await message.answer("❌ Отправьте фото или URL изображения:")
        return
    
    data = await state.get_data()
    payload = {
        "name": data["name"],
        "about": data["about"],
        "tags": data["tags"],
        "image": image_url
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/v1/cases", json=payload, headers=HEADERS, timeout=10.0)
            response.raise_for_status()
            result = response.json()
        await message.answer(
            f"✅ Кейс создан!\n\nID: {result['id']}\nНазвание: {result['name']}\nТеги: {', '.join(result['tags'])}",
            reply_markup=get_back_keyboard("cases")
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer("❌ Некорректные данные. Проверьте введенную информацию", reply_markup=get_back_keyboard("cases"))
        elif e.response.status_code == 422:
            await message.answer("❌ Ошибка валидации данных", reply_markup=get_back_keyboard("cases"))
        else:
            await message.answer(f"❌ Ошибка сервера (код {e.response.status_code})", reply_markup=get_back_keyboard("cases"))
    except httpx.TimeoutException:
        await message.answer("❌ Превышено время ожидания. Попробуйте позже", reply_markup=get_back_keyboard("cases"))
    except Exception as e:
        logger.error(f"Ошибка создания кейса: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже", reply_markup=get_back_keyboard("cases"))
    await state.clear()


def set_api_url(url: str):
    global API_URL
    API_URL = url
