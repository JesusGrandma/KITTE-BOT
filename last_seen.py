import discord
from discord.ext import commands
from datetime import datetime
import aiosqlite
import asyncio

DB_FILE = "lastseen.db"

class LastSeen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.init_db())

    async def init_db(self):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS last_seen (
                    user_id INTEGER PRIMARY KEY,
                    timestamp TEXT
                )
            ''')
            await db.commit()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Only act if status changed to offline
        if before.status != discord.Status.offline and after.status == discord.Status.offline:
            user_id = after.id
            now = datetime.utcnow().isoformat()
            async with aiosqlite.connect(DB_FILE) as db:
                await db.execute(
                    "REPLACE INTO last_seen (user_id, timestamp) VALUES (?, ?)",
                    (user_id, now)
                )
                await db.commit()

    @commands.command()
    async def lastseen(self, ctx, member: discord.Member):
        async with aiosqlite.connect(DB_FILE) as db:
            async with db.execute(
                "SELECT timestamp FROM last_seen WHERE user_id = ?", (member.id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    last_seen_time = datetime.fromisoformat(row[0])
                    delta = datetime.utcnow() - last_seen_time
                    days = delta.days
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes = remainder // 60
                    await ctx.send(
                        f"{member.display_name} was last seen {days}d {hours}h {minutes}m ago."
                    )
                else:
                    await ctx.send(f"I haven’t seen {member.display_name} go offline yet.")

def setup(bot):
    bot.add_cog(LastSeen(bot))
