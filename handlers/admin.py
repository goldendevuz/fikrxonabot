from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    add_book, add_category, get_all_categories, get_all_books,
    delete_book, delete_category, get_stats
)
from keyboards import (
    admin_menu, main_menu, cancel_keyboard,
    admin_delete_keyboard, confirm_delete_keyboard, categories_keyboard
)
from config import ADMIN_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AddBookState(StatesGroup):
    title = State()
    author = State()
    category = State()
    description = State()
    cover = State()
    file = State()


class AddCategoryState(StatesGroup):
    name = State()


# ─── Admin panel ───────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("🔧 <b>Admin panel</b>", parse_mode="HTML", reply_markup=admin_menu())


@router.callback_query(F.data == "back_admin")
async def back_to_admin(callback: CallbackQuery):
    await callback.message.answer("🔧 Admin panel", reply_markup=admin_menu())
    await callback.answer()


# ─── Kategoriya qo'shish ───────────────────────────────────────────────────

@router.message(F.text == "🗂 Kategoriya qo'shish")
async def add_category_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddCategoryState.name)
    await message.answer("🗂 Yangi kategoriya nomini kiriting:", reply_markup=cancel_keyboard())


@router.message(AddCategoryState.name)
async def add_category_process(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi", reply_markup=admin_menu())
        return
    result = add_category(message.text.strip())
    await state.clear()
    if result:
        await message.answer(f"✅ <b>{message.text}</b> kategoriyasi qo'shildi!", parse_mode="HTML", reply_markup=admin_menu())
    else:
        await message.answer("⚠️ Bu kategoriya allaqachon mavjud!", reply_markup=admin_menu())


# ─── Kitob qo'shish ────────────────────────────────────────────────────────

@router.message(F.text == "➕ Kitob qo'shish")
async def add_book_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddBookState.title)
    await message.answer("📖 Kitob nomini kiriting:", reply_markup=cancel_keyboard())


@router.message(AddBookState.title)
async def add_book_title(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi", reply_markup=admin_menu())
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddBookState.author)
    await message.answer("👤 Muallif ismini kiriting:")


@router.message(AddBookState.author)
async def add_book_author(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi", reply_markup=admin_menu())
        return
    await state.update_data(author=message.text.strip())
    categories = get_all_categories()
    if not categories:
        await message.answer("⚠️ Avval kategoriya qo'shing!")
        await state.clear()
        return
    await state.set_state(AddBookState.category)
    await message.answer("🗂 Kategoriyani tanlang:", reply_markup=categories_keyboard(categories))


@router.callback_query(AddBookState.category, F.data.startswith("cat_"))
async def add_book_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=cat_id)
    await state.set_state(AddBookState.description)
    await callback.message.answer("📝 Kitob tavsifini kiriting (yoki '-' yozing):")
    await callback.answer()


@router.message(AddBookState.description)
async def add_book_description(message: Message, state: FSMContext):
    desc = "" if message.text.strip() in ["-", "skip"] else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(AddBookState.cover)
    await message.answer("🖼 Kitob muqovasini (rasm) yuboring yoki '-' yozing:")


@router.message(AddBookState.cover)
async def add_book_cover(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(cover_id=message.photo[-1].file_id)
    else:
        await state.update_data(cover_id=None)
    await state.set_state(AddBookState.file)
    await message.answer("📄 Kitob PDF faylini yuboring:")


@router.message(AddBookState.file)
async def add_book_file(message: Message, state: FSMContext):
    data = await state.get_data()
    add_book(
        title=data["title"],
        author=data["author"],
        category_id=data["category_id"],
        description=data.get("description", ""),
        file_id=message.document.file_id,
        cover_id=data.get("cover_id")
    )
    await state.clear()
    await message.answer(
        f"✅ <b>{data['title']}</b> muvaffaqiyatli qo'shildi!",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


# ─── Kitob o'chirish ───────────────────────────────────────────────────────

@router.message(F.text == "🗑 Kitob o'chirish")
async def delete_book_start(message: Message):
    if not is_admin(message.from_user.id):
        return
    books = get_all_books()
    if not books:
        await message.answer("📭 Kitoblar yo'q.", reply_markup=admin_menu())
        return
    await message.answer("🗑 Qaysi kitobni o'chirmoqchisiz?", reply_markup=admin_delete_keyboard(books))


@router.callback_query(F.data.startswith("del_book_"))
async def confirm_delete_book(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[2])
    await callback.message.answer(
        "⚠️ Haqiqatan ham o'chirishni xohlaysizmi?",
        reply_markup=confirm_delete_keyboard(book_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_del_"))
async def execute_delete_book(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[2])
    delete_book(book_id)
    await callback.message.answer("✅ Kitob o'chirildi!", reply_markup=admin_menu())
    await callback.answer()


# ─── Statistika ────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    books, users, downloads = get_stats()
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"📚 Kitoblar: <b>{books}</b>\n"
        f"👤 Foydalanuvchilar: <b>{users}</b>\n"
        f"📥 Yuklab olishlar: <b>{downloads}</b>",
        parse_mode="HTML"
    )
