from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import get_all_categories, get_books_by_category
from keyboards import categories_keyboard, books_list_keyboard, main_menu

router = Router()


@router.message(F.text == "📚 Kategoriyalar")
async def show_categories(message: Message):
    categories = get_all_categories()
    if not categories:
        await message.answer("📭 Hozircha kategoriyalar yo'q.", reply_markup=main_menu())
        return
    await message.answer("📚 <b>Kategoriyani tanlang:</b>", parse_mode="HTML", reply_markup=categories_keyboard(categories))


@router.callback_query(F.data.startswith("cat_"))
async def show_category_books(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[1])
    books = get_books_by_category(cat_id)

    if not books:
        await callback.answer("📭 Bu kategoriyada kitoblar yo'q!", show_alert=True)
        return

    await callback.message.answer(
        f"📚 <b>{len(books)} ta kitob:</b>",
        parse_mode="HTML",
        reply_markup=books_list_keyboard(books, back_callback="back_categories")
    )
    await callback.answer()


@router.callback_query(F.data == "back_categories")
async def back_to_categories(callback: CallbackQuery):
    categories = get_all_categories()
    await callback.message.answer(
        "📚 <b>Kategoriyani tanlang:</b>",
        parse_mode="HTML",
        reply_markup=categories_keyboard(categories)
    )
    await callback.answer()
