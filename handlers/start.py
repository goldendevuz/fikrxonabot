from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import register_user
from keyboards import main_menu, admin_menu
from config import ADMIN_IDS

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    register_user(user.id, user.username or "", user.full_name or "")

    is_admin = user.id in ADMIN_IDS
    kb = admin_menu() if is_admin else main_menu()

    await message.answer(
        f"📚 <b>Fikrxona kutubxonasiga xush kelibsiz!</b>\n\n"
        f"Salom, <b>{user.first_name}</b>! 👋\n\n"
        f"Bu botda siz:\n"
        f"🔍 Kitob qidirishingiz\n"
        f"📥 PDF yuklab olishingiz\n"
        f"📚 Kategoriyalar bo'yicha ko'rishingiz\n"
        f"⭐ Top kitoblarni ko'rishingiz mumkin!\n\n"
        f"Pastdagi tugmalardan foydalaning 👇",
        parse_mode="HTML",
        reply_markup=kb
    )


@router.message(F.text == "ℹ️ Yordam")
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "🔍 <b>Kitob qidirish</b> — kitob nomi yoki muallif bo'yicha qidiring\n"
        "📚 <b>Kategoriyalar</b> — janr bo'yicha kitoblarni ko'ring\n"
        "⭐ <b>Top kitoblar</b> — eng ko'p yuklab olingan kitoblar\n"
        "🎯 <b>Tavsiya</b> — siz uchun kitob tavsiya qilinadi\n"
        "📥 <b>Yuklab olganlarim</b> — yuklab olish tarixingiz\n\n"
        "❓ Savol yoki takliflar uchun: @Fikrxonamiz",
        parse_mode="HTML"
    )


@router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id in ADMIN_IDS
    kb = admin_menu() if is_admin else main_menu()
    await message.answer("🏠 Asosiy menyu", reply_markup=kb)
