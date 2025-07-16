import discord
from discord.ext import commands
import asyncio
import random

class ConnectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # channel_id: game

    @commands.command(name="connect4", help="Play Connect Four with another user or the bot. Usage: /connect4 [@user]")
    async def connect4(self, ctx, opponent: discord.Member = None):
        if ctx.channel.id in self.active_games:
            await ctx.send("A Connect Four game is already in progress in this channel.")
            return
        if opponent is None or opponent == self.bot.user:
            opponent = self.bot.user
            is_vs_bot = True
        else:
            is_vs_bot = False
        if opponent.bot and opponent != self.bot.user:
            await ctx.send("You must challenge a human user or the bot!")
            return
        if opponent == ctx.author:
            await ctx.send("You must challenge another user or the bot!")
            return
        board = [[":white_circle:" for _ in range(7)] for _ in range(6)]
        players = [ctx.author, opponent]
        symbols = [":red_circle:", ":yellow_circle:"]
        turn = 0
        game_over = False
        def render_board():
            rows = ["".join(row) for row in board]
            return "\n".join(rows) + "\n1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
        async def drop_piece(col, symbol):
            for row in reversed(board):
                if row[col] == ":white_circle:":
                    row[col] = symbol
                    return True
            return False
        def check_win(symbol):
            for r in range(6):
                for c in range(7):
                    if c <= 3 and all(board[r][c+i] == symbol for i in range(4)):
                        return True
                    if r <= 2 and all(board[r+i][c] == symbol for i in range(4)):
                        return True
                    if r <= 2 and c <= 3 and all(board[r+i][c+i] == symbol for i in range(4)):
                        return True
                    if r <= 2 and c >= 3 and all(board[r+i][c-i] == symbol for i in range(4)):
                        return True
            return False
        self.active_games[ctx.channel.id] = True
        await ctx.send(f"Connect Four: {players[0].mention} (🔴) vs {players[1].mention if players[1] != self.bot.user else 'Bot (🟡)'}")
        await ctx.send(render_board())
        while not game_over:
            current = players[turn % 2]
            symbol = symbols[turn % 2]
            if is_vs_bot and current == self.bot.user:
                # Bot's turn: pick a random valid column
                await asyncio.sleep(1)
                valid_cols = [i for i in range(7) if board[0][i] == ":white_circle:"]
                if not valid_cols:
                    await ctx.send("It's a tie!")
                    break
                col = random.choice(valid_cols)
                await drop_piece(col, symbol)
                await ctx.send(f"Bot drops in column {col+1}.")
                await ctx.send(render_board())
                if check_win(symbol):
                    await ctx.send(f"Bot wins! Game over.")
                    game_over = True
                    break
            else:
                await ctx.send(f"{current.mention}, choose a column (1-7) to drop your piece.")
                def check(m):
                    return m.author == current and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 7
                try:
                    msg = await self.bot.wait_for("message", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send(f"{current.mention} took too long! Game over.")
                    break
                col = int(msg.content) - 1
                if not await drop_piece(col, symbol):
                    await ctx.send("That column is full! Try another.")
                    continue
                await ctx.send(render_board())
                if check_win(symbol):
                    await ctx.send(f"{current.mention} wins! Game over.")
                    game_over = True
                    break
            if all(cell != ":white_circle:" for row in board for cell in row):
                await ctx.send("It's a tie!")
                game_over = True
                break
            turn += 1
        del self.active_games[ctx.channel.id]

def setup(bot):
    bot.add_cog(ConnectFour(bot)) 