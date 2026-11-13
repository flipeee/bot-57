from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def idea_keyboard(msg_id, likes, dislikes, group_username):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"👍 {likes}", callback_data=f"like:{msg_id}"),
        InlineKeyboardButton(text=f"👎 {dislikes}", callback_data=f"dislike:{msg_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Написать комментарий", url=f"https://t.me/{group_username}")
    )
    return builder.as_markup()

def confirm_admin_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принять", callback_data=f"approve:{user_id}")
    builder.button(text="❌ Отклонить", callback_data=f"reject:{user_id}")
    return builder.as_markup()

def banned_keyboard(admin_username):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать администрации", url=f"https://t.me/{admin_username}")]
    ])