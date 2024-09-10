from config import Config, temp
from helper.database import db
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    ChatPrivileges,
)
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid,
)
import os
import sys
import time
import asyncio
import logging
import datetime

from plugins.session import generate_session
from .start import client, start_clone_bot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# approve all pending request is only for user for more info https://docs.pyrogram.org/api/methods/approve_all_chat_join_requests#pyrogram.Client.approve_all_chat_join_requests:~:text=Approve%20all%20pending%20join%20requests%20in%20a%20chat. only Usable by User not bot


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply("**Aᴄᴄᴇꜱꜱɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟꜱ.....**")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(
        text=f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`"
    )


# Restart to cancell all process
@Client.on_message(
    filters.private & filters.command("restart") & filters.user(Config.ADMIN)
)
async def restart_bot(b, m):
    await m.reply_text("🔄__Rᴇꜱᴛᴀʀᴛɪɴɢ.....__")
    os.execl(sys.executable, sys.executable, *sys.argv)


# ⚠️ Broadcasting only those people who has started your bot


@Client.on_message(
    filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply
)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(
        Config.LOG_CHANNEL,
        f"{m.from_user.mention} or {m.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Bʀᴏᴀᴅᴄᴀꜱᴛ......",
    )
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user["id"], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user["id"])
        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}"
            )
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}"
    )


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500


@Client.on_message(
    filters.private & filters.command("add_userbot") & filters.user(Config.ADMIN)
)
async def add_userbot(bot: Client, message: Message):
    try:
        bot_exist = await db.is_user_bot_exist(message.from_user.id)

        if bot_exist:
            return await message.reply_text(
                "**⚠️ User Bot Already Exists**",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("User Bot", callback_data="userbot")]]
                ),
            )
    except:
        pass

    user_id = int(message.from_user.id)

    text = "<b>⚠️ DISCLAIMER ⚠️</b>\n\n<code>\nPlease add your pyrogram session with your own risk. Their is a chance to ban your account. My developer is not responsible if your account may get banned.</code>\n\n /cancel ** to cancel the process **"
    await bot.send_message(user_id, text=text)
    session = await generate_session(bot, message)
    try:
        user_account = await start_clone_bot(client(session))
    except Exception as e:
        await message.reply_text(f"<b>USER BOT ERROR:</b> `{e}`")
        print(
            "Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )
        return

    user = user_account.me

    details = {
        "id": user.id,
        "is_bot": False,
        "user_id": user_id,
        "name": user.first_name,
        "session": session,
        "username": user.username,
    }
    await db.add_user_bot(details)

    await message.reply_text(
        "**User Bot Added Successfully ✅**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❮ Back", callback_data="userbot")]]
        ),
    )


@Client.on_callback_query(filters.regex("^acceptallchat_"))
async def handle_accept_pending_request(bot: Client, update: CallbackQuery):
    # await update.message.delete()
    chat_id = int(update.data.split("_")[1])
    user_id = update.from_user.id

    if user_id in temp.PENDING_REQUESTS:
        return await update.message.edit(
            "**Please Wait...**\n\n**Until Previous Work Is Completed.**"
        )

    temp.PENDING_REQUESTS.append(user_id)

    try:
        bot_exist = await db.is_user_bot_exist(update.from_user.id)
    except:
        return await update.message.edit(
            "**⚠️ You have not added user bot yet !\n\nUse /add_userbot to add it **"
        )

    if not bot_exist:
        return await update.message.edit(
            "**⚠️ You have not added user bot yet !\n\nUse /add_userbot to add it **"
        )

    user_bot = await db.get_user_bot(update.from_user.id)

    user = await start_clone_bot(client(user_bot["session"]))
    try:
        link = await bot.export_chat_invite_link(chat_id=chat_id)
        await user.join_chat(link)
        await bot.promote_chat_member(
            chat_id=chat_id,
            user_id=user_bot["id"],
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_post_messages=True,
                can_change_info=True,
                can_delete_messages=True,
                can_edit_messages=True,
                can_invite_users=True,
            ),
        )
    except:
        pass

    ms = await update.message.edit("**Please Wait Accepting the peding requests. ♻️**")

    async for request in user.get_chat_join_requests(chat_id=chat_id):
        try:
            await user.approve_chat_join_request(
                chat_id=chat_id, user_id=request.user.id
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await user.approve_chat_join_request(
                chat_id=chat_id, user_id=request.user.id
            )
        except Exception as e:
            try:
                await user.approve_chat_join_request(
                    chat_id=chat_id, user_id=request.user.id
                )
            except:
                pass

    await ms.delete()
    try:
        chnlInfo = await bot.get_chat(int(chat_id))
    except:
        pass
    await update.message.reply_text(
        f"**Task Completed** ✓ **Approved ✅ All Pending Join Requests from `{chnlInfo.title if chnlInfo else chat_id}`**"
    )

    temp.PENDING_REQUESTS.remove(user_id)
    await user.stop()


@Client.on_callback_query(filters.regex("^declineallchat_"))
async def handle_delcine_pending_request(bot: Client, update: CallbackQuery):

    user_id = update.from_user.id

    if user_id in temp.PENDING_REQUESTS:
        return await update.message.edit(
            "**Please Wait...**\n\n**Until Previous Work Is Completed.**"
        )

    temp.PENDING_REQUESTS.append(user_id)

    try:
        bot_exist = await db.is_user_bot_exist(update.from_user.id)
    except:
        return await update.message.edit(
            "**⚠️ You have not added user bot yet !\n\nUse /add_userbot to add it **"
        )

    if not bot_exist:
        return await update.message.edit(
            "**⚠️ You have not added user bot yet !\n\nUse /add_userbot to add it **"
        )

    ms = await update.message.edit(
        "**Please Wait Declining all the peding requests. ♻️**"
    )

    chat_id = update.data.split("_")[1]
    user_bot = await db.get_user_bot(update.from_user.id)
    user = await start_clone_bot(client(user_bot["session"]))
    try:
        link = await bot.export_chat_invite_link(chat_id=chat_id)
        await user.join_chat(link)
        await bot.promote_chat_member(
            chat_id=chat_id,
            user_id=user_bot["id"],
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_post_messages=True,
                can_change_info=True,
                can_delete_messages=True,
                can_edit_messages=True,
                can_invite_users=True,
            ),
        )
    except:
        pass

    async for request in user.get_chat_join_requests(chat_id=chat_id):
        try:
            await user.decline_chat_join_request(
                chat_id=chat_id, user_id=request.user.id
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await user.decline_chat_join_request(
                chat_id=chat_id, user_id=request.user.id
            )
        except:
            pass

    await ms.delete()
    try:
        chnlInfo = await bot.get_chat(int(chat_id))
    except:
        pass
    await update.message.reply_text(
        f"**Task Completed** ✓ **Declined ❌ All The Pending Join Requests from `{chnlInfo.title if chnlInfo else chat_id}`**"
    )

    temp.PENDING_REQUESTS.remove(user_id)
    await user.stop()
