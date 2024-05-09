from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import db
from helper.utils import OnWelcBtn, OnLeavBtn, OnAutoacceptBtn, OffAutoacceptBtn, OffLeavBtn, OffWelcBtn
from config import TxT


@Client.on_callback_query()
async def handle_CallbackQuery(bot: Client, query: CallbackQuery):

    data = query.data

    if data.startswith('autoapprove_'):
        id = data.split('_')[1]

        text = "**Here are the channels where I'm admin and you can toggle the auto accept functionality.**"

        db_channels = await db.get_admin_channels()
        btn = []
        try:
            for key, value in db_channels.items():
                channel = await bot.get_chat(int(key))

                if key == id:
                    if value:
                        await db.update_admin_channel(id, False)
                        btn.append([InlineKeyboardButton(
                            f'{channel.title} ❌', callback_data=f'autoapprove_{key}')])
                    else:
                        await db.update_admin_channel(id, True)
                        btn.append([InlineKeyboardButton(
                            f'{channel.title} ✅', callback_data=f'autoapprove_{key}')])

                else:
                    if value:
                        btn.append([InlineKeyboardButton(
                            f'{channel.title} ✅', callback_data=f'autoapprove_{key}')])
                    else:
                        btn.append([InlineKeyboardButton(
                            f'{channel.title} ❌', callback_data=f'autoapprove_{key}')])

            await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            return query.message.edit("**I'm Not admin in any channel or group yet**\n\nOR Maybe you make me admin in any channels or group when i was offline so make sure to remove me and make me admin again !")

    elif data.startswith('welc'):
        text = "Click the button from below to toggle Welcome & Leaving Message also Auto Accept."
        boolean = data.split('-')[1]

        if boolean == 'on':
            await db.set_bool_welc(query.from_user.id, False)
            if await db.get_bool_leav(query.from_user.id):
                if await db.get_bool_auto_accept(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

            else:
                if await db.get_bool_auto_accept(query.from_user.id):

                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OffLeavBtn], [OnAutoacceptBtn]]))
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OffLeavBtn], [OffAutoacceptBtn]]))

        elif boolean == 'off':
            await db.set_bool_welc(query.from_user.id, True)
            if await db.get_bool_leav(query.from_user.id):
                if await db.get_bool_auto_accept(query.from_user.id):

                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

            else:
                if await db.get_bool_auto_accept(query.from_user.id):

                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffLeavBtn], [OnAutoacceptBtn]]))

                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffLeavBtn], [OffAutoacceptBtn]]))

    elif data.startswith('leav'):
        text = "Click the button from below to toggle Welcome & Leaving Message also Auto Accept."
        boolean = data.split('-')[1]

        if boolean == 'on':
            await db.set_bool_leav(query.from_user.id, False)
            if await db.get_bool_welc(query.from_user.id):
                if await db.get_bool_auto_accept(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffLeavBtn], [OnAutoacceptBtn]]))

                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffLeavBtn], [OffAutoacceptBtn]]))

            else:
                if await db.get_bool_auto_accept(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OffLeavBtn], [OnAutoacceptBtn]]))
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OffLeavBtn], [OffAutoacceptBtn]]))

        elif boolean == 'off':
            await db.set_bool_leav(query.from_user.id, True)
            if await db.get_bool_welc(query.from_user.id):
                if await db.get_bool_auto_accept(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

            else:
                if await db.get_bool_auto_accept(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OnLeavBtn], [OnAutoacceptBtn], [OffAutoacceptBtn]]))

    elif data.startswith('autoaccept'):
        text = "Click the button from below to toggle Welcome & Leaving Message also Auto Accept."
        boolean = data.split('-')[1]

        if boolean == 'on':
            await db.set_bool_auto_accept(query.from_user.id, False)
            if await db.get_bool_welc(query.from_user.id) and await db.get_bool_leav(query.from_user.id):
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

            elif await db.get_bool_welc(query.from_user.id):
                if await db.get_bool_leav(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffLeavBtn], [OffAutoacceptBtn]]))

            elif await db.get_bool_leav(query.from_user.id):
                if await db.get_bool_welc(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OnLeavBtn], [OffAutoacceptBtn]]))

            else:
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OffLeavBtn], [OffAutoacceptBtn]]))
        else:
            await db.set_bool_auto_accept(query.from_user.id, True)
            if await db.get_bool_welc(query.from_user.id) and await db.get_bool_leav(query.from_user.id):
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))

            elif await db.get_bool_welc(query.from_user.id):
                if await db.get_bool_leav(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))

                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffLeavBtn], [OnAutoacceptBtn]]))

            elif await db.get_bool_leav(query.from_user.id):
                if await db.get_bool_welc(query.from_user.id):
                    return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))

                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OnLeavBtn], [OnAutoacceptBtn]]))

            else:
                return await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[OffWelcBtn, OffLeavBtn], [OnAutoacceptBtn]]))

    elif data == 'userbot':
        userBot = await db.get_user_bot(query.from_user.id)

        text = f"Name: {userBot['name']}\nUserName: @{userBot['username']}\n UserId: {userBot['user_id']}"

        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('❌ Remove ❌', callback_data='rmuserbot')], [InlineKeyboardButton('✘ Close ✘', callback_data='close')]]))

    elif data == 'rmuserbot':
        
        await db.remove_user(query.from_user.id)
        await query.message.edit(text='**User Bot Removed Successfully ✅**', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('✘ Close ✘', callback_data='close')]]))
        
    elif data == 'help':
        await query.message.edit(TxT.HELP_MSG, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('✘ Close ✘', callback_data='close')]]))

    elif data == 'close':
        await query.message.delete()
        await query.message.continue_propagation()
