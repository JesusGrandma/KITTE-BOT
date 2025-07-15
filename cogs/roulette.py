import discord
from discord.ext import commands
import random
import sqlite3

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roulette', help="Play a game of Russian Roulette. Usage: /roulette")
    async def roulette(self, ctx, bet_amount: int = None, bet_color: str = None):
        colors = ['red', 'black', 'green']
        syntax = "`!roulette <amount> <color>` — Example: `!roulette 100 red`"

        # Check for missing arguments
        if bet_amount is None or bet_color is None:
            return await ctx.send(f"Incorrect usage. Correct syntax: {syntax}")

        bet_color = bet_color.lower()

        if bet_color not in colors:
            return await ctx.send(f"Invalid color. Choose `red`, `black`, or `green`.\nCorrect syntax: {syntax}")

        if bet_amount <= 0:
            return await ctx.send(f"Bet amount must be greater than zero.\nCorrect syntax: {syntax}")

        # Connect to SQLite database
        conn = sqlite3.connect("currency.db")
        cursor = conn.cursor()

        # Get or create user balance
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
        row = cursor.fetchone()

        if not row:
            balance = 1000
            cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (ctx.author.id, balance))
            conn.commit()
        else:
            balance = row[0]

        # Check if the user has enough coins
        if bet_amount > balance:
            conn.close()
            return await ctx.send("You don't have enough coins for that bet.")

        # Deduct the bet
        balance -= bet_amount
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance, ctx.author.id))
        conn.commit()

        # Spin the wheel
        result_number = random.randint(0, 36)
        result_color = 'green' if result_number == 0 else random.choice(['red', 'black'])

        win = result_color == bet_color
        payout = 0

        if win:
            payout = bet_amount * (14 if bet_color == 'green' else 2)
            balance += payout
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance, ctx.author.id))
            conn.commit()

        conn.close()

        # Build the embed
        embed = discord.Embed(
            title="Roulette Result",
            color=discord.Color.green() if result_color == 'green'
            else discord.Color.red() if result_color == 'red'
            else discord.Color.dark_gray()
        )

        embed.add_field(name="Player", value=ctx.author.mention, inline=True)
        embed.add_field(name="Your Bet", value=f"{bet_amount} on `{bet_color}`", inline=True)
        embed.add_field(name="Outcome", value=f"{result_color.upper()} {result_number}", inline=False)

        if win:
            embed.add_field(name="Result", value=f"You won {payout} coins.", inline=False)
        else:
            embed.add_field(name="Result", value="You lost your bet.", inline=False)

        embed.add_field(name="New Balance", value=f"{balance} coins", inline=False)
        embed.set_footer(text="Use /balance to check your total.")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Roulette(bot))
