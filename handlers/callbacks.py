from aiogram import Router, F
from aiogram.types import CallbackQuery
import database as db
from keyboards import idea_keyboard

router = Router()

@router.callback_query(F.data.startswith("like:") | F.data.startswith("dislike:"))
async def vote(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    if user and user[2] == 1:
        await call.answer("Вы заблокированы.", show_alert=True)
        return
    
    action, msg_id = call.data.split(":")
    msg_id = int(msg_id)
    vote_type = "like" if action == "like" else "dislike"
    
    existing = await db.get_vote(call.from_user.id, msg_id)
    
    if existing:
        if existing == vote_type:
            await call.answer("Ты уже так голосовал! Можно поставить только один лайк или дизлайк.")
            return
        await db.switch_vote(call.from_user.id, msg_id, vote_type)
    else:
        await db.add_vote(call.from_user.id, msg_id, vote_type)
    
    likes, dislikes = await db.get_counts(msg_id)
    
    chat_info = await call.bot.get_chat(call.message.chat.id)
    group_username = chat_info.username if chat_info.username else "c"
    
    await call.bot.edit_message_reply_markup(
        call.message.chat.id, msg_id,
        reply_markup=idea_keyboard(msg_id, likes, dislikes, group_username)
    )
    await call.answer("Голос учтён!")
