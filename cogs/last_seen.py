import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

class LastSeen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("lastseen.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS last_seen (
                user_id INTEGER PRIMARY KEY,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def update_online_time(self, user_id):
        timestamp = datetime.utcnow().isoformat()
        self.cursor.execute(
            "REPLACE INTO last_seen (user_id, timestamp) VALUES (?, ?)",
            (user_id, timestamp)
        )
        self.conn.commit()

    def get_online_time(self, user_id):
        self.cursor.execute(
            "SELECT timestamp FROM last_seen WHERE user_id = ?",
            (user_id,)
        )
        row = self.cursor.fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.status != after.status and after.status == discord.Status.online:
            print(f"Updating last seen for {after.display_name} ({after.id})")  # For debugging
            self.update_online_time(after.id)

    @commands.command(name="lastseen", help="Show when a user was last online. Usage: /lastseen [user]")
    async def lastseen(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        seen_time = self.get_online_time(member.id)
        if seen_time:
            delta = datetime.utcnow() - seen_time
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes = remainder // 60
            await ctx.send(
                f"📡 {member.display_name} was last **online** {days}d {hours}h {minutes}m ago."
            )
        else:
            await ctx.send(f"❓ I haven’t seen {member.display_name} online yet.")

async def setup(bot):
    await bot.add_cog(LastSeen(bot))
