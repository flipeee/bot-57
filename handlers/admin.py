from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from keyboards import confirm_admin_keyboard, banned_keyboard
from config import PASSWORD_LIMITED, PASSWORD_FULL, FULL_ADMIN_ID, ADMIN_USERNAME

router = Router()

class AdminForm(StatesGroup):
    waiting_password = State()
    waiting_block = State()

@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if message.chat.type != "private":
        await message.answer("Введите /admin в личке с ботом.")
        return
    await state.set_state(AdminForm.waiting_password)
    await message.answer("Введите пароль:")

@router.message(AdminForm.waiting_password)
async def check_password(message: Message, state: FSMContext):
    await state.clear()
    pwd = message.text
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    if pwd == PASSWORD_FULL:
        await db.set_role(user_id, "admin_full")
        await message.answer("✅ Полный доступ предоставлен. Доступны скрытые команды /admins и /block.")
        return
    
    if pwd == PASSWORD_LIMITED:
        await db.add_pending(user_id, username)
        await message.bot.send_message(
            FULL_ADMIN_ID,
            f"🔔 Пользователь @{username} ввёл пароль ограниченного доступа.\nПодтвердить?",
            reply_markup=confirm_admin_keyboard(user_id)
        )
        await message.answer("⏳ Заявка отправлена на рассмотрение.")
        return
    
    await message.bot.send_message(
        FULL_ADMIN_ID,
        f"⚠️ Пользователь @{username} ввёл НЕВЕРНЫЙ пароль."
    )
    await message.answer("❌ Неверный пароль.")

@router.callback_query(F.data.startswith("approve:") | F.data.startswith("reject:"))
async def handle_approval(call: CallbackQuery):
    if call.from_user.id != FULL_ADMIN_ID:
        await call.answer("Нет прав.")
        return
    
    action, user_id = call.data.split(":")
    user_id = int(user_id)
    
    if action == "approve":
        await db.set_role(user_id, "admin_limited")
        await db.remove_pending(user_id)
        await call.bot.send_message(user_id, "✅ Доступ предоставлен.")
        await call.message.edit_text(f"Пользователь стал ограниченным админом.")
    else:
        await db.remove_pending(user_id)
        await call.message.edit_text("❌ Заявка отклонена.")
    await call.answer()

@router.message(Command("admins"))
async def list_admins(message: Message):
    if message.from_user.id != FULL_ADMIN_ID:
        return
    admins = await db.get_all_admins()
    if not admins:
        await message.answer("Список админов пуст.")
        return
    text = "👑 **Список администраторов:**\n\n"
    for a in admins:
        text += f"ID: `{a[0]}` | @{a[1]} | Роль: {a[2]}\n"
    text += "\nЧтобы снять права, напишите: `/demote ID`"
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("demote"))
async def demote_admin(message: Message):
    if message.from_user.id != FULL_ADMIN_ID:
        return
    try:
        target_id = int(message.text.split()[1])
        await db.set_role(target_id, "user")
        await message.answer(f"✅ Пользователь {target_id} лишен прав админа.")
    except:
        await message.answer("Использование: /demote 12345678")

@router.message(Command("block"))
async def block_user(message: Message, state: FSMContext):
    if message.from_user.id != FULL_ADMIN_ID:
        return
    await state.set_state(AdminForm.waiting_block)
    await message.answer("Введите @username пользователя, которого нужно заблокировать (без @ не сработает):")

@router.message(AdminForm.waiting_block)
async def process_block(message: Message, state: FSMContext):
    await state.clear()
    username = message.text.replace("@", "")
    await db.ban_user_by_username(username)
    await message.answer(f"✅ Пользователь @{username} заблокирован (если он есть в базе).")
