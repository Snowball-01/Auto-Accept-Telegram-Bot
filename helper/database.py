import datetime
import sys
import motor.motor_asyncio
from config import Config
from helper.utils import send_log


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.bot = self.db.bots
        self.config = self.db.config

    def new_user(self, id):
        return dict(
            id=int(id),
            join_date=datetime.date.today().isoformat(),
        )

    def add_config(self, id):
        return dict(
            id=int(id),
            welc_file=None,
            leav_file=None,
            welcome=None,
            leave=None,
            bool_auto_accept=False,
            bool_welc=None,
            bool_leav=None,
            channel=[],
            admin_channels={},
        )

    def approved_user(self, id):
        return dict(id=int(id))

    async def add_user_bot(self, bot_datas):
        if not await self.is_user_bot_exist(bot_datas["user_id"]):
            await self.bot.insert_one(bot_datas)

    async def get_user_bot(self, user_id: int):
        user = await self.bot.find_one({"user_id": user_id, "is_bot": False})
        return user if user else None

    async def is_user_bot_exist(self, user_id):
        user = await self.bot.find_one({"user_id": user_id, "is_bot": False})
        return bool(user)

    async def remove_user(self, user_id):
        await self.bot.delete_many({"user_id": int(user_id), "is_bot": False})

    async def set_welcome(self, user_id, welcome):
        await self.config.update_one({"id": int(user_id)}, {"$set": {"welcome": welcome}})

    async def get_welcome(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("welcome", None)

    async def set_welc_file(self, user_id, welc_file):
        await self.config.update_one(
            {"id": int(user_id)}, {"$set": {"welc_file": welc_file}}
        )

    async def get_welc_file(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("welc_file", None)

    async def set_leav_file(self, user_id, leav_file):
        await self.config.update_one(
            {"id": int(user_id)}, {"$set": {"leav_file": leav_file}}
        )

    async def get_leav_file(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("leav_file", None)

    async def set_leave(self, user_id, leave):
        await self.config.update_one({"id": int(user_id)}, {"$set": {"leave": leave}})

    async def get_leave(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("leave", None)

    async def set_bool_auto_accept(self, user_id, bool_auto_accept):
        await self.config.update_one(
            {"id": int(user_id)}, {"$set": {"bool_auto_accept": bool_auto_accept}}
        )

    async def get_bool_auto_accept(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("bool_auto_accept", None)

    async def set_bool_welc(self, user_id, bool_welc):
        await self.config.update_one(
            {"id": int(user_id)}, {"$set": {"bool_welc": bool_welc}}
        )

    async def get_bool_welc(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("bool_welc", None)

    async def set_bool_leav(self, user_id, boo_leav):
        await self.config.update_one(
            {"id": int(user_id)}, {"$set": {"bool_leav": boo_leav}}
        )

    async def get_bool_leav(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("bool_leav", None)

    async def set_admin_channel(self, channel_id, condition):
        user = await self.config.find_one({"id": int(Config.ADMIN)})
        if user:
            channels = user.get("admin_channels", {})
            if channel_id not in channels:
                channels.update({f"{channel_id}": condition})
                await self.config.update_one(
                    {"id": int(Config.ADMIN)}, {"$set": {"admin_channels": channels}}
                )

    async def update_admin_channel(self, id, condition):
        user = await self.config.find_one({"id": int(Config.ADMIN)})
        if user:
            channels = user.get("admin_channels", {})
            if id in channels:
                channels.update({f"{id}": condition})
                await self.config.update_one(
                    {"id": int(Config.ADMIN)}, {"$set": {"admin_channels": channels}}
                )

    async def get_admin_channels(self):
        user = await self.config.find_one({"id": int(Config.ADMIN)})
        return user.get("admin_channels", {})

    async def remove_admin_channel(self, channel_id):
        user = await self.config.find_one({"id": int(Config.ADMIN)})
        if user:
            channels = user.get("admin_channels", {})
            if channel_id in channels:
                channels.pop(channel_id)
                await self.config.update_one(
                    {"id": int(Config.ADMIN)}, {"$set": {"admin_channels": channels}}
                )

    async def set_channel(self, user_id, channel_id):
        user = await self.config.find_one({"id": int(user_id)})
        if user:
            channels = user.get("channel", [])
            if channel_id not in channels:
                channels.append(channel_id)
                await self.config.update_one(
                    {"id": int(user_id)}, {"$set": {"channel": channels}}
                )

    async def get_channel(self, id):
        user = await self.config.find_one({"id": int(id)})
        return user.get("channel", [])

    async def remove_channel(self, user_id, channel_id):
        user = await self.config.find_one({"id": int(user_id)})
        if user:
            channels = user.get("channel", [])
            if channel_id in channels:
                channels.remove(channel_id)
                await self.config.update_one(
                    {"id": int(user_id)}, {"$set": {"channel": channels}}
                )

    async def add_user(self, b, m):
    
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            config = self.add_config(u.id)
            await self.config.insert_one(config)
            await self.col.insert_one(user)
            await send_log(b, u)
        
    async def add_appro_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.approved_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})


db = Database(Config.DB_URL, Config.DB_NAME)
