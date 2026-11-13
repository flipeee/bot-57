from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from keyboards import idea_keyboard, banned_keyboard
from config import GROUP_ID, ADMIN_USERNAME

router = Router()

class IdeaForm(StatesGroup):
    waiting_text = State()

@router.message(CommandStart())
async def start(message: Message):
    if message.chat.type != "private":
        return
    await db.create_user(message.from_user.id, message.from_user.username or "")
    user = await db.get_user(message.from_user.id)
    if user and user[2] == 1:
        await message.answer("Вы заблокированы.", reply_markup=banned_keyboard(ADMIN_USERNAME))
        return
    
    await message.answer(
        "Привет! Нажми /idea чтобы предложить идею.\n"
        "Идеи анонимные — никто не узнает, что это ты."
    )

@router.message(F.text == "/idea")
async def idea_start(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return
    user = await db.get_user(message.from_user.id)
    if user and user[2] == 1:
        await message.answer("Вы заблокированы.", reply_markup=banned_keyboard(ADMIN_USERNAME))
        return
    await state.set_state(IdeaForm.waiting_text)
    await message.answer("Напиши свою идею одним сообщением:")

@router.message(IdeaForm.waiting_text)
async def idea_save(message: Message, state: FSMContext):
    await state.clear()
    text = message.text
    
    sent = await message.bot.send_message(
        GROUP_ID,
        f"💡 Идея:\n\n{text}"
    )
    
    await db.save_idea(sent.message_id, text)
    
    chat_info = await message.bot.get_chat(GROUP_ID)
    group_username = chat_info.username if chat_info.username else "c"
    
    await message.bot.edit_message_reply_markup(
        GROUP_ID, sent.message_id,
        reply_markup=idea_keyboard(sent.message_id, 0, 0, group_username)
    )
    
    await message.answer("✅ Идея опубликована анонимно!")