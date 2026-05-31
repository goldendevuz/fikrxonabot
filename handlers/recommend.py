import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_all_categories, get_books_by_category, get_top_books, get_user_downloads
from keyboards import categories_keyboard, books_list_keyboard, main_menu

router = Router()


class RecommendState(StatesGroup):
    choosing_category = State()


@router.message(F.text == "🎯 Tavsiya")
async def recommend_start(message: Message, state: FSMContext):
    categories = get_all_categories()
    if not categories:
        await message.answer("😔 Hozircha kitoblar yo'q.", reply_markup=main_menu())
        return
    await state.set_state(RecommendState.choosing_category)
    await message.answer(
        "🎯 <b>Tavsiya uchun kategoriyani tanlang:</b>",
        parse_mode="HTML",
        reply_markup=categories_keyboard(categories)
    )


@router.callback_query(RecommendState.choosing_category, F.data.startswith("cat_"))
async def recommend_by_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    cat_id = int(callback.data.split("_")[1])
    books = get_books_by_category(cat_id)

    if not books:
        await callback.answer("😔 Bu kategoriyada kitoblar yo'q!", show_alert=True)
        return

    recommended = random.sample(list(books), min(3, len(books)))
    await callback.message.answer(
        "🎯 <b>Siz uchun tavsiya:</b>",
        parse_mode="HTML",
        reply_markup=books_list_keyboard(recommended, back_callback="back_main")
    )
    await callback.answer()


@router.message(F.text == "⭐ Top kitoblar")
async def show_top_books(message: Message):
    books = get_top_books(limit=10)
    if not books:
        await message.answer("😔 Hozircha kitoblar yo'q.", reply_markup=main_menu())
        return
    await message.answer(
        "⭐ <b>Eng mashhur kitoblar:</b>",
        parse_mode="HTML",
        reply_markup=books_list_keyboard(books, back_callback="back_main")
    )


@router.message(F.text == "📥 Yuklab olganlarim")
async def show_my_downloads(message: Message):
    books = get_user_downloads(message.from_user.id)
    if not books:
        await message.answer("📭 Siz hali hech qanday kitob yuklab olmadingiz.", reply_markup=main_menu())
        return
    await message.answer(
        "📥 <b>Yuklab olgan kitoblaringiz:</b>",
        parse_mode="HTML",
        reply_markup=books_list_keyboard(books, back_callback="back_main")
    )
