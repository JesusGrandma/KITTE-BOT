import discord
from discord.ext import commands
import sqlite3

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("currency.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 1000
            )
        """)
        self.conn.commit()

    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
            return 1000

    def update_balance(self, user_id, amount):
        balance = self.get_balance(user_id) + amount
        self.cursor.execute("REPLACE INTO users (user_id, balance) VALUES (?, ?)", (user_id, balance))
        self.conn.commit()
        return balance

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        bal = self.get_balance(member.id)
        await ctx.send(f"💰 {member.display_name} has **{bal}** coins.")

    @commands.command()
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("Amount must be positive.")

        sender_balance = self.get_balance(ctx.author.id)
        if sender_balance < amount:
            return await ctx.send("You don’t have enough coins.")

        self.update_balance(ctx.author.id, -amount)
        self.update_balance(member.id, amount)
        await ctx.send(f"✅ Gave **{amount}** coins to {member.display_name}.")

async def setup(bot):
    await bot.add_cog(Currency(bot))
